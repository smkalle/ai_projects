"""
FarmConnect Farmer Onboarding Scoring Agent - LangGraph Implementation
AI-powered farmer evaluation and onboarding optimization system
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
class FarmerScore:
    """Farmer onboarding score with detailed breakdown"""
    farmer_id: str
    overall_score: float
    category_scores: Dict[str, float]
    revenue_potential: float
    priority_level: str
    onboarding_recommendations: List[str]
    risk_factors: List[str]
    expected_monthly_revenue: float

class FarmerScoringState(TypedDict):
    """State for farmer scoring workflow"""
    messages: Annotated[Sequence[BaseMessage], operator.add]
    farmer_data: Dict[str, Any]
    location_analysis: Dict[str, Any]
    product_evaluation: Dict[str, Any]
    certification_assessment: Dict[str, Any]
    market_fit_analysis: Dict[str, Any]
    financial_projection: Dict[str, Any]
    final_score: Dict[str, Any]
    onboarding_plan: Dict[str, Any]

class FarmerScoringAgent:
    """
    LangGraph-based Farmer Scoring Agent for FarmConnect
    Evaluates farmers for onboarding with comprehensive scoring
    """
    
    def __init__(self):
        """Initialize the farmer scoring agent"""
        
        # Get API key from environment
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OpenAI API key not found in environment")
        
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0,
            api_key=api_key
        )
        
        # Scoring criteria and weights
        self.scoring_criteria = {
            "location_factors": {
                "weight": 0.20,
                "criteria": {
                    "proximity_to_urban": {"max_score": 25, "metro_cities": 25, "tier_2": 20, "tier_3": 15, "rural": 10},
                    "logistics_access": {"max_score": 15, "highway_access": 15, "good_roads": 12, "poor_access": 5},
                    "climate_suitability": {"max_score": 10, "optimal": 10, "good": 8, "average": 5}
                }
            },
            "product_portfolio": {
                "weight": 0.25,
                "criteria": {
                    "product_diversity": {"max_score": 20, "5_plus": 20, "3_to_4": 15, "2_products": 10, "single": 5},
                    "demand_alignment": {"max_score": 15, "high_demand": 15, "medium": 10, "low": 5},
                    "seasonal_spread": {"max_score": 15, "year_round": 15, "multi_season": 10, "single_season": 5}
                }
            },
            "quality_credentials": {
                "weight": 0.25,
                "criteria": {
                    "organic_certification": {"max_score": 25, "certified": 25, "in_process": 15, "none": 0},
                    "other_certifications": {"max_score": 15, "multiple": 15, "single": 10, "none": 0},
                    "quality_history": {"max_score": 10, "excellent": 10, "good": 7, "average": 4}
                }
            },
            "operational_capacity": {
                "weight": 0.15,
                "criteria": {
                    "production_scale": {"max_score": 15, "large": 15, "medium": 10, "small": 6},
                    "technology_adoption": {"max_score": 10, "advanced": 10, "basic": 6, "traditional": 3},
                    "delivery_capability": {"max_score": 10, "own_transport": 10, "third_party": 7, "pickup_only": 3}
                }
            },
            "financial_profile": {
                "weight": 0.15,
                "criteria": {
                    "revenue_history": {"max_score": 15, "high": 15, "medium": 10, "low": 5},
                    "payment_reliability": {"max_score": 10, "excellent": 10, "good": 7, "poor": 3},
                    "investment_capacity": {"max_score": 10, "high": 10, "medium": 6, "low": 3}
                }
            }
        }
        
        # Market demand data
        self.market_demand = {
            "vegetables": {"demand_score": 0.8, "price_premium": 1.1, "competition": "high"},
            "fruits": {"demand_score": 0.9, "price_premium": 1.3, "competition": "medium"},
            "grains": {"demand_score": 0.6, "price_premium": 1.0, "competition": "high"},
            "dairy": {"demand_score": 0.95, "price_premium": 1.4, "competition": "low"},
            "organic": {"demand_score": 1.0, "price_premium": 1.5, "competition": "low"},
            "exotic": {"demand_score": 0.85, "price_premium": 1.8, "competition": "very_low"}
        }
        
        # Geographic scoring
        self.location_scores = {
            "mumbai": {"urban_proximity": 25, "logistics": 15, "market_access": 20},
            "pune": {"urban_proximity": 22, "logistics": 14, "market_access": 18},
            "bangalore": {"urban_proximity": 23, "logistics": 13, "market_access": 19},
            "delhi": {"urban_proximity": 25, "logistics": 15, "market_access": 20},
            "hyderabad": {"urban_proximity": 20, "logistics": 12, "market_access": 16},
            "tier_2": {"urban_proximity": 15, "logistics": 10, "market_access": 12},
            "rural": {"urban_proximity": 8, "logistics": 6, "market_access": 8}
        }
        
        # Create workflow
        self.workflow = self._create_workflow()
        
        logger.info("FarmerScoringAgent initialized for comprehensive onboarding evaluation")
    
    def _create_workflow(self) -> StateGraph:
        """Create the LangGraph workflow for farmer scoring"""
        
        # Initialize the graph
        workflow = StateGraph(FarmerScoringState)
        
        # Add nodes for scoring analysis
        workflow.add_node("location_analyzer", self.location_analyzer_node)
        workflow.add_node("product_evaluator", self.product_evaluator_node)
        workflow.add_node("certification_assessor", self.certification_assessor_node)
        workflow.add_node("market_fit_analyzer", self.market_fit_analyzer_node)
        workflow.add_node("financial_projector", self.financial_projector_node)
        workflow.add_node("score_calculator", self.score_calculator_node)
        workflow.add_node("onboarding_planner", self.onboarding_planner_node)
        
        # Set entry point and create chain
        workflow.set_entry_point("location_analyzer")
        workflow.add_edge("location_analyzer", "product_evaluator")
        workflow.add_edge("product_evaluator", "certification_assessor")
        workflow.add_edge("certification_assessor", "market_fit_analyzer")
        workflow.add_edge("market_fit_analyzer", "financial_projector")
        workflow.add_edge("financial_projector", "score_calculator")
        workflow.add_edge("score_calculator", "onboarding_planner")
        workflow.add_edge("onboarding_planner", END)
        
        return workflow.compile()
    
    async def location_analyzer_node(self, state: FarmerScoringState) -> FarmerScoringState:
        """Analyze farmer location factors"""
        logger.info("Location Analyzer activated")
        
        farmer_data = state.get("farmer_data", {})
        location = farmer_data.get("location", "").lower()
        
        # Analyze location factors
        location_analysis = await self._analyze_location_factors(farmer_data)
        
        message = AIMessage(content=f"Location analysis complete for {location}. Proximity score: {location_analysis['total_score']}")
        
        return {
            **state,
            "location_analysis": location_analysis,
            "messages": state.get("messages", []) + [message]
        }
    
    async def product_evaluator_node(self, state: FarmerScoringState) -> FarmerScoringState:
        """Evaluate farmer's product portfolio"""
        logger.info("Product Evaluator activated")
        
        farmer_data = state.get("farmer_data", {})
        
        # Evaluate product portfolio
        product_evaluation = await self._evaluate_product_portfolio(farmer_data)
        
        message = AIMessage(content=f"Product evaluation complete. Portfolio diversity: {product_evaluation['diversity_score']}")
        
        return {
            **state,
            "product_evaluation": product_evaluation,
            "messages": state.get("messages", []) + [message]
        }
    
    async def certification_assessor_node(self, state: FarmerScoringState) -> FarmerScoringState:
        """Assess farmer certifications and quality credentials"""
        logger.info("Certification Assessor activated")
        
        farmer_data = state.get("farmer_data", {})
        
        # Assess certifications
        certification_assessment = await self._assess_certifications(farmer_data)
        
        message = AIMessage(content=f"Certification assessment complete. Quality score: {certification_assessment['total_score']}")
        
        return {
            **state,
            "certification_assessment": certification_assessment,
            "messages": state.get("messages", []) + [message]
        }
    
    async def market_fit_analyzer_node(self, state: FarmerScoringState) -> FarmerScoringState:
        """Analyze market fit and demand alignment"""
        logger.info("Market Fit Analyzer activated")
        
        farmer_data = state.get("farmer_data", {})
        product_evaluation = state.get("product_evaluation", {})
        
        # Analyze market fit
        market_fit_analysis = await self._analyze_market_fit(farmer_data, product_evaluation)
        
        message = AIMessage(content=f"Market fit analysis complete. Demand alignment: {market_fit_analysis['demand_score']}")
        
        return {
            **state,
            "market_fit_analysis": market_fit_analysis,
            "messages": state.get("messages", []) + [message]
        }
    
    async def financial_projector_node(self, state: FarmerScoringState) -> FarmerScoringState:
        """Project financial potential and revenue estimates"""
        logger.info("Financial Projector activated")
        
        farmer_data = state.get("farmer_data", {})
        location_analysis = state.get("location_analysis", {})
        product_evaluation = state.get("product_evaluation", {})
        market_fit_analysis = state.get("market_fit_analysis", {})
        
        # Project financial potential
        financial_projection = await self._project_financial_potential(
            farmer_data, location_analysis, product_evaluation, market_fit_analysis
        )
        
        expected_revenue = financial_projection.get("monthly_revenue_projection", 0)
        message = AIMessage(content=f"Financial projection complete. Expected monthly revenue: ₹{expected_revenue:,.0f}")
        
        return {
            **state,
            "financial_projection": financial_projection,
            "messages": state.get("messages", []) + [message]
        }
    
    async def score_calculator_node(self, state: FarmerScoringState) -> FarmerScoringState:
        """Calculate final farmer score"""
        logger.info("Score Calculator activated")
        
        # Gather all analysis results
        location_analysis = state.get("location_analysis", {})
        product_evaluation = state.get("product_evaluation", {})
        certification_assessment = state.get("certification_assessment", {})
        market_fit_analysis = state.get("market_fit_analysis", {})
        financial_projection = state.get("financial_projection", {})
        
        # Calculate comprehensive score
        final_score = await self._calculate_comprehensive_score(
            location_analysis, product_evaluation, certification_assessment, 
            market_fit_analysis, financial_projection
        )
        
        score = final_score.get("overall_score", 0)
        message = AIMessage(content=f"Final scoring complete. Overall farmer score: {score}/100")
        
        return {
            **state,
            "final_score": final_score,
            "messages": state.get("messages", []) + [message]
        }
    
    async def onboarding_planner_node(self, state: FarmerScoringState) -> FarmerScoringState:
        """Create personalized onboarding plan"""
        logger.info("Onboarding Planner activated")
        
        farmer_data = state.get("farmer_data", {})
        final_score = state.get("final_score", {})
        
        # Create onboarding plan
        onboarding_plan = await self._create_onboarding_plan(farmer_data, final_score)
        
        plan_items = len(onboarding_plan.get("action_items", []))
        message = AIMessage(content=f"Onboarding plan created with {plan_items} action items")
        
        return {
            **state,
            "onboarding_plan": onboarding_plan,
            "messages": state.get("messages", []) + [message]
        }
    
    async def _analyze_location_factors(self, farmer_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze farmer location factors"""
        
        location = farmer_data.get("location", "").lower()
        state = farmer_data.get("state", "").lower()
        
        # Determine location category
        location_category = "rural"  # default
        if any(city in location for city in ["mumbai", "delhi", "bangalore", "pune", "hyderabad"]):
            for city in ["mumbai", "delhi", "bangalore", "pune", "hyderabad"]:
                if city in location:
                    location_category = city
                    break
        elif any(tier2 in location for tier2 in ["nashik", "aurangabad", "surat", "indore", "nagpur"]):
            location_category = "tier_2"
        
        # Get location scores
        location_scores = self.location_scores.get(location_category, self.location_scores["rural"])
        
        # Climate analysis
        climate_score = 8  # Default good climate
        if state in ["maharashtra", "punjab", "karnataka"]:
            climate_score = 10
        elif state in ["rajasthan", "gujarat"]:
            climate_score = 6
        
        total_score = (
            location_scores["urban_proximity"] + 
            location_scores["logistics"] + 
            location_scores["market_access"] + 
            climate_score
        )
        
        return {
            "location_category": location_category,
            "urban_proximity_score": location_scores["urban_proximity"],
            "logistics_score": location_scores["logistics"],
            "market_access_score": location_scores["market_access"],
            "climate_score": climate_score,
            "total_score": total_score,
            "max_possible": 70,
            "percentage": (total_score / 70) * 100,
            "strengths": [
                "Good urban proximity" if location_scores["urban_proximity"] >= 20 else "",
                "Excellent logistics" if location_scores["logistics"] >= 12 else "",
                "Strong market access" if location_scores["market_access"] >= 15 else ""
            ],
            "improvement_areas": [
                "Consider proximity partnerships" if location_scores["urban_proximity"] < 15 else "",
                "Improve logistics connections" if location_scores["logistics"] < 10 else ""
            ]
        }
    
    async def _evaluate_product_portfolio(self, farmer_data: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate farmer's product portfolio"""
        
        products = farmer_data.get("products", [])
        
        # Analyze product diversity
        diversity_score = min(len(products) * 4, 20)  # Max 20 for 5+ products
        
        # Categorize products
        product_categories = {}
        seasonal_spread = set()
        
        for product in products:
            product_lower = product.lower()
            
            # Categorize product
            if any(veg in product_lower for veg in ["tomato", "onion", "potato", "spinach", "carrot"]):
                category = "vegetables"
                seasonal_spread.add("year_round")
            elif any(fruit in product_lower for fruit in ["mango", "orange", "grape", "apple"]):
                category = "fruits"
                if "mango" in product_lower:
                    seasonal_spread.add("summer")
                elif "orange" in product_lower:
                    seasonal_spread.add("winter")
            elif any(grain in product_lower for grain in ["rice", "wheat", "jowar"]):
                category = "grains"
                seasonal_spread.add("harvest")
            else:
                category = "other"
            
            product_categories[category] = product_categories.get(category, 0) + 1
        
        # Calculate demand alignment
        demand_scores = []
        for product in products:
            product_lower = product.lower()
            if "organic" in product_lower or farmer_data.get("organic_certified", False):
                demand_scores.append(self.market_demand["organic"]["demand_score"])
            elif any(fruit in product_lower for fruit in ["mango", "grape", "orange"]):
                demand_scores.append(self.market_demand["fruits"]["demand_score"])
            else:
                demand_scores.append(self.market_demand["vegetables"]["demand_score"])
        
        avg_demand_score = np.mean(demand_scores) if demand_scores else 0.5
        demand_alignment_score = avg_demand_score * 15  # Max 15 points
        
        # Seasonal spread analysis
        seasonal_score = len(seasonal_spread) * 5  # 5 points per season
        seasonal_score = min(seasonal_score, 15)  # Max 15
        
        total_portfolio_score = diversity_score + demand_alignment_score + seasonal_score
        
        return {
            "products": products,
            "product_count": len(products),
            "diversity_score": diversity_score,
            "demand_alignment_score": demand_alignment_score,
            "seasonal_score": seasonal_score,
            "total_score": total_portfolio_score,
            "max_possible": 50,
            "percentage": (total_portfolio_score / 50) * 100,
            "categories": product_categories,
            "seasonal_spread": list(seasonal_spread),
            "strengths": [
                "Excellent product diversity" if len(products) >= 4 else "",
                "High demand products" if avg_demand_score >= 0.8 else "",
                "Good seasonal coverage" if len(seasonal_spread) >= 2 else ""
            ],
            "recommendations": [
                "Add seasonal products" if len(seasonal_spread) < 2 else "",
                "Focus on high-demand categories" if avg_demand_score < 0.7 else "",
                "Consider organic certification" if not farmer_data.get("organic_certified") else ""
            ]
        }
    
    async def _assess_certifications(self, farmer_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess farmer certifications and quality credentials"""
        
        certifications = farmer_data.get("certifications", [])
        rating = farmer_data.get("rating", 4.0)
        
        # Organic certification scoring
        organic_score = 0
        if any("organic" in cert.lower() for cert in certifications):
            organic_score = 25
        elif farmer_data.get("organic_in_process", False):
            organic_score = 15
        
        # Other certifications scoring
        other_cert_score = 0
        non_organic_certs = [cert for cert in certifications if "organic" not in cert.lower()]
        if len(non_organic_certs) >= 2:
            other_cert_score = 15
        elif len(non_organic_certs) == 1:
            other_cert_score = 10
        
        # Quality history scoring based on rating
        if rating >= 4.7:
            quality_score = 10
        elif rating >= 4.3:
            quality_score = 7
        else:
            quality_score = 4
        
        total_quality_score = organic_score + other_cert_score + quality_score
        
        return {
            "certifications": certifications,
            "rating": rating,
            "organic_score": organic_score,
            "other_certifications_score": other_cert_score,
            "quality_history_score": quality_score,
            "total_score": total_quality_score,
            "max_possible": 50,
            "percentage": (total_quality_score / 50) * 100,
            "certification_status": "excellent" if total_quality_score >= 40 else "good" if total_quality_score >= 25 else "basic",
            "strengths": [
                "Organic certified" if organic_score == 25 else "",
                "Multiple certifications" if other_cert_score >= 10 else "",
                "Excellent quality track record" if quality_score >= 9 else ""
            ],
            "recommendations": [
                "Pursue organic certification" if organic_score == 0 else "",
                "Obtain additional certifications" if other_cert_score < 10 else "",
                "Focus on quality improvement" if quality_score < 7 else ""
            ]
        }
    
    async def _analyze_market_fit(self, farmer_data: Dict[str, Any], 
                                 product_evaluation: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze market fit and demand alignment"""
        
        products = farmer_data.get("products", [])
        location = farmer_data.get("location", "").lower()
        
        # Market demand analysis
        market_scores = []
        premium_potential = []
        
        for product in products:
            product_lower = product.lower()
            
            # Check for high-demand categories
            if "organic" in product_lower or farmer_data.get("organic_certified", False):
                market_scores.append(1.0)
                premium_potential.append(1.5)
            elif any(exotic in product_lower for exotic in ["dragon", "avocado", "kiwi"]):
                market_scores.append(0.9)
                premium_potential.append(1.8)
            elif any(fruit in product_lower for fruit in ["mango", "grape"]):
                market_scores.append(0.8)
                premium_potential.append(1.3)
            else:
                market_scores.append(0.6)
                premium_potential.append(1.1)
        
        avg_market_score = np.mean(market_scores) if market_scores else 0.6
        avg_premium = np.mean(premium_potential) if premium_potential else 1.0
        
        # Competition analysis
        competition_level = "medium"
        if avg_market_score >= 0.9:
            competition_level = "low"
        elif avg_market_score <= 0.6:
            competition_level = "high"
        
        # Geographic market fit
        geo_multiplier = 1.0
        if any(metro in location for metro in ["mumbai", "delhi", "bangalore"]):
            geo_multiplier = 1.2
        elif "tier_2" in location or any(tier2 in location for tier2 in ["pune", "nashik"]):
            geo_multiplier = 1.1
        
        demand_score = avg_market_score * geo_multiplier * 30  # Max 30 points
        
        return {
            "demand_score": min(demand_score, 30),
            "market_scores": market_scores,
            "premium_potential": avg_premium,
            "competition_level": competition_level,
            "geographic_multiplier": geo_multiplier,
            "max_possible": 30,
            "percentage": (min(demand_score, 30) / 30) * 100,
            "market_positioning": "premium" if avg_premium >= 1.4 else "mid-market" if avg_premium >= 1.2 else "standard",
            "strengths": [
                "High market demand products" if avg_market_score >= 0.8 else "",
                "Premium pricing potential" if avg_premium >= 1.4 else "",
                "Low competition environment" if competition_level == "low" else ""
            ],
            "opportunities": [
                "Expand premium product line" if avg_premium < 1.3 else "",
                "Target urban markets" if geo_multiplier < 1.2 else "",
                "Leverage low competition" if competition_level == "low" else ""
            ]
        }
    
    async def _project_financial_potential(self, farmer_data: Dict[str, Any],
                                          location_analysis: Dict[str, Any],
                                          product_evaluation: Dict[str, Any],
                                          market_fit_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Project financial potential and revenue estimates"""
        
        # Base revenue calculation
        base_monthly_revenue = 35000  # Base farmer revenue
        
        # Apply multipliers based on analysis
        location_multiplier = 1 + (location_analysis.get("percentage", 50) / 100 * 0.3)
        product_multiplier = 1 + (product_evaluation.get("percentage", 50) / 100 * 0.4) 
        market_multiplier = market_fit_analysis.get("premium_potential", 1.0)
        
        # Quality and certification bonus
        quality_bonus = 1.0
        if farmer_data.get("organic_certified", False):
            quality_bonus += 0.3
        
        rating = farmer_data.get("rating", 4.0)
        if rating >= 4.5:
            quality_bonus += 0.15
        
        # Calculate projected revenue
        monthly_revenue_projection = (
            base_monthly_revenue * 
            location_multiplier * 
            product_multiplier * 
            market_multiplier * 
            quality_bonus
        )
        
        # Commission and platform revenue
        commission_rate = 0.08  # 8% commission
        monthly_platform_revenue = monthly_revenue_projection * commission_rate
        
        # Growth projections
        month_6_revenue = monthly_revenue_projection * 1.2
        month_12_revenue = monthly_revenue_projection * 1.5
        
        # Risk assessment
        risk_factors = []
        risk_score = 0
        
        if location_analysis.get("percentage", 50) < 40:
            risk_factors.append("Remote location challenges")
            risk_score += 15
        
        if product_evaluation.get("product_count", 0) < 2:
            risk_factors.append("Limited product diversity")
            risk_score += 20
        
        if farmer_data.get("rating", 4.0) < 4.0:
            risk_factors.append("Quality consistency concerns")
            risk_score += 25
        
        return {
            "monthly_revenue_projection": int(monthly_revenue_projection),
            "monthly_platform_revenue": int(monthly_platform_revenue),
            "annual_revenue_projection": int(monthly_revenue_projection * 12),
            "growth_projections": {
                "month_6": int(month_6_revenue),
                "month_12": int(month_12_revenue)
            },
            "multipliers": {
                "location": round(location_multiplier, 2),
                "product": round(product_multiplier, 2), 
                "market": round(market_multiplier, 2),
                "quality": round(quality_bonus, 2)
            },
            "risk_factors": risk_factors,
            "risk_score": risk_score,
            "financial_grade": "A" if risk_score < 20 else "B" if risk_score < 40 else "C"
        }
    
    async def _calculate_comprehensive_score(self, location_analysis: Dict[str, Any],
                                           product_evaluation: Dict[str, Any],
                                           certification_assessment: Dict[str, Any],
                                           market_fit_analysis: Dict[str, Any],
                                           financial_projection: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate comprehensive farmer score"""
        
        # Weight the scores according to criteria
        location_score = location_analysis.get("percentage", 0) * 0.20
        product_score = product_evaluation.get("percentage", 0) * 0.25
        quality_score = certification_assessment.get("percentage", 0) * 0.25
        market_score = market_fit_analysis.get("percentage", 0) * 0.15
        
        # Financial scoring based on projections
        monthly_revenue = financial_projection.get("monthly_revenue_projection", 0)
        financial_score = min(monthly_revenue / 1000, 15)  # Max 15 points, scale by thousands
        
        overall_score = location_score + product_score + quality_score + market_score + financial_score
        
        # Determine priority level
        if overall_score >= 80:
            priority_level = "high"
            onboarding_priority = "immediate"
        elif overall_score >= 60:
            priority_level = "medium"
            onboarding_priority = "within_2_weeks"
        else:
            priority_level = "low"
            onboarding_priority = "evaluate_further"
        
        # Risk-adjusted score
        risk_score = financial_projection.get("risk_score", 0)
        adjusted_score = max(overall_score - (risk_score * 0.3), 0)
        
        return {
            "overall_score": round(overall_score, 1),
            "adjusted_score": round(adjusted_score, 1),
            "component_scores": {
                "location": round(location_score, 1),
                "product_portfolio": round(product_score, 1),
                "quality_credentials": round(quality_score, 1),
                "market_fit": round(market_score, 1),
                "financial_potential": round(financial_score, 1)
            },
            "priority_level": priority_level,
            "onboarding_priority": onboarding_priority,
            "grade": "A+" if adjusted_score >= 85 else "A" if adjusted_score >= 75 else "B+" if adjusted_score >= 65 else "B" if adjusted_score >= 55 else "C",
            "revenue_potential": financial_projection.get("monthly_revenue_projection", 0),
            "risk_assessment": financial_projection.get("financial_grade", "C")
        }
    
    async def _create_onboarding_plan(self, farmer_data: Dict[str, Any], 
                                     final_score: Dict[str, Any]) -> Dict[str, Any]:
        """Create personalized onboarding plan"""
        
        priority_level = final_score.get("priority_level", "low")
        overall_score = final_score.get("overall_score", 0)
        component_scores = final_score.get("component_scores", {})
        
        # Create action items based on weakest areas
        action_items = []
        
        if component_scores.get("location", 0) < 15:
            action_items.append({
                "category": "logistics",
                "action": "Establish pickup point partnerships in nearest urban center",
                "timeline": "2 weeks",
                "investment": "₹5,000"
            })
        
        if component_scores.get("quality_credentials", 0) < 20:
            action_items.append({
                "category": "certification",
                "action": "Begin organic certification process",
                "timeline": "3 months", 
                "investment": "₹15,000"
            })
        
        if component_scores.get("product_portfolio", 0) < 20:
            action_items.append({
                "category": "diversification",
                "action": "Add 2-3 complementary products to portfolio",
                "timeline": "1 month",
                "investment": "₹10,000"
            })
        
        if component_scores.get("market_fit", 0) < 12:
            action_items.append({
                "category": "market_research",
                "action": "Conduct local market demand analysis",
                "timeline": "1 week",
                "investment": "₹2,000"
            })
        
        # Support program recommendations
        support_programs = []
        
        if priority_level == "high":
            support_programs.extend([
                "Premium Farmer Fast-Track Program",
                "Quality Excellence Training",
                "Market Linkage Assistance"
            ])
        else:
            support_programs.extend([
                "Basic Farmer Training Program",
                "Digital Literacy Support"
            ])
        
        # Timeline and milestones
        timeline = {
            "week_1": "Documentation and verification",
            "week_2": "Training program enrollment",
            "month_1": "Initial product listing",
            "month_3": "Performance review",
            "month_6": "Expansion opportunities assessment"
        }
        
        return {
            "priority_level": priority_level,
            "action_items": action_items,
            "support_programs": support_programs,
            "timeline": timeline,
            "success_metrics": [
                "Monthly revenue target: ₹" + str(final_score.get("revenue_potential", 35000)),
                "Quality rating maintenance: >4.5",
                "Product diversity: 3+ categories",
                "Customer retention: >85%"
            ],
            "investment_required": sum(int(item["investment"].replace("₹", "").replace(",", "")) for item in action_items),
            "expected_roi": "3.5x within 6 months"
        }
    
    async def score_farmer(self, farmer_data: Dict[str, Any]) -> Dict[str, Any]:
        """Score a single farmer for onboarding"""
        
        logger.info(f"Scoring farmer: {farmer_data.get('name', 'Unknown')}")
        
        # Initialize state
        initial_state = {
            "messages": [HumanMessage(content=f"Score farmer: {farmer_data.get('name', 'Unknown')}")],
            "farmer_data": farmer_data,
            "location_analysis": {},
            "product_evaluation": {},
            "certification_assessment": {},
            "market_fit_analysis": {},
            "financial_projection": {},
            "final_score": {},
            "onboarding_plan": {}
        }
        
        try:
            start_time = datetime.now()
            
            # Execute workflow
            final_state = await self.workflow.ainvoke(initial_state)
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Prepare response
            result = {
                "success": True,
                "farmer_id": farmer_data.get("id", "unknown"),
                "farmer_name": farmer_data.get("name", "Unknown"),
                "execution_time": execution_time,
                "overall_score": final_state.get("final_score", {}).get("overall_score", 0),
                "priority_level": final_state.get("final_score", {}).get("priority_level", "low"),
                "revenue_potential": final_state.get("financial_projection", {}).get("monthly_revenue_projection", 0),
                "detailed_analysis": {
                    "location_analysis": final_state.get("location_analysis", {}),
                    "product_evaluation": final_state.get("product_evaluation", {}),
                    "certification_assessment": final_state.get("certification_assessment", {}),
                    "market_fit_analysis": final_state.get("market_fit_analysis", {}),
                    "financial_projection": final_state.get("financial_projection", {}),
                    "final_score": final_state.get("final_score", {}),
                    "onboarding_plan": final_state.get("onboarding_plan", {})
                },
                "messages": [msg.content for msg in final_state.get("messages", [])]
            }
            
            logger.info(f"Farmer scoring completed in {execution_time:.2f} seconds")
            return result
            
        except Exception as e:
            logger.error(f"Farmer scoring failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "farmer_id": farmer_data.get("id", "unknown")
            }

# Example usage
async def main():
    """Example usage of the farmer scoring agent"""
    
    scoring_agent = FarmerScoringAgent()
    
    # Test farmer data
    test_farmer = {
        "id": "F001",
        "name": "Rajesh Kumar",
        "location": "Pune Rural",
        "state": "Maharashtra",
        "products": ["Tomatoes", "Onions", "Spinach", "Carrots"],
        "rating": 4.7,
        "certifications": ["Organic Certified", "GAP Certified"],
        "delivery_radius": "50 km",
        "monthly_revenue": 55000,
        "organic_certified": True,
        "years_experience": 8
    }
    
    result = await scoring_agent.score_farmer(test_farmer)
    print("Farmer Scoring Result:", json.dumps(result, indent=2, default=str))

if __name__ == "__main__":
    asyncio.run(main())