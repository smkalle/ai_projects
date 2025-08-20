"""
FarmConnect Revenue Insights Agent - LangGraph Implementation
AI-powered onboarding optimization and revenue maximization strategies
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
from dataclasses import dataclass

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class RevenueOpportunity:
    """Revenue optimization opportunity"""
    category: str
    opportunity_type: str
    potential_revenue: float
    implementation_effort: str
    time_to_impact: str
    confidence_score: float
    action_items: List[str]

class RevenueInsightsState(TypedDict):
    """State for revenue insights workflow"""
    messages: Annotated[Sequence[BaseMessage], operator.add]
    analysis_type: Literal["farmer_onboarding", "product_optimization", "pricing_strategy", "market_expansion"]
    farmer_data: List[Dict[str, Any]]
    product_data: List[Dict[str, Any]]
    market_data: Dict[str, Any]
    onboarding_insights: Dict[str, Any]
    product_insights: Dict[str, Any]
    pricing_recommendations: Dict[str, Any]
    revenue_opportunities: List[Dict[str, Any]]
    action_plan: Dict[str, Any]
    roi_projections: Dict[str, Any]

class RevenueInsightsAgent:
    """
    LangGraph-based Revenue Insights Agent for FarmConnect
    Analyzes farmer and product onboarding to maximize revenue
    """
    
    def __init__(self):
        """Initialize the revenue insights agent"""
        
        # Get API key from environment
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OpenAI API key not found in environment")
        
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0,
            api_key=api_key
        )
        
        # Revenue optimization metrics
        self.revenue_metrics = {
            "farmer_value_factors": {
                "organic_premium": 1.3,          # 30% premium for organic
                "certification_bonus": 1.2,      # 20% bonus for certifications
                "rating_multiplier": {           # Rating-based multipliers
                    4.8: 1.15, 4.5: 1.10, 4.0: 1.05, 3.5: 1.0
                },
                "delivery_radius_bonus": {       # Radius-based bonuses
                    "100+ km": 1.2, "50+ km": 1.1, "25+ km": 1.0
                }
            },
            "product_categories": {
                "vegetables": {"margin": 0.15, "demand_growth": 1.2},
                "fruits": {"margin": 0.20, "demand_growth": 1.4},
                "grains": {"margin": 0.10, "demand_growth": 1.1},
                "dairy": {"margin": 0.25, "demand_growth": 1.6},
                "organic": {"margin": 0.30, "demand_growth": 1.8}
            },
            "seasonal_multipliers": {
                "summer": {"mangoes": 2.0, "watermelon": 1.8, "vegetables": 0.9},
                "winter": {"oranges": 1.5, "carrots": 1.3, "leafy_greens": 1.4},
                "monsoon": {"grains": 1.2, "spices": 1.1, "vegetables": 0.8}
            }
        }
        
        # Target markets and pricing data
        self.market_analysis = {
            "target_demographics": {
                "urban_professionals": {"willingness_to_pay": 1.4, "organic_preference": 0.8},
                "health_conscious": {"willingness_to_pay": 1.6, "organic_preference": 0.9},
                "price_sensitive": {"willingness_to_pay": 0.9, "organic_preference": 0.3},
                "premium_buyers": {"willingness_to_pay": 1.8, "organic_preference": 0.95}
            },
            "competitor_analysis": {
                "bigbasket": {"market_share": 0.35, "avg_markup": 1.4},
                "grofers": {"market_share": 0.25, "avg_markup": 1.3},
                "local_stores": {"market_share": 0.40, "avg_markup": 1.2}
            }
        }
        
        # Create workflow
        self.workflow = self._create_workflow()
        
        logger.info("RevenueInsightsAgent initialized for onboarding optimization")
    
    def _create_workflow(self) -> StateGraph:
        """Create the LangGraph workflow for revenue insights"""
        
        # Initialize the graph
        workflow = StateGraph(RevenueInsightsState)
        
        # Add nodes for revenue analysis
        workflow.add_node("farmer_analyzer", self.farmer_analyzer_node)
        workflow.add_node("product_optimizer", self.product_optimizer_node)
        workflow.add_node("pricing_strategist", self.pricing_strategist_node)
        workflow.add_node("market_expander", self.market_expander_node)
        workflow.add_node("roi_calculator", self.roi_calculator_node)
        workflow.add_node("coordinator", self.coordinator_node)
        
        # Set entry point
        workflow.set_entry_point("coordinator")
        
        # Add conditional routing from coordinator
        workflow.add_conditional_edges(
            "coordinator",
            self.route_analysis_task,
            {
                "farmer_analysis": "farmer_analyzer",
                "product_optimization": "product_optimizer",
                "pricing_strategy": "pricing_strategist",
                "market_expansion": "market_expander",
                "roi_calculation": "roi_calculator",
                "end": END
            }
        )
        
        # Chain revenue analysis process
        workflow.add_edge("farmer_analyzer", "product_optimizer")
        workflow.add_edge("product_optimizer", "pricing_strategist")
        workflow.add_edge("pricing_strategist", "market_expander")
        workflow.add_edge("market_expander", "roi_calculator")
        workflow.add_edge("roi_calculator", "coordinator")
        
        return workflow.compile()
    
    async def coordinator_node(self, state: RevenueInsightsState) -> RevenueInsightsState:
        """Coordinate revenue analysis workflow"""
        
        logger.info(f"Revenue Coordinator processing: {state.get('analysis_type')}")
        
        # Check completion status
        has_farmer_insights = bool(state.get("onboarding_insights"))
        has_product_insights = bool(state.get("product_insights"))
        has_pricing = bool(state.get("pricing_recommendations"))
        has_market_expansion = bool(state.get("market_expansion_plan"))
        has_roi = bool(state.get("roi_projections"))
        
        # Determine next step
        if not has_farmer_insights:
            next_step = "farmer_analysis"
        elif not has_product_insights:
            next_step = "product_optimization"
        elif not has_pricing:
            next_step = "pricing_strategy"
        elif not has_market_expansion:
            next_step = "market_expansion"
        elif not has_roi:
            next_step = "roi_calculation"
        else:
            next_step = "end"
        
        message = AIMessage(content=f"Revenue coordinator: Next analysis - {next_step}")
        
        return {
            **state,
            "next_step": next_step,
            "messages": state.get("messages", []) + [message]
        }
    
    def route_analysis_task(self, state: RevenueInsightsState) -> str:
        """Route to the appropriate analysis step"""
        return state.get("next_step", "end")
    
    async def farmer_analyzer_node(self, state: RevenueInsightsState) -> RevenueInsightsState:
        """
        Analyze farmer onboarding patterns for revenue optimization
        """
        logger.info("Farmer Analyzer activated")
        
        farmer_data = state.get("farmer_data", [])
        
        if not farmer_data:
            # Use mock data for analysis
            farmer_data = [
                {
                    "id": 1, "name": "Rajesh Kumar", "location": "Pune Rural",
                    "products": ["Tomatoes", "Cucumbers", "Spinach"],
                    "rating": 4.8, "delivery_radius": "50 km",
                    "certifications": ["Organic Certified", "GAP Certified"],
                    "monthly_revenue": 45000, "join_date": "2024-01-15"
                },
                {
                    "id": 2, "name": "Sita Devi", "location": "Nashik",
                    "products": ["Onions", "Grapes", "Pomegranate"],
                    "rating": 4.6, "delivery_radius": "100 km",
                    "certifications": ["APEDA Registered"],
                    "monthly_revenue": 62000, "join_date": "2024-02-20"
                }
            ]
        
        # Analyze high-value farmer characteristics
        insights = await self._analyze_farmer_value_patterns(farmer_data)
        
        message = AIMessage(content=f"Farmer analysis complete. Identified {len(insights['high_value_segments'])} high-value segments")
        
        return {
            **state,
            "onboarding_insights": insights,
            "messages": state.get("messages", []) + [message]
        }
    
    async def product_optimizer_node(self, state: RevenueInsightsState) -> RevenueInsightsState:
        """
        Optimize product mix and onboarding for maximum revenue
        """
        logger.info("Product Optimizer activated")
        
        product_data = state.get("product_data", [])
        onboarding_insights = state.get("onboarding_insights", {})
        
        if not product_data:
            # Use mock data
            product_data = [
                {
                    "id": 1, "name": "Fresh Tomatoes", "category": "Vegetables",
                    "price": 35, "unit": "kg", "farmer_name": "Rajesh Kumar",
                    "organic_certified": True, "monthly_sales": 1200,
                    "profit_margin": 0.18, "demand_growth": 1.3
                },
                {
                    "id": 2, "name": "Alphonso Mangoes", "category": "Fruits",
                    "price": 180, "unit": "dozen", "farmer_name": "Prakash Patil",
                    "organic_certified": True, "monthly_sales": 800,
                    "profit_margin": 0.25, "demand_growth": 1.8
                }
            ]
        
        # Optimize product portfolio
        product_insights = await self._optimize_product_portfolio(product_data, onboarding_insights)
        
        message = AIMessage(content=f"Product optimization complete. {len(product_insights['recommendations'])} optimization opportunities identified")
        
        return {
            **state,
            "product_insights": product_insights,
            "messages": state.get("messages", []) + [message]
        }
    
    async def pricing_strategist_node(self, state: RevenueInsightsState) -> RevenueInsightsState:
        """
        Develop dynamic pricing strategies for revenue maximization
        """
        logger.info("Pricing Strategist activated")
        
        product_data = state.get("product_data", [])
        market_data = state.get("market_data", {})
        
        # Analyze optimal pricing strategies
        pricing_recommendations = await self._develop_pricing_strategy(product_data, market_data)
        
        message = AIMessage(content=f"Pricing strategy developed with {len(pricing_recommendations['strategies'])} pricing models")
        
        return {
            **state,
            "pricing_recommendations": pricing_recommendations,
            "messages": state.get("messages", []) + [message]
        }
    
    async def market_expander_node(self, state: RevenueInsightsState) -> RevenueInsightsState:
        """
        Identify market expansion opportunities
        """
        logger.info("Market Expander activated")
        
        farmer_data = state.get("farmer_data", [])
        product_data = state.get("product_data", [])
        
        # Analyze expansion opportunities
        expansion_plan = await self._identify_expansion_opportunities(farmer_data, product_data)
        
        message = AIMessage(content=f"Market expansion analysis complete. {len(expansion_plan['opportunities'])} opportunities identified")
        
        return {
            **state,
            "market_expansion_plan": expansion_plan,
            "messages": state.get("messages", []) + [message]
        }
    
    async def roi_calculator_node(self, state: RevenueInsightsState) -> RevenueInsightsState:
        """
        Calculate ROI projections for optimization strategies
        """
        logger.info("ROI Calculator activated")
        
        onboarding_insights = state.get("onboarding_insights", {})
        product_insights = state.get("product_insights", {})
        pricing_recommendations = state.get("pricing_recommendations", {})
        
        # Calculate comprehensive ROI projections
        roi_projections = await self._calculate_roi_projections(
            onboarding_insights, product_insights, pricing_recommendations
        )
        
        total_revenue_impact = roi_projections.get("total_annual_impact", 0)
        message = AIMessage(content=f"ROI calculations complete. Projected annual revenue impact: ₹{total_revenue_impact:,.0f}")
        
        return {
            **state,
            "roi_projections": roi_projections,
            "messages": state.get("messages", []) + [message]
        }
    
    async def _analyze_farmer_value_patterns(self, farmer_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze patterns in high-value farmers for targeted onboarding
        """
        
        # Calculate farmer value scores
        farmer_scores = []
        for farmer in farmer_data:
            score = self._calculate_farmer_value_score(farmer)
            farmer_scores.append({
                "farmer": farmer,
                "value_score": score,
                "revenue_potential": score * 1000  # Convert to monthly revenue potential
            })
        
        # Sort by value score
        farmer_scores.sort(key=lambda x: x["value_score"], reverse=True)
        
        # Identify high-value segments
        high_value_segments = []
        
        # Organic certified farmers
        organic_farmers = [f for f in farmer_data if any("Organic" in cert for cert in f.get("certifications", []))]
        if organic_farmers:
            avg_revenue = np.mean([f.get("monthly_revenue", 0) for f in organic_farmers])
            high_value_segments.append({
                "segment": "organic_certified",
                "count": len(organic_farmers),
                "avg_monthly_revenue": avg_revenue,
                "characteristics": ["Organic certification", "Premium pricing", "Health-conscious market"],
                "onboarding_priority": "high",
                "revenue_multiplier": 1.3
            })
        
        # Multi-product farmers
        multi_product_farmers = [f for f in farmer_data if len(f.get("products", [])) >= 3]
        if multi_product_farmers:
            avg_revenue = np.mean([f.get("monthly_revenue", 0) for f in multi_product_farmers])
            high_value_segments.append({
                "segment": "diversified_portfolio",
                "count": len(multi_product_farmers),
                "avg_monthly_revenue": avg_revenue,
                "characteristics": ["Multiple products", "Year-round supply", "Risk diversification"],
                "onboarding_priority": "high", 
                "revenue_multiplier": 1.25
            })
        
        # High-rating farmers
        high_rating_farmers = [f for f in farmer_data if f.get("rating", 0) >= 4.5]
        if high_rating_farmers:
            avg_revenue = np.mean([f.get("monthly_revenue", 0) for f in high_rating_farmers])
            high_value_segments.append({
                "segment": "premium_quality",
                "count": len(high_rating_farmers),
                "avg_monthly_revenue": avg_revenue,
                "characteristics": ["High customer ratings", "Quality consistency", "Brand reputation"],
                "onboarding_priority": "medium",
                "revenue_multiplier": 1.15
            })
        
        # Onboarding recommendations
        onboarding_strategies = [
            {
                "strategy": "Organic Certification Incentive Program",
                "target_segment": "organic_certified",
                "investment": "₹2L/month",
                "expected_farmers": 50,
                "revenue_impact": "₹15L/month additional",
                "payback_period": "4 months"
            },
            {
                "strategy": "Diversification Support Program", 
                "target_segment": "single_product_farmers",
                "investment": "₹3L/month",
                "expected_farmers": 75,
                "revenue_impact": "₹22L/month additional",
                "payback_period": "5 months"
            },
            {
                "strategy": "Quality Excellence Program",
                "target_segment": "medium_quality_farmers",
                "investment": "₹1.5L/month",
                "expected_farmers": 100,
                "revenue_impact": "₹12L/month additional",
                "payback_period": "3 months"
            }
        ]
        
        return {
            "high_value_segments": high_value_segments,
            "farmer_value_scores": farmer_scores[:5],  # Top 5
            "onboarding_strategies": onboarding_strategies,
            "key_insights": [
                f"Organic farmers generate {1.3}x more revenue on average",
                f"Multi-product farmers have {1.25}x higher retention rates",
                f"High-rating farmers command {1.15}x premium pricing"
            ]
        }
    
    async def _optimize_product_portfolio(self, product_data: List[Dict[str, Any]], 
                                         farmer_insights: Dict[str, Any]) -> Dict[str, Any]:
        """
        Optimize product mix for maximum revenue
        """
        
        # Analyze current product performance
        product_analysis = []
        for product in product_data:
            monthly_revenue = product.get("monthly_sales", 0) * product.get("price", 0)
            profit_margin = product.get("profit_margin", 0.15)
            monthly_profit = monthly_revenue * profit_margin
            
            # Calculate product score
            score = (
                monthly_profit * 0.4 +                      # 40% weight on profit
                product.get("demand_growth", 1.0) * 20 +    # 20% weight on growth  
                (1.3 if product.get("organic_certified") else 1.0) * 15 +  # 15% organic bonus
                product.get("rating", 4.0) * 5              # 5% rating impact
            )
            
            product_analysis.append({
                "product": product,
                "monthly_revenue": monthly_revenue,
                "monthly_profit": monthly_profit,
                "score": score,
                "category": product.get("category", "unknown")
            })
        
        # Sort by score
        product_analysis.sort(key=lambda x: x["score"], reverse=True)
        
        # Category performance analysis
        category_performance = {}
        for analysis in product_analysis:
            category = analysis["category"]
            if category not in category_performance:
                category_performance[category] = {
                    "total_revenue": 0,
                    "total_profit": 0,
                    "product_count": 0,
                    "avg_margin": 0
                }
            
            category_performance[category]["total_revenue"] += analysis["monthly_revenue"]
            category_performance[category]["total_profit"] += analysis["monthly_profit"]
            category_performance[category]["product_count"] += 1
        
        # Calculate averages
        for category in category_performance:
            count = category_performance[category]["product_count"]
            category_performance[category]["avg_revenue"] = category_performance[category]["total_revenue"] / count
            category_performance[category]["avg_profit"] = category_performance[category]["total_profit"] / count
        
        # Product optimization recommendations
        recommendations = [
            {
                "type": "expand_high_performers",
                "description": "Scale top-performing organic vegetables",
                "target_products": [p["product"]["name"] for p in product_analysis[:3]],
                "investment": "₹5L",
                "revenue_impact": "₹18L/month",
                "timeline": "2 months"
            },
            {
                "type": "introduce_premium_category",
                "description": "Add exotic fruits and premium vegetables",
                "target_products": ["Dragon Fruit", "Avocados", "Bell Peppers"],
                "investment": "₹8L", 
                "revenue_impact": "₹25L/month",
                "timeline": "3 months"
            },
            {
                "type": "seasonal_optimization",
                "description": "Align product launches with seasonal demand peaks",
                "target_products": ["Summer fruits", "Winter vegetables"],
                "investment": "₹3L",
                "revenue_impact": "₹12L/month",
                "timeline": "Ongoing"
            }
        ]
        
        return {
            "product_performance": product_analysis,
            "category_analysis": category_performance,
            "recommendations": recommendations,
            "optimization_score": sum(p["score"] for p in product_analysis) / len(product_analysis)
        }
    
    async def _develop_pricing_strategy(self, product_data: List[Dict[str, Any]], 
                                       market_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Develop dynamic pricing strategies
        """
        
        pricing_strategies = []
        
        # Premium pricing for organic products
        organic_products = [p for p in product_data if p.get("organic_certified", False)]
        if organic_products:
            strategies.append({
                "strategy": "Organic Premium Strategy",
                "target_products": len(organic_products),
                "price_adjustment": "+30%",
                "rationale": "Health-conscious consumers willing to pay premium",
                "expected_revenue_lift": "25-35%",
                "market_acceptance": "high"
            })
        
        # Dynamic seasonal pricing
        pricing_strategies.append({
            "strategy": "Seasonal Dynamic Pricing",
            "description": "Adjust prices based on seasonal demand patterns",
            "summer_adjustments": {"mangoes": "+80%", "vegetables": "-10%"},
            "winter_adjustments": {"citrus": "+50%", "leafy_greens": "+40%"},
            "expected_revenue_lift": "15-20%",
            "implementation": "automated"
        })
        
        # Bundle pricing strategy
        pricing_strategies.append({
            "strategy": "Product Bundling",
            "description": "Create attractive product bundles",
            "bundles": [
                {"name": "Organic Vegetable Box", "products": ["Tomatoes", "Onions", "Spinach"], "discount": "15%"},
                {"name": "Seasonal Fruit Box", "products": ["Mangoes", "Oranges", "Grapes"], "discount": "20%"},
                {"name": "Farmer's Choice", "products": ["Mixed selection"], "discount": "25%"}
            ],
            "expected_revenue_lift": "30-40%",
            "average_order_value_increase": "60%"
        })
        
        # Geographic pricing optimization
        pricing_strategies.append({
            "strategy": "Geographic Price Optimization",
            "description": "Optimize prices by delivery location",
            "urban_premium": "+20%",
            "suburban_standard": "base price",
            "rural_discount": "-10%",
            "delivery_cost_factor": "included",
            "expected_revenue_lift": "12-18%"
        })
        
        return {
            "strategies": pricing_strategies,
            "total_revenue_impact": "35-50%",
            "implementation_priority": ["Seasonal Dynamic", "Organic Premium", "Bundling", "Geographic"],
            "monitoring_metrics": ["price_elasticity", "conversion_rate", "average_order_value", "customer_satisfaction"]
        }
    
    async def _identify_expansion_opportunities(self, farmer_data: List[Dict[str, Any]], 
                                              product_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Identify market expansion opportunities
        """
        
        expansion_opportunities = [
            {
                "opportunity": "Geographic Expansion - Tier 2 Cities",
                "target_markets": ["Indore", "Nagpur", "Surat", "Vadodara"],
                "farmer_potential": 500,
                "revenue_potential": "₹5Cr/month",
                "investment_required": "₹2Cr",
                "timeline": "6 months",
                "key_success_factors": ["Local partnerships", "Supply chain setup", "Marketing"]
            },
            {
                "opportunity": "B2B Restaurant Supply",
                "target_customers": ["Restaurant chains", "Hotels", "Catering companies"],
                "market_size": "₹15Cr addressable",
                "farmer_benefits": "Bulk orders, predictable demand",
                "revenue_potential": "₹3Cr/month", 
                "investment_required": "₹1.5Cr",
                "timeline": "4 months"
            },
            {
                "opportunity": "Corporate Cafeteria Supply",
                "target_customers": ["IT companies", "Manufacturing units", "Hospitals"],
                "market_size": "₹8Cr addressable",
                "value_proposition": "Fresh, healthy, traceable food",
                "revenue_potential": "₹2Cr/month",
                "investment_required": "₹1Cr",
                "timeline": "3 months"
            },
            {
                "opportunity": "Export Market - Middle East",
                "target_products": ["Organic spices", "Basmati rice", "Fruits"],
                "market_size": "$50M addressable",
                "regulatory_requirements": ["Export licenses", "Quality certifications"],
                "revenue_potential": "₹4Cr/month",
                "investment_required": "₹3Cr",
                "timeline": "12 months"
            }
        ]
        
        # Prioritize opportunities by ROI
        for opp in expansion_opportunities:
            revenue_annual = float(opp["revenue_potential"].replace("₹", "").replace("Cr/month", "")) * 12
            investment = float(opp["investment_required"].replace("₹", "").replace("Cr", ""))
            opp["roi"] = revenue_annual / investment if investment > 0 else 0
            
            # Risk assessment
            if "export" in opp["opportunity"].lower():
                opp["risk_level"] = "high"
            elif "b2b" in opp["opportunity"].lower():
                opp["risk_level"] = "medium"
            else:
                opp["risk_level"] = "low"
        
        # Sort by ROI
        expansion_opportunities.sort(key=lambda x: x["roi"], reverse=True)
        
        return {
            "opportunities": expansion_opportunities,
            "total_addressable_market": "₹32Cr/month",
            "recommended_sequence": [opp["opportunity"] for opp in expansion_opportunities[:3]],
            "total_investment_needed": "₹7.5Cr",
            "payback_period": "18 months average"
        }
    
    def _calculate_farmer_value_score(self, farmer: Dict[str, Any]) -> float:
        """Calculate value score for a farmer"""
        
        score = 50  # Base score
        
        # Organic certification bonus
        certifications = farmer.get("certifications", [])
        if any("Organic" in cert for cert in certifications):
            score += 20
        
        # Rating bonus
        rating = farmer.get("rating", 4.0)
        if rating >= 4.5:
            score += 15
        elif rating >= 4.0:
            score += 10
        
        # Product diversity bonus
        products_count = len(farmer.get("products", []))
        score += min(products_count * 5, 20)  # Max 20 points
        
        # Delivery radius bonus
        radius = farmer.get("delivery_radius", "25 km")
        if "100" in radius:
            score += 15
        elif "50" in radius:
            score += 10
        
        # Revenue history bonus
        monthly_revenue = farmer.get("monthly_revenue", 30000)
        if monthly_revenue >= 60000:
            score += 20
        elif monthly_revenue >= 45000:
            score += 15
        elif monthly_revenue >= 30000:
            score += 10
        
        return min(score, 100)  # Cap at 100
    
    async def _calculate_roi_projections(self, onboarding_insights: Dict[str, Any],
                                        product_insights: Dict[str, Any],
                                        pricing_recommendations: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate comprehensive ROI projections
        """
        
        # Base revenue assumptions
        current_monthly_gmv = 50_00_000  # ₹50L current GMV
        current_commission = 0.08        # 8% commission rate
        current_monthly_revenue = current_monthly_gmv * current_commission  # ₹4L
        
        # Revenue impact from strategies
        farmer_onboarding_impact = 0.35   # 35% increase from better farmer onboarding
        product_optimization_impact = 0.25 # 25% increase from product portfolio optimization  
        pricing_strategy_impact = 0.20    # 20% increase from dynamic pricing
        
        # Calculate projections
        month_1_revenue = current_monthly_revenue * (1 + farmer_onboarding_impact * 0.3)  # 30% of impact in month 1
        month_3_revenue = current_monthly_revenue * (1 + farmer_onboarding_impact * 0.7 + product_optimization_impact * 0.4)
        month_6_revenue = current_monthly_revenue * (1 + farmer_onboarding_impact + product_optimization_impact * 0.8 + pricing_strategy_impact * 0.5)
        month_12_revenue = current_monthly_revenue * (1 + farmer_onboarding_impact + product_optimization_impact + pricing_strategy_impact)
        
        # Investment requirements
        total_investment = 15_00_000  # ₹15L total investment
        onboarding_investment = 6_00_000   # ₹6L for farmer onboarding programs
        product_investment = 5_00_000      # ₹5L for product optimization
        pricing_tech_investment = 4_00_000 # ₹4L for pricing technology
        
        annual_revenue_lift = (month_12_revenue - current_monthly_revenue) * 12
        roi = (annual_revenue_lift - total_investment) / total_investment
        payback_months = total_investment / (month_12_revenue - current_monthly_revenue)
        
        return {
            "current_monthly_revenue": current_monthly_revenue,
            "projected_monthly_revenue": {
                "month_1": int(month_1_revenue),
                "month_3": int(month_3_revenue), 
                "month_6": int(month_6_revenue),
                "month_12": int(month_12_revenue)
            },
            "total_annual_impact": int(annual_revenue_lift),
            "investment_breakdown": {
                "farmer_onboarding": onboarding_investment,
                "product_optimization": product_investment,
                "pricing_technology": pricing_tech_investment,
                "total": total_investment
            },
            "roi_metrics": {
                "annual_roi": f"{roi:.1%}",
                "payback_period_months": f"{payback_months:.1f}",
                "net_profit_year_1": int(annual_revenue_lift - total_investment),
                "revenue_growth": f"{((month_12_revenue/current_monthly_revenue - 1) * 100):.0f}%"
            },
            "key_assumptions": [
                "Commission rate remains at 8%",
                "Market demand supports growth",
                "Farmer retention rate >85%",
                "No major competitor disruption"
            ]
        }
    
    async def execute(self, analysis_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute revenue insights analysis workflow
        """
        logger.info(f"Executing revenue insights analysis: {analysis_type}")
        
        # Initialize state
        initial_state = {
            "messages": [HumanMessage(content=f"Analyze revenue optimization for: {analysis_type}")],
            "analysis_type": analysis_type,
            "farmer_data": data.get("farmer_data", []),
            "product_data": data.get("product_data", []),
            "market_data": data.get("market_data", {}),
            "onboarding_insights": {},
            "product_insights": {},
            "pricing_recommendations": {},
            "revenue_opportunities": [],
            "action_plan": {},
            "roi_projections": {}
        }
        
        try:
            start_time = datetime.now()
            
            # Execute workflow
            final_state = await self.workflow.ainvoke(initial_state)
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Prepare comprehensive response
            result = {
                "success": True,
                "analysis_type": analysis_type,
                "execution_time": execution_time,
                "onboarding_insights": final_state.get("onboarding_insights", {}),
                "product_insights": final_state.get("product_insights", {}),
                "pricing_recommendations": final_state.get("pricing_recommendations", {}),
                "market_expansion_plan": final_state.get("market_expansion_plan", {}),
                "roi_projections": final_state.get("roi_projections", {}),
                "messages": [msg.content for msg in final_state.get("messages", [])]
            }
            
            logger.info(f"Revenue insights analysis completed in {execution_time:.2f} seconds")
            return result
            
        except Exception as e:
            logger.error(f"Revenue insights analysis failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "analysis_type": analysis_type
            }

# Example usage
async def main():
    """Example usage of the revenue insights agent"""
    
    revenue_agent = RevenueInsightsAgent()
    
    # Test comprehensive revenue analysis
    analysis_data = {
        "farmer_data": [
            {
                "id": 1, "name": "Rajesh Kumar", "location": "Pune Rural",
                "products": ["Tomatoes", "Cucumbers", "Spinach"],
                "rating": 4.8, "delivery_radius": "50 km",
                "certifications": ["Organic Certified", "GAP Certified"],
                "monthly_revenue": 45000, "join_date": "2024-01-15"
            }
        ],
        "product_data": [
            {
                "id": 1, "name": "Fresh Tomatoes", "category": "Vegetables",
                "price": 35, "unit": "kg", "farmer_name": "Rajesh Kumar",
                "organic_certified": True, "monthly_sales": 1200,
                "profit_margin": 0.18, "demand_growth": 1.3
            }
        ],
        "market_data": {
            "season": "summer",
            "competition_level": "high",
            "consumer_trends": ["organic", "local", "sustainable"]
        }
    }
    
    result = await revenue_agent.execute("farmer_onboarding", analysis_data)
    print("Revenue Insights Result:", json.dumps(result, indent=2, default=str))

if __name__ == "__main__":
    asyncio.run(main())