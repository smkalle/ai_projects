"""
FarmConnect Logistics Agent - LangGraph Implementation
Handles delivery partner integration, route optimization, and real-time tracking
"""

from typing import TypedDict, Annotated, Sequence, Literal, Optional, Dict, Any, List
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain.schema import BaseMessage, HumanMessage, AIMessage, SystemMessage
import operator
import asyncio
import json
from datetime import datetime, timedelta
import logging
import os
from dotenv import load_dotenv
import aiohttp
import numpy as np
from dataclasses import dataclass

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class DeliveryPoint:
    """Delivery point with GPS coordinates"""
    id: str
    address: str
    latitude: float
    longitude: float
    weight: float
    priority: int = 1

class LogisticsState(TypedDict):
    """State for logistics agent workflow"""
    messages: Annotated[Sequence[BaseMessage], operator.add]
    task_type: Literal["route_optimize", "partner_select", "track_shipment", "cost_estimate"]
    delivery_points: List[Dict[str, Any]]
    vehicle_capacity: float
    budget_limit: float
    time_constraints: Dict[str, Any]
    selected_partner: Optional[str]
    optimized_route: List[Dict[str, Any]]
    cost_breakdown: Dict[str, Any]
    tracking_info: Dict[str, Any]
    recommendations: List[str]
    execution_time: float

