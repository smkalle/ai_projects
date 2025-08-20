"""
FarmConnect Inventory Management Agent - LangGraph Implementation
AI-powered demand forecasting, inventory optimization, and supply planning
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
import numpy as np
import pandas as pd
from dataclasses import dataclass

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class InventoryItem:
    """Inventory item with forecasting data"""
    product_id: str
    name: str
    current_stock: int
    reserved_stock: int
    available_stock: int
    reorder_point: int
    max_stock: int
    unit_cost: float
    shelf_life_days: int
    demand_pattern: str  # seasonal, regular, trending

@dataclass
class DemandForecast:
    """Demand forecast result"""
    product_id: str
    forecast_period: str  # daily, weekly, monthly
    predicted_demand: List[float]
    confidence_interval: List[tuple]
    seasonality_factor: float
    trend_factor: float
    recommendations: List[str]

class InventoryState(TypedDict):
    """State for inventory management workflow"""
    messages: Annotated[Sequence[BaseMessage], operator.add]
    task_type: Literal["demand_forecast", "stock_optimize", "reorder_plan", "expiry_alert"]
    inventory_data: List[Dict[str, Any]]
    historical_sales: List[Dict[str, Any]]
    market_conditions: Dict[str, Any]
    forecast_results: List[Dict[str, Any]]
    optimization_plan: Dict[str, Any]
    alerts: List[Dict[str, Any]]
    recommendations: List[str]
    kpis: Dict[str, Any]

class InventoryAgent:
    """
    LangGraph-based Inventory Management Agent for FarmConnect
    Handles demand forecasting, stock optimization, and supply planning
    """
    
    def __init__(self):
        """Initialize the inventory agent with ML models"""
        
        # Get API key from environment
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OpenAI API key not found in environment")
        
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0,
            api_key=api_key
        )
        
        # Inventory management parameters
        self.demand_patterns = {
            "vegetables": {
                "seasonality": 0.3,
                "volatility": 0.4,
                "perishability": "high",
                "lead_time_days": 1
            },
            "fruits": {
                "seasonality": 0.5,
                "volatility": 0.6,
                "perishability": "high",
                "lead_time_days": 2
            },
            "grains": {
                "seasonality": 0.2,
                "volatility": 0.2,
                "perishability": "low",
                "lead_time_days": 7
            }
        }
        
        # Market factors affecting demand
        self.market_factors = {
            "festival_multiplier": 1.5,
            "weather_impact": 0.3,
            "price_elasticity": -0.8,
            "competitor_effect": 0.2,
            "season_boost": {
                "summer": {"mangoes": 2.0, "watermelon": 1.8},
                "winter": {"oranges": 1.5, "carrots": 1.3},
                "monsoon": {"leafy_greens": 0.7, "tomatoes": 0.8}
            }
        }
        
        # Create workflow
        self.workflow = self._create_workflow()
        
        logger.info("InventoryAgent initialized with demand forecasting models")
    
    def _create_workflow(self) -> StateGraph:
        """Create the LangGraph workflow for inventory management"""
        
        # Initialize the graph
        workflow = StateGraph(InventoryState)
        
        # Add nodes for inventory operations
        workflow.add_node("demand_forecaster", self.demand_forecaster_node)
        workflow.add_node("stock_optimizer", self.stock_optimizer_node)
        workflow.add_node("reorder_planner", self.reorder_planner_node)
        workflow.add_node("expiry_manager", self.expiry_manager_node)
        workflow.add_node("kpi_analyzer", self.kpi_analyzer_node)
        workflow.add_node("coordinator", self.coordinator_node)
        
        # Set entry point
        workflow.set_entry_point("coordinator")
        
        # Add conditional routing from coordinator
        workflow.add_conditional_edges(
            "coordinator",
            self.route_inventory_task,
            {
                "demand_forecast": "demand_forecaster",
                "stock_optimize": "stock_optimizer",
                "reorder_plan": "reorder_planner",
                "expiry_alert": "expiry_manager",
                "kpi_analysis": "kpi_analyzer",
                "end": END
            }
        )
        
        # Chain inventory management process
        workflow.add_edge("demand_forecaster", "stock_optimizer")
        workflow.add_edge("stock_optimizer", "reorder_planner")
        workflow.add_edge("reorder_planner", "expiry_manager")
        workflow.add_edge("expiry_manager", "kpi_analyzer")
        workflow.add_edge("kpi_analyzer", "coordinator")
        
        return workflow.compile()
    
    async def coordinator_node(self, state: InventoryState) -> InventoryState:
        """
        Coordinator node that orchestrates inventory management
        """
        logger.info(f"Inventory Coordinator processing task: {state.get('task_type')}")
        
        # Check completion status
        has_forecast = bool(state.get("forecast_results"))
        has_optimization = bool(state.get("optimization_plan"))
        has_reorder = bool(state.get("reorder_plan"))
        has_expiry = bool(state.get("expiry_alerts"))
        has_kpis = bool(state.get("kpis"))
        
        # Determine next step
        if not has_forecast:
            next_step = "demand_forecast"
        elif not has_optimization:
            next_step = "stock_optimize"
        elif not has_reorder:
            next_step = "reorder_plan"
        elif not has_expiry:
            next_step = "expiry_alert"
        elif not has_kpis:
            next_step = "kpi_analysis"
        else:
            next_step = "end"
        
        message = AIMessage(content=f"Inventory coordinator: Next step - {next_step}")
        
        return {
            **state,
            "next_step": next_step,
            "messages": state.get("messages", []) + [message]
        }
    
    def route_inventory_task(self, state: InventoryState) -> str:
        """Route to the appropriate inventory operation"""
        return state.get("next_step", "end")
    
    async def demand_forecaster_node(self, state: InventoryState) -> InventoryState:
        """
        AI-powered demand forecasting using historical data and market factors
        """
        logger.info("Demand Forecaster activated")
        
        inventory_data = state.get("inventory_data", [])
        historical_sales = state.get("historical_sales", [])
        market_conditions = state.get("market_conditions", {})
        
        forecast_results = []
        
        for item in inventory_data:
            product_id = item.get("product_id", "unknown")
            
            # Generate demand forecast using AI analysis
            forecast = await self._forecast_demand(item, historical_sales, market_conditions)
            forecast_results.append(forecast)
        
        total_forecasted = sum(sum(f["predicted_demand"]) for f in forecast_results)
        message = AIMessage(content=f"Demand forecast generated for {len(forecast_results)} products. Total predicted demand: {total_forecasted:.0f} units")
        
        return {
            **state,
            "forecast_results": forecast_results,
            "messages": state.get("messages", []) + [message]
        }
    
    async def stock_optimizer_node(self, state: InventoryState) -> InventoryState:
        """
        Optimize inventory levels based on demand forecasts
        """
        logger.info("Stock Optimizer activated")
        
        inventory_data = state.get("inventory_data", [])
        forecast_results = state.get("forecast_results", [])
        
        # Create optimization plan
        optimization_plan = await self._optimize_inventory_levels(inventory_data, forecast_results)
        
        total_cost_saving = optimization_plan.get("total_cost_saving", 0)
        message = AIMessage(content=f"Inventory optimization complete. Potential cost savings: ₹{total_cost_saving:,.2f}")
        
        return {
            **state,
            "optimization_plan": optimization_plan,
            "messages": state.get("messages", []) + [message]
        }
    
    async def reorder_planner_node(self, state: InventoryState) -> InventoryState:
        """
        Create intelligent reorder plans based on forecasts and optimization
        """
        logger.info("Reorder Planner activated")
        
        inventory_data = state.get("inventory_data", [])
        forecast_results = state.get("forecast_results", [])
        optimization_plan = state.get("optimization_plan", {})
        
        # Generate reorder recommendations
        reorder_plan = await self._generate_reorder_plan(inventory_data, forecast_results, optimization_plan)
        
        reorder_items = len(reorder_plan.get("reorder_list", []))
        message = AIMessage(content=f"Reorder plan created for {reorder_items} products requiring restocking")
        
        return {
            **state,
            "reorder_plan": reorder_plan,
            "messages": state.get("messages", []) + [message]
        }
    
    async def expiry_manager_node(self, state: InventoryState) -> InventoryState:
        """
        Manage product expiry and minimize waste
        """
        logger.info("Expiry Manager activated")
        
        inventory_data = state.get("inventory_data", [])
        
        # Generate expiry alerts and waste prevention recommendations
        expiry_alerts = await self._manage_expiry_alerts(inventory_data)
        
        critical_alerts = len([a for a in expiry_alerts if a.get("priority") == "high"])
        message = AIMessage(content=f"Expiry management complete. {critical_alerts} critical alerts generated")
        
        return {
            **state,
            "expiry_alerts": expiry_alerts,
            "messages": state.get("messages", []) + [message]
        }
    
    async def kpi_analyzer_node(self, state: InventoryState) -> InventoryState:
        """
        Analyze key performance indicators for inventory management
        """
        logger.info("KPI Analyzer activated")
        
        inventory_data = state.get("inventory_data", [])
        forecast_results = state.get("forecast_results", [])
        optimization_plan = state.get("optimization_plan", {})
        
        # Calculate comprehensive KPIs
        kpis = await self._calculate_inventory_kpis(inventory_data, forecast_results, optimization_plan)
        
        inventory_turnover = kpis.get("inventory_turnover", 0)
        message = AIMessage(content=f"KPI analysis complete. Inventory turnover: {inventory_turnover:.1f}x annually")
        
        return {
            **state,
            "kpis": kpis,
            "messages": state.get("messages", []) + [message]
        }
    
    async def _forecast_demand(self, item: Dict[str, Any], 
                              historical_sales: List[Dict[str, Any]], 
                              market_conditions: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate AI-powered demand forecast for a product
        """
        product_id = item.get("product_id", "")
        product_name = item.get("name", "")
        category = item.get("category", "vegetables")
        
        # Get historical data for this product
        product_sales = [sale for sale in historical_sales if sale.get("product_id") == product_id]
        
        # Base demand calculation
        if product_sales:
            recent_sales = [sale.get("quantity", 0) for sale in product_sales[-30:]]  # Last 30 days
            base_demand = np.mean(recent_sales) if recent_sales else 10
        else:
            base_demand = 15  # Default assumption
        
        # Apply seasonality and market factors
        season = market_conditions.get("season", "summer")
        festival_boost = market_conditions.get("festival_upcoming", False)
        weather_factor = market_conditions.get("weather_impact", 1.0)
        
        # Generate 7-day forecast
        forecast_days = 7
        predicted_demand = []
        
        for day in range(forecast_days):
            daily_demand = base_demand
            
            # Add seasonality
            seasonal_factor = self.demand_patterns.get(category, {}).get("seasonality", 0.3)
            daily_demand *= (1 + seasonal_factor * np.sin(day * 2 * np.pi / 7))
            
            # Add market factors
            if festival_boost:
                daily_demand *= self.market_factors["festival_multiplier"]
            
            daily_demand *= weather_factor
            
            # Add random variation
            volatility = self.demand_patterns.get(category, {}).get("volatility", 0.4)
            daily_demand *= (1 + np.random.normal(0, volatility * 0.1))
            
            predicted_demand.append(max(0, int(daily_demand)))
        
        # Calculate confidence intervals
        confidence_interval = [(max(0, int(d * 0.8)), int(d * 1.2)) for d in predicted_demand]
        
        return {
            "product_id": product_id,
            "product_name": product_name,
            "forecast_period": "daily",
            "predicted_demand": predicted_demand,
            "confidence_interval": confidence_interval,
            "seasonality_factor": seasonal_factor,
            "trend_factor": 1.0,
            "total_forecast": sum(predicted_demand),
            "recommendations": self._generate_demand_recommendations(predicted_demand, base_demand)
        }
    
    async def _optimize_inventory_levels(self, inventory_data: List[Dict[str, Any]], 
                                        forecast_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Optimize inventory levels using AI analysis
        """
        optimization_recommendations = []
        total_cost_saving = 0
        
        for item in inventory_data:
            product_id = item.get("product_id", "")
            current_stock = item.get("current_stock", 0)
            unit_cost = item.get("unit_cost", 10)
            
            # Find forecast for this product
            forecast = next((f for f in forecast_results if f["product_id"] == product_id), None)
            
            if forecast:
                total_forecast = forecast.get("total_forecast", 0)
                
                # Calculate optimal stock levels
                safety_stock = max(5, int(total_forecast * 0.2))  # 20% safety buffer
                optimal_stock = total_forecast + safety_stock
                
                # Calculate adjustments
                stock_adjustment = optimal_stock - current_stock
                cost_impact = abs(stock_adjustment) * unit_cost
                
                if stock_adjustment > 0:
                    action = "increase"
                    impact = "prevent_stockout"
                elif stock_adjustment < 0:
                    action = "reduce"
                    impact = "reduce_holding_cost"
                    total_cost_saving += abs(stock_adjustment) * unit_cost * 0.1  # 10% holding cost
                else:
                    action = "maintain"
                    impact = "optimal_level"
                
                optimization_recommendations.append({
                    "product_id": product_id,
                    "current_stock": current_stock,
                    "optimal_stock": optimal_stock,
                    "adjustment": stock_adjustment,
                    "action": action,
                    "cost_impact": cost_impact,
                    "impact": impact,
                    "priority": "high" if abs(stock_adjustment) > total_forecast * 0.3 else "medium"
                })
        
        return {
            "optimization_recommendations": optimization_recommendations,
            "total_cost_saving": total_cost_saving,
            "optimization_score": min(100, total_cost_saving / 1000 * 10),
            "summary": {
                "items_to_increase": len([r for r in optimization_recommendations if r["action"] == "increase"]),
                "items_to_reduce": len([r for r in optimization_recommendations if r["action"] == "reduce"]),
                "items_optimal": len([r for r in optimization_recommendations if r["action"] == "maintain"])
            }
        }
    
    async def _generate_reorder_plan(self, inventory_data: List[Dict[str, Any]], 
                                    forecast_results: List[Dict[str, Any]], 
                                    optimization_plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate intelligent reorder plan
        """
        reorder_list = []
        total_reorder_cost = 0
        
        optimization_recs = optimization_plan.get("optimization_recommendations", [])
        
        for item in inventory_data:
            product_id = item.get("product_id", "")
            current_stock = item.get("current_stock", 0)
            reorder_point = item.get("reorder_point", 10)
            unit_cost = item.get("unit_cost", 10)
            lead_time = item.get("lead_time_days", 3)
            
            # Find optimization recommendation
            opt_rec = next((r for r in optimization_recs if r["product_id"] == product_id), None)
            
            # Check if reorder is needed
            needs_reorder = current_stock <= reorder_point
            
            if needs_reorder or (opt_rec and opt_rec["action"] == "increase"):
                # Calculate order quantity
                if opt_rec:
                    order_quantity = max(0, opt_rec["adjustment"])
                else:
                    # Standard reorder calculation
                    forecast = next((f for f in forecast_results if f["product_id"] == product_id), None)
                    if forecast:
                        weekly_demand = sum(forecast.get("predicted_demand", [0]))
                        order_quantity = weekly_demand + reorder_point - current_stock
                    else:
                        order_quantity = reorder_point - current_stock
                
                if order_quantity > 0:
                    order_cost = order_quantity * unit_cost
                    total_reorder_cost += order_cost
                    
                    # Calculate urgency
                    if current_stock <= reorder_point * 0.5:
                        urgency = "critical"
                        recommended_date = datetime.now().date()
                    elif current_stock <= reorder_point:
                        urgency = "high"
                        recommended_date = (datetime.now() + timedelta(days=1)).date()
                    else:
                        urgency = "medium"
                        recommended_date = (datetime.now() + timedelta(days=lead_time)).date()
                    
                    reorder_list.append({
                        "product_id": product_id,
                        "current_stock": current_stock,
                        "reorder_point": reorder_point,
                        "order_quantity": order_quantity,
                        "unit_cost": unit_cost,
                        "order_cost": order_cost,
                        "urgency": urgency,
                        "recommended_date": recommended_date.isoformat(),
                        "lead_time_days": lead_time,
                        "supplier": item.get("preferred_supplier", "default")
                    })
        
        # Sort by urgency and cost impact
        reorder_list.sort(key=lambda x: (
            {"critical": 0, "high": 1, "medium": 2}[x["urgency"]],
            -x["order_cost"]
        ))
        
        return {
            "reorder_list": reorder_list,
            "total_items": len(reorder_list),
            "total_cost": total_reorder_cost,
            "critical_items": len([r for r in reorder_list if r["urgency"] == "critical"]),
            "execution_timeline": {
                "immediate": len([r for r in reorder_list if r["urgency"] == "critical"]),
                "this_week": len([r for r in reorder_list if r["urgency"] == "high"]),
                "next_week": len([r for r in reorder_list if r["urgency"] == "medium"])
            }
        }
    
    async def _manage_expiry_alerts(self, inventory_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Generate expiry alerts and waste prevention recommendations
        """
        alerts = []
        
        for item in inventory_data:
            product_id = item.get("product_id", "")
            current_stock = item.get("current_stock", 0)
            shelf_life_days = item.get("shelf_life_days", 7)
            unit_cost = item.get("unit_cost", 10)
            
            # Simulate batch tracking (in production, use actual batch data)
            batches = [
                {"batch_id": f"B001_{product_id}", "quantity": current_stock // 2, "days_left": 2},
                {"batch_id": f"B002_{product_id}", "quantity": current_stock // 2, "days_left": 5}
            ]
            
            for batch in batches:
                days_left = batch["days_left"]
                quantity = batch["quantity"]
                
                if days_left <= 1:
                    priority = "critical"
                    action = "immediate_sale_or_processing"
                    potential_loss = quantity * unit_cost
                elif days_left <= 2:
                    priority = "high"
                    action = "discount_pricing"
                    potential_loss = quantity * unit_cost * 0.3
                elif days_left <= shelf_life_days * 0.5:
                    priority = "medium"
                    action = "promote_sales"
                    potential_loss = quantity * unit_cost * 0.1
                else:
                    continue
                
                alerts.append({
                    "product_id": product_id,
                    "batch_id": batch["batch_id"],
                    "quantity": quantity,
                    "days_left": days_left,
                    "priority": priority,
                    "recommended_action": action,
                    "potential_loss": potential_loss,
                    "created_at": datetime.now().isoformat()
                })
        
        return alerts
    
    async def _calculate_inventory_kpis(self, inventory_data: List[Dict[str, Any]], 
                                       forecast_results: List[Dict[str, Any]], 
                                       optimization_plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate comprehensive inventory management KPIs
        """
        if not inventory_data:
            return {}
        
        # Calculate basic metrics
        total_inventory_value = sum(
            item.get("current_stock", 0) * item.get("unit_cost", 0) 
            for item in inventory_data
        )
        
        total_available_stock = sum(item.get("available_stock", 0) for item in inventory_data)
        total_reserved_stock = sum(item.get("reserved_stock", 0) for item in inventory_data)
        
        # Calculate turnover (simulate with forecast data)
        total_forecasted_demand = sum(
            sum(f.get("predicted_demand", [])) for f in forecast_results
        ) * 52  # Annualized
        
        inventory_turnover = total_forecasted_demand / total_inventory_value if total_inventory_value > 0 else 0
        
        # Stock levels analysis
        stockout_risk_items = sum(
            1 for item in inventory_data 
            if item.get("current_stock", 0) <= item.get("reorder_point", 0)
        )
        
        overstock_items = sum(
            1 for item in inventory_data 
            if item.get("current_stock", 0) > item.get("max_stock", 100)
        )
        
        # Optimization impact
        potential_savings = optimization_plan.get("total_cost_saving", 0)
        
        return {
            "inventory_value": total_inventory_value,
            "inventory_turnover": round(inventory_turnover, 2),
            "stock_utilization": round((total_reserved_stock / (total_available_stock + total_reserved_stock)) * 100, 1) if (total_available_stock + total_reserved_stock) > 0 else 0,
            "stockout_risk_items": stockout_risk_items,
            "overstock_items": overstock_items,
            "optimization_potential": round(potential_savings, 2),
            "inventory_health_score": min(100, max(0, 100 - stockout_risk_items * 10 - overstock_items * 5)),
            "days_of_inventory": round(total_inventory_value / (total_forecasted_demand / 365), 1) if total_forecasted_demand > 0 else 0,
            "forecast_accuracy": 85.5,  # Simulated metric
            "waste_percentage": 2.3,    # Simulated metric
            "last_updated": datetime.now().isoformat()
        }
    
    def _generate_demand_recommendations(self, predicted_demand: List[float], base_demand: float) -> List[str]:
        """Generate recommendations based on demand forecast"""
        recommendations = []
        
        avg_forecast = np.mean(predicted_demand)
        max_demand = max(predicted_demand)
        min_demand = min(predicted_demand)
        
        # Demand variation analysis
        if max_demand > base_demand * 1.5:
            recommendations.append("High demand spike expected - ensure adequate stock levels")
        
        if min_demand < base_demand * 0.5:
            recommendations.append("Low demand period forecasted - consider promotional activities")
        
        # Trend analysis
        if predicted_demand[-1] > predicted_demand[0] * 1.2:
            recommendations.append("Growing demand trend detected - consider increasing stock")
        elif predicted_demand[-1] < predicted_demand[0] * 0.8:
            recommendations.append("Declining demand trend - optimize inventory levels")
        
        return recommendations
    
    async def execute(self, task_type: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute inventory management workflow
        """
        logger.info(f"Executing inventory management task: {task_type}")
        
        # Initialize state
        initial_state = {
            "messages": [HumanMessage(content=f"Execute inventory management: {task_type}")],
            "task_type": task_type,
            "inventory_data": task_data.get("inventory_data", []),
            "historical_sales": task_data.get("historical_sales", []),
            "market_conditions": task_data.get("market_conditions", {}),
            "forecast_results": [],
            "optimization_plan": {},
            "alerts": [],
            "recommendations": [],
            "kpis": {}
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
                "forecast_results": final_state.get("forecast_results", []),
                "optimization_plan": final_state.get("optimization_plan", {}),
                "reorder_plan": final_state.get("reorder_plan", {}),
                "expiry_alerts": final_state.get("expiry_alerts", []),
                "kpis": final_state.get("kpis", {}),
                "messages": [msg.content for msg in final_state.get("messages", [])]
            }
            
            logger.info(f"Inventory management completed in {execution_time:.2f} seconds")
            return result
            
        except Exception as e:
            logger.error(f"Inventory management workflow failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "task_type": task_type
            }

# Example usage
async def main():
    """Example usage of the inventory agent"""
    
    inventory_agent = InventoryAgent()
    
    # Test inventory optimization
    inventory_task = {
        "inventory_data": [
            {
                "product_id": "TOM001",
                "name": "Fresh Tomatoes",
                "category": "vegetables",
                "current_stock": 50,
                "reserved_stock": 10,
                "available_stock": 40,
                "reorder_point": 20,
                "max_stock": 100,
                "unit_cost": 35,
                "shelf_life_days": 7,
                "lead_time_days": 1
            },
            {
                "product_id": "ONI001", 
                "name": "Onions",
                "category": "vegetables",
                "current_stock": 30,
                "reserved_stock": 5,
                "available_stock": 25,
                "reorder_point": 15,
                "max_stock": 80,
                "unit_cost": 25,
                "shelf_life_days": 30,
                "lead_time_days": 2
            }
        ],
        "historical_sales": [
            {"product_id": "TOM001", "date": "2024-01-15", "quantity": 45},
            {"product_id": "TOM001", "date": "2024-01-14", "quantity": 38},
            {"product_id": "ONI001", "date": "2024-01-15", "quantity": 25}
        ],
        "market_conditions": {
            "season": "winter",
            "festival_upcoming": True,
            "weather_impact": 1.2
        }
    }
    
    result = await inventory_agent.execute("demand_forecast", inventory_task)
    print("Inventory Management Result:", json.dumps(result, indent=2, default=str))

if __name__ == "__main__":
    asyncio.run(main())