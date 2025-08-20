"""
FarmConnect Quality Inspector Agent - LangGraph Implementation
AI-powered quality assessment using computer vision and ML models
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
import base64
from PIL import Image
import io
import numpy as np
from dataclasses import dataclass

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class QualityCheck:
    """Quality check result"""
    product_id: str
    grade: str  # A, B, C, Rejected
    confidence_score: float
    defects: List[str]
    freshness_score: int  # 1-10
    shelf_life_days: int
    recommendation: str
    price_adjustment: float  # Percentage

class QualityState(TypedDict):
    """State for quality inspector workflow"""
    messages: Annotated[Sequence[BaseMessage], operator.add]
    task_type: Literal["visual_inspection", "batch_assessment", "defect_analysis", "freshness_check"]
    product_images: List[str]  # Base64 encoded or file paths
    product_info: Dict[str, Any]
    quality_standards: Dict[str, Any]
    inspection_results: List[Dict[str, Any]]
    recommendations: List[str]
    batch_summary: Dict[str, Any]
    action_required: List[str]

class QualityInspectorAgent:
    """
    LangGraph-based Quality Inspector Agent for FarmConnect
    Uses AI vision and ML models for automated quality assessment
    """
    
    def __init__(self):
        """Initialize the quality inspector with AI models"""
        
        # Get API key from environment
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OpenAI API key not found in environment")
        
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0,
            api_key=api_key
        )
        
        # Quality standards for different products
        self.quality_standards = {
            "tomatoes": {
                "A_grade": {
                    "color_range": "deep_red",
                    "firmness": "firm",
                    "size": "uniform",
                    "defects": "none",
                    "shelf_life": 7,
                    "price_premium": 0
                },
                "B_grade": {
                    "color_range": "light_red_to_red",
                    "firmness": "slightly_soft",
                    "size": "mostly_uniform",
                    "defects": "minor_blemishes",
                    "shelf_life": 4,
                    "price_adjustment": -10
                },
                "C_grade": {
                    "color_range": "green_to_light_red",
                    "firmness": "soft",
                    "size": "varied",
                    "defects": "visible_damage",
                    "shelf_life": 2,
                    "price_adjustment": -25
                }
            },
            "onions": {
                "A_grade": {
                    "color": "golden_brown",
                    "firmness": "hard",
                    "skin": "dry_papery",
                    "defects": "none",
                    "shelf_life": 30,
                    "price_premium": 0
                },
                "B_grade": {
                    "color": "light_brown",
                    "firmness": "firm",
                    "skin": "slightly_loose",
                    "defects": "minor_bruising",
                    "shelf_life": 20,
                    "price_adjustment": -8
                }
            }
        }
        
        # Defect detection patterns
        self.defect_patterns = {
            "bruising": ["dark_spots", "soft_areas", "discoloration"],
            "mold": ["fuzzy_growth", "white_spots", "green_patches"],
            "overripe": ["soft_texture", "wrinkled_skin", "strong_odor"],
            "underripe": ["green_color", "hard_texture", "no_aroma"],
            "damage": ["cuts", "holes", "cracks", "broken_skin"],
            "pest_damage": ["holes", "bite_marks", "insect_presence"]
        }
        
        # Create workflow
        self.workflow = self._create_workflow()
        
        logger.info("QualityInspectorAgent initialized with AI vision models")
    
    def _create_workflow(self) -> StateGraph:
        """Create the LangGraph workflow for quality inspection"""
        
        # Initialize the graph
        workflow = StateGraph(QualityState)
        
        # Add nodes for each quality operation
        workflow.add_node("visual_analyzer", self.visual_analyzer_node)
        workflow.add_node("defect_detector", self.defect_detector_node)
        workflow.add_node("freshness_assessor", self.freshness_assessor_node)
        workflow.add_node("grade_classifier", self.grade_classifier_node)
        workflow.add_node("recommendation_generator", self.recommendation_generator_node)
        workflow.add_node("coordinator", self.coordinator_node)
        
        # Set entry point
        workflow.set_entry_point("coordinator")
        
        # Add conditional routing from coordinator
        workflow.add_conditional_edges(
            "coordinator",
            self.route_quality_task,
            {
                "visual_inspection": "visual_analyzer",
                "defect_analysis": "defect_detector", 
                "freshness_check": "freshness_assessor",
                "grade_classification": "grade_classifier",
                "generate_recommendations": "recommendation_generator",
                "end": END
            }
        )
        
        # Chain the quality inspection process
        workflow.add_edge("visual_analyzer", "defect_detector")
        workflow.add_edge("defect_detector", "freshness_assessor")
        workflow.add_edge("freshness_assessor", "grade_classifier")
        workflow.add_edge("grade_classifier", "recommendation_generator")
        workflow.add_edge("recommendation_generator", "coordinator")
        
        return workflow.compile()
    
    async def coordinator_node(self, state: QualityState) -> QualityState:
        """
        Coordinator node that orchestrates quality inspection process
        """
        logger.info(f"Quality Coordinator processing task: {state.get('task_type')}")
        
        # Check what has been completed
        has_visual = bool(state.get("visual_analysis"))
        has_defects = bool(state.get("defect_analysis"))
        has_freshness = bool(state.get("freshness_analysis"))
        has_grades = bool(state.get("inspection_results"))
        has_recommendations = bool(state.get("recommendations"))
        
        # Determine next step in quality inspection pipeline
        if not has_visual:
            next_step = "visual_inspection"
        elif not has_defects:
            next_step = "defect_analysis"
        elif not has_freshness:
            next_step = "freshness_check"
        elif not has_grades:
            next_step = "grade_classification"
        elif not has_recommendations:
            next_step = "generate_recommendations"
        else:
            next_step = "end"
        
        message = AIMessage(content=f"Quality inspection coordinator: Next step - {next_step}")
        
        return {
            **state,
            "next_step": next_step,
            "messages": state.get("messages", []) + [message]
        }
    
    def route_quality_task(self, state: QualityState) -> str:
        """Route to the appropriate quality operation"""
        return state.get("next_step", "end")
    
    async def visual_analyzer_node(self, state: QualityState) -> QualityState:
        """
        Analyze product images using AI vision
        """
        logger.info("Visual Analyzer activated")
        
        product_images = state.get("product_images", [])
        product_info = state.get("product_info", {})
        
        if not product_images:
            return {
                **state, 
                "visual_analysis": {"error": "No images provided for analysis"}
            }
        
        # Simulate AI vision analysis (in production, use actual CV models)
        visual_analysis = await self._analyze_images_with_ai(product_images, product_info)
        
        message = AIMessage(content=f"Visual analysis completed for {len(product_images)} images")
        
        return {
            **state,
            "visual_analysis": visual_analysis,
            "messages": state.get("messages", []) + [message]
        }
    
    async def defect_detector_node(self, state: QualityState) -> QualityState:
        """
        Detect specific defects using pattern recognition
        """
        logger.info("Defect Detector activated")
        
        visual_analysis = state.get("visual_analysis", {})
        product_info = state.get("product_info", {})
        
        # Analyze detected features for defects
        defects_found = await self._detect_defects(visual_analysis, product_info)
        
        message = AIMessage(content=f"Defect analysis complete. Found {len(defects_found)} potential issues")
        
        return {
            **state,
            "defect_analysis": defects_found,
            "messages": state.get("messages", []) + [message]
        }
    
    async def freshness_assessor_node(self, state: QualityState) -> QualityState:
        """
        Assess product freshness and shelf life
        """
        logger.info("Freshness Assessor activated")
        
        visual_analysis = state.get("visual_analysis", {})
        defect_analysis = state.get("defect_analysis", [])
        product_info = state.get("product_info", {})
        
        # Calculate freshness score and shelf life
        freshness_assessment = await self._assess_freshness(
            visual_analysis, defect_analysis, product_info
        )
        
        message = AIMessage(content=f"Freshness assessment: Score {freshness_assessment['score']}/10, Shelf life: {freshness_assessment['shelf_life']} days")
        
        return {
            **state,
            "freshness_analysis": freshness_assessment,
            "messages": state.get("messages", []) + [message]
        }
    
    async def grade_classifier_node(self, state: QualityState) -> QualityState:
        """
        Classify products into quality grades
        """
        logger.info("Grade Classifier activated")
        
        visual_analysis = state.get("visual_analysis", {})
        defect_analysis = state.get("defect_analysis", [])
        freshness_analysis = state.get("freshness_analysis", {})
        product_info = state.get("product_info", {})
        
        # Generate quality grades for products
        quality_grades = await self._classify_grades(
            visual_analysis, defect_analysis, freshness_analysis, product_info
        )
        
        total_products = len(quality_grades)
        a_grade_count = sum(1 for grade in quality_grades if grade["grade"] == "A")
        
        message = AIMessage(content=f"Graded {total_products} products. A-grade: {a_grade_count}/{total_products}")
        
        return {
            **state,
            "inspection_results": quality_grades,
            "messages": state.get("messages", []) + [message]
        }
    
    async def recommendation_generator_node(self, state: QualityState) -> QualityState:
        """
        Generate actionable recommendations based on quality assessment
        """
        logger.info("Recommendation Generator activated")
        
        inspection_results = state.get("inspection_results", [])
        product_info = state.get("product_info", {})
        
        # Generate comprehensive recommendations
        recommendations = await self._generate_quality_recommendations(
            inspection_results, product_info
        )
        
        # Generate batch summary
        batch_summary = self._create_batch_summary(inspection_results)
        
        message = AIMessage(content=f"Generated {len(recommendations)} recommendations for quality optimization")
        
        return {
            **state,
            "recommendations": recommendations,
            "batch_summary": batch_summary,
            "messages": state.get("messages", []) + [message]
        }
    
    async def _analyze_images_with_ai(self, images: List[str], product_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze product images using AI vision models
        """
        product_type = product_info.get("type", "unknown")
        
        # Simulate AI vision analysis results
        analysis = {
            "product_type": product_type,
            "color_analysis": {
                "dominant_color": "red" if product_type == "tomatoes" else "brown",
                "color_uniformity": np.random.uniform(0.7, 0.95),
                "color_saturation": np.random.uniform(0.6, 0.9)
            },
            "shape_analysis": {
                "uniformity_score": np.random.uniform(0.6, 0.9),
                "size_consistency": np.random.uniform(0.7, 0.95),
                "geometric_score": np.random.uniform(0.8, 0.95)
            },
            "surface_analysis": {
                "smoothness": np.random.uniform(0.5, 0.9),
                "blemish_count": np.random.randint(0, 3),
                "surface_damage": np.random.uniform(0, 0.2)
            },
            "texture_analysis": {
                "firmness_indicator": np.random.uniform(0.6, 0.95),
                "ripeness_indicator": np.random.uniform(0.7, 0.9)
            }
        }
        
        return analysis
    
    async def _detect_defects(self, visual_analysis: Dict[str, Any], product_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Detect specific defects based on visual analysis
        """
        defects = []
        surface_analysis = visual_analysis.get("surface_analysis", {})
        
        # Check for various defect types
        if surface_analysis.get("blemish_count", 0) > 2:
            defects.append({
                "type": "bruising",
                "severity": "moderate",
                "confidence": 0.85,
                "location": "surface",
                "impact": "appearance"
            })
        
        if surface_analysis.get("surface_damage", 0) > 0.15:
            defects.append({
                "type": "damage",
                "severity": "high",
                "confidence": 0.9,
                "location": "skin",
                "impact": "shelf_life"
            })
        
        # Freshness-related defects
        texture_analysis = visual_analysis.get("texture_analysis", {})
        if texture_analysis.get("firmness_indicator", 1) < 0.7:
            defects.append({
                "type": "overripe",
                "severity": "moderate",
                "confidence": 0.8,
                "location": "internal",
                "impact": "quality"
            })
        
        return defects
    
    async def _assess_freshness(self, visual_analysis: Dict[str, Any], 
                               defects: List[Dict[str, Any]], 
                               product_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Assess product freshness and calculate shelf life
        """
        base_shelf_life = {
            "tomatoes": 7,
            "onions": 30,
            "potatoes": 14,
            "mangoes": 5
        }
        
        product_type = product_info.get("type", "unknown")
        base_life = base_shelf_life.get(product_type, 7)
        
        # Calculate freshness score (1-10)
        firmness = visual_analysis.get("texture_analysis", {}).get("firmness_indicator", 0.8)
        ripeness = visual_analysis.get("texture_analysis", {}).get("ripeness_indicator", 0.8)
        
        freshness_score = int((firmness + ripeness) * 5)
        
        # Adjust shelf life based on defects
        shelf_life_days = base_life
        for defect in defects:
            if defect["impact"] == "shelf_life":
                if defect["severity"] == "high":
                    shelf_life_days = max(1, shelf_life_days - 3)
                elif defect["severity"] == "moderate":
                    shelf_life_days = max(1, shelf_life_days - 1)
        
        return {
            "score": freshness_score,
            "shelf_life": shelf_life_days,
            "firmness": firmness,
            "ripeness": ripeness,
            "storage_recommendation": "cool_dry_place" if shelf_life_days > 3 else "immediate_use"
        }
    
    async def _classify_grades(self, visual_analysis: Dict[str, Any], 
                              defects: List[Dict[str, Any]], 
                              freshness: Dict[str, Any], 
                              product_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Classify products into quality grades
        """
        product_type = product_info.get("type", "unknown")
        quantity = product_info.get("quantity", 1)
        
        grades = []
        
        for i in range(quantity):
            # Calculate overall quality score
            visual_score = np.mean([
                visual_analysis.get("color_analysis", {}).get("color_uniformity", 0.8),
                visual_analysis.get("shape_analysis", {}).get("uniformity_score", 0.8),
                visual_analysis.get("surface_analysis", {}).get("smoothness", 0.8)
            ])
            
            freshness_score = freshness.get("score", 7) / 10.0
            defect_penalty = len([d for d in defects if d["severity"] == "high"]) * 0.2
            
            overall_score = max(0, (visual_score + freshness_score) / 2 - defect_penalty)
            
            # Classify grade
            if overall_score >= 0.8 and len(defects) == 0:
                grade = "A"
                price_adjustment = 0
            elif overall_score >= 0.6:
                grade = "B"
                price_adjustment = -10
            elif overall_score >= 0.4:
                grade = "C"
                price_adjustment = -25
            else:
                grade = "Rejected"
                price_adjustment = -100
            
            grades.append({
                "product_id": f"{product_type}_{i+1}",
                "grade": grade,
                "confidence_score": overall_score,
                "defects": [d["type"] for d in defects],
                "freshness_score": freshness.get("score", 7),
                "shelf_life_days": freshness.get("shelf_life", 3),
                "price_adjustment": price_adjustment,
                "recommendation": self._get_grade_recommendation(grade, defects)
            })
        
        return grades
    
    async def _generate_quality_recommendations(self, inspection_results: List[Dict[str, Any]], 
                                               product_info: Dict[str, Any]) -> List[str]:
        """
        Generate actionable recommendations for quality optimization
        """
        recommendations = []
        
        # Analyze grade distribution
        total_products = len(inspection_results)
        a_grade = sum(1 for result in inspection_results if result["grade"] == "A")
        rejected = sum(1 for result in inspection_results if result["grade"] == "Rejected")
        
        a_grade_percent = (a_grade / total_products * 100) if total_products > 0 else 0
        reject_percent = (rejected / total_products * 100) if total_products > 0 else 0
        
        # Grade distribution recommendations
        if a_grade_percent < 60:
            recommendations.append("Consider improving harvest timing to increase A-grade percentage")
        
        if reject_percent > 10:
            recommendations.append("High rejection rate detected - review harvesting and handling practices")
        
        # Defect-based recommendations
        common_defects = {}
        for result in inspection_results:
            for defect in result.get("defects", []):
                common_defects[defect] = common_defects.get(defect, 0) + 1
        
        for defect, count in common_defects.items():
            if count > total_products * 0.3:  # More than 30% affected
                if defect == "bruising":
                    recommendations.append("Implement gentler handling procedures to reduce bruising")
                elif defect == "damage":
                    recommendations.append("Review packaging and transport methods to prevent damage")
                elif defect == "overripe":
                    recommendations.append("Harvest earlier to prevent overripening")
        
        # Shelf life recommendations
        avg_shelf_life = np.mean([result.get("shelf_life_days", 0) for result in inspection_results])
        if avg_shelf_life < 3:
            recommendations.append("Products have short shelf life - prioritize immediate sale or processing")
        
        # Pricing recommendations
        avg_price_adjustment = np.mean([result.get("price_adjustment", 0) for result in inspection_results])
        if avg_price_adjustment < -15:
            recommendations.append(f"Average quality requires {abs(avg_price_adjustment):.1f}% price reduction")
        
        return recommendations
    
    def _create_batch_summary(self, inspection_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Create summary statistics for the batch
        """
        if not inspection_results:
            return {}
        
        total_products = len(inspection_results)
        
        # Grade distribution
        grade_counts = {"A": 0, "B": 0, "C": 0, "Rejected": 0}
        for result in inspection_results:
            grade = result.get("grade", "Unknown")
            if grade in grade_counts:
                grade_counts[grade] += 1
        
        # Average metrics
        avg_freshness = np.mean([result.get("freshness_score", 0) for result in inspection_results])
        avg_shelf_life = np.mean([result.get("shelf_life_days", 0) for result in inspection_results])
        avg_price_impact = np.mean([result.get("price_adjustment", 0) for result in inspection_results])
        
        return {
            "total_products": total_products,
            "grade_distribution": grade_counts,
            "grade_percentages": {k: v/total_products*100 for k, v in grade_counts.items()},
            "average_freshness_score": round(avg_freshness, 1),
            "average_shelf_life_days": round(avg_shelf_life, 1),
            "average_price_impact": round(avg_price_impact, 1),
            "quality_score": round((grade_counts["A"] + grade_counts["B"]*0.7) / total_products * 100, 1)
        }
    
    def _get_grade_recommendation(self, grade: str, defects: List[Dict[str, Any]]) -> str:
        """
        Get specific recommendation based on grade and defects
        """
        if grade == "A":
            return "Premium quality - package carefully for maximum value"
        elif grade == "B":
            return "Good quality - suitable for regular market with 10% discount"
        elif grade == "C":
            return "Fair quality - consider value-added processing or immediate sale"
        else:
            defect_types = [d.get("type", "") for d in defects]
            if "damage" in defect_types:
                return "Significant damage - unsuitable for fresh sale, consider processing"
            else:
                return "Quality issues detected - not recommended for sale"
    
    async def execute(self, task_type: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute quality inspection workflow
        """
        logger.info(f"Executing quality inspection task: {task_type}")
        
        # Initialize state
        initial_state = {
            "messages": [HumanMessage(content=f"Execute quality inspection: {task_type}")],
            "task_type": task_type,
            "product_images": task_data.get("product_images", []),
            "product_info": task_data.get("product_info", {}),
            "quality_standards": self.quality_standards,
            "inspection_results": [],
            "recommendations": [],
            "batch_summary": {},
            "action_required": []
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
                "inspection_results": final_state.get("inspection_results", []),
                "batch_summary": final_state.get("batch_summary", {}),
                "recommendations": final_state.get("recommendations", []),
                "messages": [msg.content for msg in final_state.get("messages", [])]
            }
            
            logger.info(f"Quality inspection completed in {execution_time:.2f} seconds")
            return result
            
        except Exception as e:
            logger.error(f"Quality inspection workflow failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "task_type": task_type
            }

# Example usage
async def main():
    """Example usage of the quality inspector agent"""
    
    inspector = QualityInspectorAgent()
    
    # Test visual inspection
    inspection_task = {
        "product_images": ["image1.jpg", "image2.jpg"],
        "product_info": {
            "type": "tomatoes",
            "quantity": 10,
            "batch_id": "TOM_2024_001",
            "harvest_date": "2024-01-15"
        }
    }
    
    result = await inspector.execute("visual_inspection", inspection_task)
    print("Quality Inspection Result:", json.dumps(result, indent=2))

if __name__ == "__main__":
    asyncio.run(main())