class LogisticsAgent:
    """
    LangGraph-based Logistics Agent for FarmConnect
    Handles delivery optimization, partner selection, and tracking
    """
    
    def __init__(self):
        """Initialize the logistics agent with LangGraph workflow"""
        
        # Get API key from environment
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OpenAI API key not found in environment")
        
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0,
            api_key=api_key
        )
        
        # Delivery partner configurations
        self.delivery_partners = {
            "dunzo": {
                "name": "Dunzo",
                "max_weight": 20,
                "cost_per_km": 8,
                "base_cost": 30,
                "coverage_radius": 25,
                "api_endpoint": "https://api.dunzo.com/v1/orders",
                "supported_categories": ["food", "groceries", "fresh_produce"]
            },
            "shadowfax": {
                "name": "Shadowfax",
                "max_weight": 50,
                "cost_per_km": 6,
                "base_cost": 25,
                "coverage_radius": 50,
                "api_endpoint": "https://api.shadowfax.in/v2/orders",
                "supported_categories": ["food", "groceries", "fresh_produce", "packaged_goods"]
            },
            "porter": {
                "name": "Porter",
                "max_weight": 500,
                "cost_per_km": 12,
                "base_cost": 60,
                "coverage_radius": 100,
                "api_endpoint": "https://api.porter.in/v1/shipments",
                "supported_categories": ["bulk", "heavy_goods", "long_distance"]
            }
        }
        
        # Create workflow
        self.workflow = self._create_workflow()
        
        logger.info("LogisticsAgent initialized with delivery partners")
    
    def _create_workflow(self) -> StateGraph:
        """Create the LangGraph workflow for logistics operations"""
        
        # Initialize the graph
        workflow = StateGraph(LogisticsState)
        
        # Add nodes for each logistics operation
        workflow.add_node("route_optimizer", self.route_optimizer_node)
        workflow.add_node("partner_selector", self.partner_selector_node)
        workflow.add_node("cost_calculator", self.cost_calculator_node)
        workflow.add_node("tracking_manager", self.tracking_manager_node)
        workflow.add_node("coordinator", self.coordinator_node)
        
        # Set entry point
        workflow.set_entry_point("coordinator")
        
        # Add conditional routing from coordinator
        workflow.add_conditional_edges(
            "coordinator",
            self.route_logistics_task,
            {
                "route_optimize": "route_optimizer",
                "partner_select": "partner_selector",
                "cost_estimate": "cost_calculator",
                "track_shipment": "tracking_manager",
                "end": END
            }
        )
        
        # All specialized nodes return to coordinator for next task
        for node in ["route_optimizer", "partner_selector", "cost_calculator", "tracking_manager"]:
            workflow.add_edge(node, "coordinator")
        
        return workflow.compile()
    
    async def coordinator_node(self, state: LogisticsState) -> LogisticsState:
        """
        Coordinator node that orchestrates logistics operations
        """
        logger.info(f"Logistics Coordinator processing task: {state.get('task_type')}")
        
        system_prompt = """You are the logistics coordinator for FarmConnect, an AI-powered farm-to-fork marketplace.
        Your role is to optimize supply chain operations including:
        
        1. Route Optimization: Plan efficient delivery routes to minimize cost and time
        2. Partner Selection: Choose the best delivery partner based on requirements
        3. Cost Estimation: Calculate accurate delivery costs and optimize for budget
        4. Shipment Tracking: Monitor deliveries and provide real-time updates
        
        Based on the current task and state, determine what logistics operation is needed next.
        Consider factors like:
        - Delivery points and distances
        - Weight and size constraints
        - Budget limitations
        - Time requirements
        - Partner capabilities
        
        Response format: Return ONLY the next operation needed: 'route_optimize', 'partner_select', 'cost_estimate', 'track_shipment', or 'end'
        """
        
        # Prepare context for coordinator decision
        context = {
            "task_type": state.get("task_type"),
            "delivery_points_count": len(state.get("delivery_points", [])),
            "has_route": bool(state.get("optimized_route")),
            "has_partner": bool(state.get("selected_partner")),
            "has_cost": bool(state.get("cost_breakdown")),
            "has_tracking": bool(state.get("tracking_info"))
        }
        
        # Get coordinator decision
        messages = state.get("messages", [])
        response = await self.llm.ainvoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"Current context: {json.dumps(context, indent=2)}")
        ])
        
        # Update state with coordinator decision
        return {
            **state,
            "messages": messages + [response],
            "next_operation": self._parse_coordinator_response(response.content)
        }
    
    def route_logistics_task(self, state: LogisticsState) -> str:
        """Route to the appropriate logistics operation"""
        
        # Check if task is complete
        task_type = state.get("task_type")
        
        if task_type == "route_optimize" and not state.get("optimized_route"):
            return "route_optimize"
        elif task_type == "partner_select" and not state.get("selected_partner"):
            return "partner_select"
        elif task_type == "cost_estimate" and not state.get("cost_breakdown"):
            return "cost_estimate"
        elif task_type == "track_shipment" and not state.get("tracking_info"):
            return "track_shipment"
        else:
            return "end"
    
    async def route_optimizer_node(self, state: LogisticsState) -> LogisticsState:
        """
        Route optimization using AI-powered algorithms
        """
        logger.info("Route Optimizer activated")
        
        delivery_points = state.get("delivery_points", [])
        vehicle_capacity = state.get("vehicle_capacity", 100)
        
        if not delivery_points:
            return {**state, "optimized_route": [], "recommendations": ["No delivery points provided"]}
        
        # Convert to delivery point objects
        points = []
        for point in delivery_points:
            points.append(DeliveryPoint(
                id=point.get("id", "unknown"),
                address=point.get("address", ""),
                latitude=point.get("latitude", 0),
                longitude=point.get("longitude", 0),
                weight=point.get("weight", 5),
                priority=point.get("priority", 1)
            ))
        
        # Optimize route using distance matrix and capacity constraints
        optimized_route = await self._optimize_route(points, vehicle_capacity)
        
        # Generate recommendations
        recommendations = await self._generate_route_recommendations(optimized_route, points)
        
        message = AIMessage(content=f"Route optimized for {len(points)} delivery points. Total distance: {optimized_route.get('total_distance', 0)} km")
        
        return {
            **state,
            "optimized_route": optimized_route,
            "recommendations": recommendations,
            "messages": state.get("messages", []) + [message]
        }
    
    async def partner_selector_node(self, state: LogisticsState) -> LogisticsState:
        """
        Select optimal delivery partner based on requirements
        """
        logger.info("Partner Selector activated")
        
        delivery_points = state.get("delivery_points", [])
        budget_limit = state.get("budget_limit", float('inf'))
        time_constraints = state.get("time_constraints", {})
        
        # Calculate requirements
        total_weight = sum(point.get("weight", 5) for point in delivery_points)
        max_distance = self._calculate_max_distance(delivery_points)
        
        # Evaluate partners
        partner_scores = {}
        for partner_id, partner_config in self.delivery_partners.items():
            score = await self._evaluate_partner(
                partner_config, total_weight, max_distance, budget_limit, time_constraints
            )
            partner_scores[partner_id] = score
        
        # Select best partner
        selected_partner_id = max(partner_scores, key=partner_scores.get) if partner_scores else None
        selected_partner = self.delivery_partners.get(selected_partner_id, {})
        
        message = AIMessage(content=f"Selected delivery partner: {selected_partner.get('name', 'None')} with score: {partner_scores.get(selected_partner_id, 0):.2f}")
        
        return {
            **state,
            "selected_partner": selected_partner_id,
            "partner_scores": partner_scores,
            "messages": state.get("messages", []) + [message]
        }
    
    async def cost_calculator_node(self, state: LogisticsState) -> LogisticsState:
        """
        Calculate comprehensive delivery costs
        """
        logger.info("Cost Calculator activated")
        
        delivery_points = state.get("delivery_points", [])
        selected_partner = state.get("selected_partner")
        optimized_route = state.get("optimized_route", {})
        
        if not selected_partner:
            return {**state, "cost_breakdown": {"error": "No delivery partner selected"}}
        
        partner_config = self.delivery_partners.get(selected_partner, {})
        total_distance = optimized_route.get("total_distance", 0)
        
        # Calculate cost breakdown
        cost_breakdown = {
            "base_cost": partner_config.get("base_cost", 0),
            "distance_cost": total_distance * partner_config.get("cost_per_km", 0),
            "service_charges": len(delivery_points) * 5,  # ₹5 per delivery
            "total_cost": 0,
            "cost_per_delivery": 0,
            "partner": partner_config.get("name", "Unknown")
        }
        
        cost_breakdown["total_cost"] = (
            cost_breakdown["base_cost"] + 
            cost_breakdown["distance_cost"] + 
            cost_breakdown["service_charges"]
        )
        
        cost_breakdown["cost_per_delivery"] = (
            cost_breakdown["total_cost"] / len(delivery_points) if delivery_points else 0
        )
        
        message = AIMessage(content=f"Cost calculated: ₹{cost_breakdown['total_cost']:.2f} total, ₹{cost_breakdown['cost_per_delivery']:.2f} per delivery")
        
        return {
            **state,
            "cost_breakdown": cost_breakdown,
            "messages": state.get("messages", []) + [message]
        }
    
    async def tracking_manager_node(self, state: LogisticsState) -> LogisticsState:
        """
        Manage shipment tracking and real-time updates
        """
        logger.info("Tracking Manager activated")
        
        # Generate mock tracking information
        tracking_info = {
            "shipment_id": f"FC_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "status": "in_transit",
            "current_location": {
                "latitude": 18.5204,
                "longitude": 73.8567,
                "address": "Pune, Maharashtra"
            },
            "estimated_delivery": (datetime.now() + timedelta(hours=2)).isoformat(),
            "progress_percentage": 65,
            "delivery_partner": state.get("selected_partner", "unknown"),
            "tracking_url": f"https://track.farmconnect.in/shipment/{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "updates": [
                {
                    "timestamp": (datetime.now() - timedelta(minutes=30)).isoformat(),
                    "status": "picked_up",
                    "location": "Farm Location"
                },
                {
                    "timestamp": (datetime.now() - timedelta(minutes=15)).isoformat(),
                    "status": "in_transit",
                    "location": "Highway Checkpoint"
                }
            ]
        }
        
        message = AIMessage(content=f"Tracking initiated for shipment {tracking_info['shipment_id']}. Current status: {tracking_info['status']}")
        
        return {
            **state,
            "tracking_info": tracking_info,
            "messages": state.get("messages", []) + [message]
        }
    
    async def _optimize_route(self, points: List[DeliveryPoint], capacity: float) -> Dict[str, Any]:
        """
        Optimize delivery route using distance and capacity constraints
        """
        if len(points) <= 1:
            return {
                "route": [point.__dict__ for point in points],
                "total_distance": 0,
                "total_time": 0,
                "vehicle_utilization": sum(p.weight for p in points) / capacity * 100
            }
        
        # Simple greedy optimization (in production, use OR-Tools)
        start_point = points[0]
        remaining_points = points[1:]
        optimized_order = [start_point]
        current_weight = start_point.weight
        
        while remaining_points and current_weight <= capacity:
            # Find nearest point that fits capacity
            nearest = min(remaining_points, key=lambda p: self._calculate_distance(
                optimized_order[-1], p
            ))
            
            if current_weight + nearest.weight <= capacity:
                optimized_order.append(nearest)
                current_weight += nearest.weight
                remaining_points.remove(nearest)
            else:
                break
        
        # Calculate total distance
        total_distance = 0
        for i in range(len(optimized_order) - 1):
            total_distance += self._calculate_distance(optimized_order[i], optimized_order[i + 1])
        
        return {
            "route": [point.__dict__ for point in optimized_order],
            "total_distance": round(total_distance, 2),
            "total_time": round(total_distance / 30 * 60, 0),  # Assuming 30 km/h average
            "vehicle_utilization": round(current_weight / capacity * 100, 1),
            "undelivered": [point.__dict__ for point in remaining_points]
        }
    
    def _calculate_distance(self, point1: DeliveryPoint, point2: DeliveryPoint) -> float:
        """Calculate distance between two points using Haversine formula"""
        R = 6371  # Earth radius in km
        
        lat1, lon1 = np.radians([point1.latitude, point1.longitude])
        lat2, lon2 = np.radians([point2.latitude, point2.longitude])
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
        c = 2 * np.arcsin(np.sqrt(a))
        
        return R * c
    
    def _calculate_max_distance(self, delivery_points: List[Dict[str, Any]]) -> float:
        """Calculate maximum distance between any two delivery points"""
        if len(delivery_points) < 2:
            return 0
        
        max_dist = 0
        for i in range(len(delivery_points)):
            for j in range(i + 1, len(delivery_points)):
                p1 = DeliveryPoint(
                    id=str(i), address="", 
                    latitude=delivery_points[i].get("latitude", 0),
                    longitude=delivery_points[i].get("longitude", 0),
                    weight=0
                )
                p2 = DeliveryPoint(
                    id=str(j), address="",
                    latitude=delivery_points[j].get("latitude", 0),
                    longitude=delivery_points[j].get("longitude", 0),
                    weight=0
                )
                dist = self._calculate_distance(p1, p2)
                max_dist = max(max_dist, dist)
        
        return max_dist
    
    async def _evaluate_partner(self, partner_config: Dict[str, Any], total_weight: float, 
                               max_distance: float, budget: float, time_constraints: Dict[str, Any]) -> float:
        """
        Evaluate delivery partner suitability
        """
        score = 100
        
        # Weight capacity check
        if total_weight > partner_config.get("max_weight", 0):
            score -= 50
        
        # Distance coverage check
        if max_distance > partner_config.get("coverage_radius", 0):
            score -= 30
        
        # Budget check
        estimated_cost = (
            partner_config.get("base_cost", 0) + 
            max_distance * partner_config.get("cost_per_km", 0)
        )
        
        if estimated_cost > budget:
            score -= 40
        
        # Cost efficiency (lower cost per km is better)
        cost_per_km = partner_config.get("cost_per_km", 10)
        score += max(0, 20 - cost_per_km)  # Bonus for lower cost
        
        return max(0, score)
    
    async def _generate_route_recommendations(self, route: Dict[str, Any], 
                                            points: List[DeliveryPoint]) -> List[str]:
        """Generate AI-powered recommendations for route optimization"""
        
        recommendations = []
        
        # Vehicle utilization recommendations
        utilization = route.get("vehicle_utilization", 0)
        if utilization < 60:
            recommendations.append("Consider consolidating orders to improve vehicle utilization")
        elif utilization > 90:
            recommendations.append("Vehicle near capacity - consider splitting into multiple trips")
        
        # Distance optimization
        total_distance = route.get("total_distance", 0)
        if total_distance > 50:
            recommendations.append("Long route detected - consider regional distribution centers")
        
        # Time efficiency
        total_time = route.get("total_time", 0)
        if total_time > 180:  # 3 hours
            recommendations.append("Route exceeds 3 hours - consider overnight delivery option")
        
        # Undelivered items
        undelivered = route.get("undelivered", [])
        if undelivered:
            recommendations.append(f"{len(undelivered)} deliveries require separate trip due to capacity")
        
        return recommendations
    
    def _parse_coordinator_response(self, response: str) -> str:
        """Parse coordinator response to extract operation name"""
        response_lower = response.strip().lower()
        
        valid_operations = ["route_optimize", "partner_select", "cost_estimate", "track_shipment", "end"]
        
        for operation in valid_operations:
            if operation in response_lower:
                return operation
        
        return "end"
    
    async def execute(self, task_type: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute logistics workflow
        """
        logger.info(f"Executing logistics task: {task_type}")
        
        # Initialize state
        initial_state = {
            "messages": [HumanMessage(content=f"Execute logistics task: {task_type}")],
            "task_type": task_type,
            "delivery_points": task_data.get("delivery_points", []),
            "vehicle_capacity": task_data.get("vehicle_capacity", 100),
            "budget_limit": task_data.get("budget_limit", 10000),
            "time_constraints": task_data.get("time_constraints", {}),
            "selected_partner": None,
            "optimized_route": {},
            "cost_breakdown": {},
            "tracking_info": {},
            "recommendations": [],
            "execution_time": 0
        }
        
        try:
            start_time = datetime.now()
            
            # Execute workflow
            final_state = await self.workflow.ainvoke(initial_state)
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Prepare response
            result = {
                "success": True,
                "task_type": task_type,
                "execution_time": execution_time,
                "selected_partner": final_state.get("selected_partner"),
                "optimized_route": final_state.get("optimized_route"),
                "cost_breakdown": final_state.get("cost_breakdown"),
                "tracking_info": final_state.get("tracking_info"),
                "recommendations": final_state.get("recommendations", []),
                "messages": [msg.content for msg in final_state.get("messages", [])]
            }
            
            logger.info(f"Logistics task completed in {execution_time:.2f} seconds")
            return result
            
        except Exception as e:
            logger.error(f"Logistics workflow failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "task_type": task_type
            }

# Example usage
async def main():
    """Example usage of the logistics agent"""
    
    logistics_agent = LogisticsAgent()
    
    # Test route optimization
    route_task = {
        "delivery_points": [
            {
                "id": "D001",
                "address": "Pune City",
                "latitude": 18.5204,
                "longitude": 73.8567,
                "weight": 15,
                "priority": 1
            },
            {
                "id": "D002", 
                "address": "Mumbai Central",
                "latitude": 19.0760,
                "longitude": 72.8777,
                "weight": 20,
                "priority": 2
            },
            {
                "id": "D003",
                "address": "Nashik Road",
                "latitude": 19.9975,
                "longitude": 73.7898,
                "weight": 10,
                "priority": 1
            }
        ],
        "vehicle_capacity": 50,
        "budget_limit": 500
    }
    
    result = await logistics_agent.execute("route_optimize", route_task)
    print("Route Optimization Result:", json.dumps(result, indent=2))

if __name__ == "__main__":
    asyncio.run(main())