"""
FarmConnect Supervisor Agent - LangGraph Implementation
Orchestrates multiple specialized agents for autonomous marketplace operations
"""

from typing import TypedDict, Annotated, Sequence, Literal, Optional, Dict, Any, List
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain.schema import BaseMessage, HumanMessage, AIMessage, SystemMessage
import operator
import asyncio
import json
from datetime import datetime
import logging
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AgentState(TypedDict):
    """Global state shared across all agents"""
    messages: Annotated[Sequence[BaseMessage], operator.add]
    current_task: str
    task_type: Literal["price_check", "quality_assess", "logistics", "negotiation", "market_analysis", "farmer_assist"]
    products: List[Dict[str, Any]]
    farmers: List[Dict[str, Any]]
    orders: List[Dict[str, Any]]
    prices: Dict[str, Any]
    quality_reports: List[Dict[str, Any]]
    logistics_plan: Dict[str, Any]
    market_insights: Dict[str, Any]
    farmer_advice: Dict[str, Any]
    negotiation_outcome: Dict[str, Any]
    next_agent: str
    iteration: int
    max_iterations: int
    execution_start: datetime
    metadata: Dict[str, Any]

class SupervisorAgent:
    """
    Main orchestrator that coordinates all specialized agents
    """
    
    def __init__(self, openai_api_key: str = None):
        """Initialize the supervisor with LangGraph workflow"""
        
        # Get API key from environment or parameter
        api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
        
        if not api_key:
            raise ValueError(
                "OpenAI API key not found. Please set OPENAI_API_KEY in .env file or pass it directly."
            )
        
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0,
            api_key=api_key
        )
        
        # Initialize specialized agents (to be imported)
        self.agents = self._initialize_agents()
        
        # Create the workflow
        self.workflow = self._create_workflow()
        
        logger.info("SupervisorAgent initialized with workflow")
    
    def _initialize_agents(self) -> Dict:
        """Initialize all specialized agents"""
        # These would be imported from separate modules
        return {
            "price_monitor": None,  # PriceMonitorAgent()
            "quality_inspector": None,  # QualityInspectorAgent()
            "farmer_assistant": None,  # FarmerAssistantAgent()
            "logistics_optimizer": None,  # LogisticsOptimizerAgent()
            "market_analyst": None,  # MarketAnalystAgent()
            "negotiation": None  # NegotiationAgent()
        }
    
    def _create_workflow(self) -> StateGraph:
        """Create the LangGraph workflow with all agents"""
        
        # Initialize the graph
        workflow = StateGraph(AgentState)
        
        # Add nodes for each agent
        workflow.add_node("supervisor", self.supervisor_node)
        workflow.add_node("price_monitor", self.price_monitor_node)
        workflow.add_node("quality_inspector", self.quality_inspector_node)
        workflow.add_node("farmer_assistant", self.farmer_assistant_node)
        workflow.add_node("logistics_optimizer", self.logistics_optimizer_node)
        workflow.add_node("market_analyst", self.market_analyst_node)
        workflow.add_node("negotiation", self.negotiation_node)
        
        # Set entry point
        workflow.set_entry_point("supervisor")
        
        # Add conditional routing from supervisor
        workflow.add_conditional_edges(
            "supervisor",
            self.route_task,
            {
                "price_monitor": "price_monitor",
                "quality_inspector": "quality_inspector",
                "farmer_assistant": "farmer_assistant",
                "logistics_optimizer": "logistics_optimizer",
                "market_analyst": "market_analyst",
                "negotiation": "negotiation",
                "end": END
            }
        )
        
        # All agents return to supervisor
        for agent in ["price_monitor", "quality_inspector", "farmer_assistant",
                     "logistics_optimizer", "market_analyst", "negotiation"]:
            workflow.add_edge(agent, "supervisor")
        
        return workflow.compile()
    
    async def supervisor_node(self, state: AgentState) -> AgentState:
        """
        Supervisor logic to coordinate agents based on task requirements
        """
        
        logger.info(f"Supervisor processing iteration {state.get('iteration', 0)}")
        
        # Check if we've exceeded max iterations
        if state.get("iteration", 0) >= state.get("max_iterations", 10):
            logger.warning("Max iterations reached, ending workflow")
            return {
                **state,
                "next_agent": "end"
            }
        
        # System prompt for supervisor
        system_prompt = """You are the supervisor of FarmConnect, an AI-powered farm-to-fork marketplace.
        Your role is to coordinate specialized agents to fulfill user requests efficiently.
        
        Available agents and their capabilities:
        1. price_monitor: Scrapes and compares prices across BigBasket, Zepto, Swiggy, Blinkit
        2. quality_inspector: Analyzes product quality from images using computer vision
        3. farmer_assistant: Provides personalized farming advice, weather updates, crop recommendations
        4. logistics_optimizer: Plans optimal delivery routes, selects delivery partners
        5. market_analyst: Provides market insights, demand forecasting, price predictions
        6. negotiation: Mediates price negotiations between farmers and buyers
        
        Based on the current task and what has been completed, decide:
        - Which agent should act next to progress the task
        - Or if the task is complete, return 'end'
        
        Consider the task type and current state to make your decision.
        Response format: Return ONLY the agent name or 'end', nothing else.
        """
        
        # Prepare context for decision
        context = self._prepare_context(state)
        
        # Get supervisor decision
        messages = state.get("messages", [])
        response = await self.llm.ainvoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"Current context: {json.dumps(context, indent=2)}"),
            *messages[-5:]  # Include last 5 messages for context
        ])
        
        # Parse the response to get next agent
        next_agent = self._parse_supervisor_response(response.content)
        
        logger.info(f"Supervisor routing to: {next_agent}")
        
        # Update state
        return {
            **state,
            "messages": state.get("messages", []) + [response],
            "next_agent": next_agent,
            "iteration": state.get("iteration", 0) + 1
        }
    
    def _prepare_context(self, state: AgentState) -> Dict:
        """Prepare context for supervisor decision"""
        return {
            "task_type": state.get("task_type"),
            "current_task": state.get("current_task"),
            "iteration": state.get("iteration", 0),
            "has_prices": bool(state.get("prices")),
            "has_quality_reports": bool(state.get("quality_reports")),
            "has_logistics_plan": bool(state.get("logistics_plan")),
            "has_market_insights": bool(state.get("market_insights")),
            "products_count": len(state.get("products", [])),
            "farmers_count": len(state.get("farmers", [])),
            "orders_count": len(state.get("orders", []))
        }
    
    def _parse_supervisor_response(self, response: str) -> str:
        """Parse supervisor response to extract agent name"""
        
        # Clean the response
        agent_name = response.strip().lower()
        
        # Map to valid agent names
        valid_agents = [
            "price_monitor", "quality_inspector", "farmer_assistant",
            "logistics_optimizer", "market_analyst", "negotiation", "end"
        ]
        
        # Find the best match
        for valid in valid_agents:
            if valid in agent_name:
                return valid
        
        # Default to end if no match
        logger.warning(f"Could not parse agent from response: {response}")
        return "end"
    
    def route_task(self, state: AgentState) -> str:
        """Route to the appropriate agent based on supervisor decision"""
        
        # Check iteration limit
        if state.get("iteration", 0) >= state.get("max_iterations", 10):
            return "end"
        
        next_agent = state.get("next_agent", "end")
        logger.info(f"Routing to agent: {next_agent}")
        
        return next_agent
    
    async def price_monitor_node(self, state: AgentState) -> AgentState:
        """Price monitoring agent node"""
        
        logger.info("Price Monitor Agent activated")
        
        # Simulate price monitoring (would call actual agent)
        products = state.get("products", [])
        
        if not products:
            products = [
                {"id": "1", "name": "Tomatoes", "unit": "kg"},
                {"id": "2", "name": "Onions", "unit": "kg"}
            ]
        
        # Mock price data
        prices = {}
        for product in products:
            prices[product["name"]] = {
                "farmer_price": 35,
                "bigbasket": 48,
                "zepto": 49,
                "swiggy": 47,
                "blinkit": 46,
                "savings": "28%",
                "timestamp": datetime.now().isoformat()
            }
        
        message = AIMessage(content=f"Price monitoring complete. Found prices for {len(products)} products with average savings of 28%")
        
        return {
            **state,
            "prices": prices,
            "messages": state.get("messages", []) + [message]
        }
    
    async def quality_inspector_node(self, state: AgentState) -> AgentState:
        """Quality inspection agent node"""
        
        logger.info("Quality Inspector Agent activated")
        
        # Mock quality inspection
        products = state.get("products", [])
        
        quality_reports = []
        for product in products:
            quality_reports.append({
                "product_id": product.get("id"),
                "product_name": product.get("name"),
                "grade": "A",
                "freshness_score": 9,
                "defects": [],
                "shelf_life": "5 days",
                "recommendation": "Premium pricing - Ready for immediate sale",
                "timestamp": datetime.now().isoformat()
            })
        
        message = AIMessage(content=f"Quality inspection complete. All {len(products)} products graded A quality.")
        
        return {
            **state,
            "quality_reports": quality_reports,
            "messages": state.get("messages", []) + [message]
        }
    
    async def farmer_assistant_node(self, state: AgentState) -> AgentState:
        """Farmer assistance agent node"""
        
        logger.info("Farmer Assistant Agent activated")
        
        # Mock farmer assistance
        advice = {
            "weather_forecast": "Partly cloudy, 28°C, no rain expected",
            "crop_recommendation": "Good time for tomato harvest",
            "pest_alert": "Low risk",
            "market_timing": "High demand expected this weekend",
            "price_suggestion": "Consider premium pricing for A-grade produce"
        }
        
        message = AIMessage(content="Farmer assistance provided: Good harvest conditions, high market demand expected.")
        
        return {
            **state,
            "farmer_advice": advice,
            "messages": state.get("messages", []) + [message]
        }
    
    async def logistics_optimizer_node(self, state: AgentState) -> AgentState:
        """Logistics optimization agent node"""
        
        logger.info("Logistics Optimizer Agent activated")
        
        # Mock logistics planning
        orders = state.get("orders", [])
        
        if not orders:
            orders = [{"id": "ORD001", "location": "Mumbai", "weight": 50}]
        
        logistics_plan = {
            "routes": [
                {
                    "route_id": "R001",
                    "orders": ["ORD001"],
                    "distance": 25,
                    "time": 45,
                    "cost": 250
                }
            ],
            "total_distance": 25,
            "total_time": 45,
            "total_cost": 250,
            "delivery_partner": "Dunzo",
            "vehicle_type": "Mini Truck"
        }
        
        message = AIMessage(content="Logistics optimized: 1 route planned, ₹250 cost, 45 min delivery time")
        
        return {
            **state,
            "logistics_plan": logistics_plan,
            "messages": state.get("messages", []) + [message]
        }
    
    async def market_analyst_node(self, state: AgentState) -> AgentState:
        """Market analysis agent node"""
        
        logger.info("Market Analyst Agent activated")
        
        # Mock market analysis
        insights = {
            "price_trend": "Upward",
            "demand_forecast": "High demand expected for next 7 days",
            "supply_status": "Normal",
            "competitor_analysis": "BigBasket running 10% discount",
            "recommendation": "Increase supply by 20% to meet demand",
            "confidence": 0.85
        }
        
        message = AIMessage(content="Market analysis complete: High demand expected, recommend 20% supply increase")
        
        return {
            **state,
            "market_insights": insights,
            "messages": state.get("messages", []) + [message]
        }
    
    async def negotiation_node(self, state: AgentState) -> AgentState:
        """Price negotiation agent node"""
        
        logger.info("Negotiation Agent activated")
        
        # Mock negotiation
        outcome = {
            "agreement_reached": True,
            "final_price": 38,
            "farmer_price": 35,
            "buyer_offer": 40,
            "savings_for_buyer": "20%",
            "profit_for_farmer": "8.5%"
        }
        
        message = AIMessage(content="Negotiation successful: Agreed at ₹38/kg (20% buyer savings, 8.5% farmer profit)")
        
        return {
            **state,
            "negotiation_outcome": outcome,
            "messages": state.get("messages", []) + [message]
        }
    
    async def execute(self, task_type: str, initial_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the workflow with given task and data
        """
        
        logger.info(f"Starting workflow execution for task: {task_type}")
        
        # Initialize state
        initial_state = {
            "messages": [HumanMessage(content=f"Execute {task_type} task")],
            "current_task": initial_data.get("task_description", task_type),
            "task_type": task_type,
            "products": initial_data.get("products", []),
            "farmers": initial_data.get("farmers", []),
            "orders": initial_data.get("orders", []),
            "prices": {},
            "quality_reports": [],
            "logistics_plan": {},
            "market_insights": {},
            "farmer_advice": {},
            "negotiation_outcome": {},
            "next_agent": "supervisor",
            "iteration": 0,
            "max_iterations": initial_data.get("max_iterations", 10),
            "execution_start": datetime.now(),
            "metadata": initial_data.get("metadata", {})
        }
        
        try:
            # Execute workflow
            final_state = await self.workflow.ainvoke(initial_state)
            
            # Calculate execution time
            execution_time = (datetime.now() - final_state["execution_start"]).total_seconds()
            
            # Prepare response
            result = {
                "success": True,
                "task_type": task_type,
                "execution_time": execution_time,
                "iterations": final_state.get("iteration", 0),
                "prices": final_state.get("prices"),
                "quality_reports": final_state.get("quality_reports"),
                "logistics_plan": final_state.get("logistics_plan"),
                "market_insights": final_state.get("market_insights"),
                "farmer_advice": final_state.get("farmer_advice"),
                "negotiation_outcome": final_state.get("negotiation_outcome"),
                "messages": [msg.content for msg in final_state.get("messages", [])]
            }
            
            logger.info(f"Workflow completed successfully in {execution_time:.2f} seconds")
            
            return result
            
        except Exception as e:
            logger.error(f"Workflow execution failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "task_type": task_type
            }

# Example usage
async def main():
    """Example usage of the supervisor agent"""
    
    # Initialize supervisor
    supervisor = SupervisorAgent()
    
    # Example 1: Price monitoring task
    price_task = {
        "task_description": "Monitor prices for tomatoes and onions across all platforms",
        "products": [
            {"id": "1", "name": "Tomatoes", "unit": "kg"},
            {"id": "2", "name": "Onions", "unit": "kg"}
        ]
    }
    
    result = await supervisor.execute("price_check", price_task)
    print("Price Monitoring Result:", json.dumps(result, indent=2))
    
    # Example 2: Multi-agent task
    complex_task = {
        "task_description": "Check prices, assess quality, and optimize logistics for pending orders",
        "products": [
            {"id": "1", "name": "Tomatoes", "unit": "kg", "quantity": 100}
        ],
        "orders": [
            {"id": "ORD001", "location": "Mumbai", "weight": 100}
        ]
    }
    
    result = await supervisor.execute("market_analysis", complex_task)
    print("Complex Task Result:", json.dumps(result, indent=2))

if __name__ == "__main__":
    asyncio.run(main())