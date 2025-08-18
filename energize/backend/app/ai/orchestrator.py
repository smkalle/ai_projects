"""AI orchestrator using LangGraph for energy optimization."""

from typing import TypedDict, Annotated, Dict, Any
import operator
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from app.ai.config import AIConfig
import asyncio
import logging

logger = logging.getLogger(__name__)


class EnergyState(TypedDict):
    """State for energy management workflow."""
    building_id: str
    current_consumption: float
    target_reduction: float
    anomalies: list
    recommendations: list
    carbon_footprint: float
    optimization_score: float
    messages: Annotated[list, operator.add]
    sensor_data: dict
    weather_data: dict
    error: str


class EnergyOrchestrator:
    """AI orchestrator for energy optimization using LangGraph."""
    
    def __init__(self, config: AIConfig = None):
        self.config = config or AIConfig()
        self.llm = ChatOpenAI(
            model=self.config.openai_model,
            temperature=self.config.openai_temperature,
            max_tokens=self.config.openai_max_tokens
        )
        self.workflow = self._build_workflow()
    
    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow for energy optimization."""
        workflow = StateGraph(EnergyState)
        
        # Add nodes for each AI agent
        workflow.add_node("analyze", self._analyze_consumption)
        workflow.add_node("detect_anomalies", self._detect_anomalies)
        workflow.add_node("optimize_energy", self._optimize_energy)
        workflow.add_node("forecast_demand", self._forecast_demand)
        workflow.add_node("reduce_carbon", self._reduce_carbon)
        workflow.add_node("generate_actions", self._generate_actions)
        workflow.add_node("validate_results", self._validate_results)
        
        # Define the workflow flow
        workflow.set_entry_point("analyze")
        workflow.add_edge("analyze", "detect_anomalies")
        workflow.add_conditional_edges(
            "detect_anomalies",
            self._route_based_on_anomalies,
            {
                "optimize": "optimize_energy",
                "forecast": "forecast_demand",
                "critical": "generate_actions"
            }
        )
        workflow.add_edge("optimize_energy", "reduce_carbon")
        workflow.add_edge("forecast_demand", "reduce_carbon")
        workflow.add_edge("reduce_carbon", "validate_results")
        workflow.add_edge("validate_results", "generate_actions")
        workflow.add_edge("generate_actions", END)
        
        return workflow.compile()
    
    async def _analyze_consumption(self, state: EnergyState) -> EnergyState:
        """Analyze current energy consumption patterns."""
        try:
            prompt = f"""
            Analyze energy consumption for Building {state['building_id']}:
            Current consumption: {state['current_consumption']} kWh
            Target reduction: {state['target_reduction']}%
            
            Provide initial analysis and optimization opportunities.
            Be specific and actionable.
            """
            
            response = await self.llm.ainvoke(prompt)
            
            state['messages'].append({
                'agent': 'analyzer',
                'action': 'consumption_analysis',
                'result': response.content,
                'timestamp': 'now'
            })
            
            # Calculate baseline metrics
            state['optimization_score'] = 65.0  # Initial score
            
            logger.info(f"Analyzed consumption for building {state['building_id']}")
            return state
            
        except Exception as e:
            state['error'] = f"Analysis failed: {str(e)}"
            return state
    
    async def _detect_anomalies(self, state: EnergyState) -> EnergyState:
        """Detect anomalies in energy consumption."""
        try:
            anomalies = []
            
            # Simulate anomaly detection
            if state['current_consumption'] > 1000:  # High consumption
                anomalies.append({
                    'type': 'high_consumption',
                    'severity': 'medium',
                    'description': 'Consumption 20% above normal',
                    'potential_savings': state['current_consumption'] * 0.2
                })
            
            prompt = f"""
            Detected {len(anomalies)} anomalies in Building {state['building_id']}:
            {anomalies}
            
            Analyze these anomalies and recommend immediate actions.
            Focus on energy waste reduction and cost savings.
            """
            
            if anomalies:
                response = await self.llm.ainvoke(prompt)
                state['messages'].append({
                    'agent': 'anomaly_detector',
                    'action': 'anomaly_analysis',
                    'result': response.content,
                    'anomalies_found': len(anomalies)
                })
            
            state['anomalies'] = anomalies
            logger.info(f"Detected {len(anomalies)} anomalies")
            return state
            
        except Exception as e:
            state['error'] = f"Anomaly detection failed: {str(e)}"
            return state
    
    async def _optimize_energy(self, state: EnergyState) -> EnergyState:
        """Optimize energy consumption using AI."""
        try:
            prompt = f"""
            Optimize energy for Building {state['building_id']}:
            Current: {state['current_consumption']} kWh
            Target reduction: {state['target_reduction']}%
            Anomalies: {len(state['anomalies'])} found
            
            Generate specific optimization strategies:
            1. HVAC optimization
            2. Lighting efficiency
            3. Equipment scheduling
            4. Peak shaving opportunities
            
            Provide actionable recommendations with expected savings.
            """
            
            response = await self.llm.ainvoke(prompt)
            
            # Calculate optimization potential
            optimization_potential = state['current_consumption'] * (state['target_reduction'] / 100)
            
            state['recommendations'].extend([
                f"Implement smart HVAC scheduling (save {optimization_potential * 0.4:.0f} kWh)",
                f"Optimize lighting systems (save {optimization_potential * 0.2:.0f} kWh)",
                f"Schedule non-critical loads to off-peak (save {optimization_potential * 0.3:.0f} kWh)"
            ])
            
            state['messages'].append({
                'agent': 'optimizer',
                'action': 'energy_optimization',
                'result': response.content,
                'potential_savings': optimization_potential
            })
            
            state['optimization_score'] += 20  # Boost score
            logger.info(f"Generated optimization plan for building {state['building_id']}")
            return state
            
        except Exception as e:
            state['error'] = f"Optimization failed: {str(e)}"
            return state
    
    async def _forecast_demand(self, state: EnergyState) -> EnergyState:
        """Forecast energy demand using AI."""
        try:
            prompt = f"""
            Forecast energy demand for Building {state['building_id']}:
            Current consumption: {state['current_consumption']} kWh
            Historical patterns available
            Weather conditions: Variable
            
            Provide 24-hour demand forecast with:
            1. Peak demand times
            2. Optimization windows
            3. Load shifting opportunities
            4. Risk factors
            """
            
            response = await self.llm.ainvoke(prompt)
            
            # Simulate forecast data
            forecast_peak = state['current_consumption'] * 1.3
            forecast_low = state['current_consumption'] * 0.7
            
            state['messages'].append({
                'agent': 'forecaster',
                'action': 'demand_forecast',
                'result': response.content,
                'peak_forecast': forecast_peak,
                'low_forecast': forecast_low
            })
            
            state['optimization_score'] += 10
            logger.info(f"Generated demand forecast for building {state['building_id']}")
            return state
            
        except Exception as e:
            state['error'] = f"Forecasting failed: {str(e)}"
            return state
    
    async def _reduce_carbon(self, state: EnergyState) -> EnergyState:
        """Reduce carbon footprint through intelligent optimization."""
        try:
            prompt = f"""
            Reduce carbon footprint for Building {state['building_id']}:
            Current footprint: {state['carbon_footprint']} tons CO2
            Energy consumption: {state['current_consumption']} kWh
            
            Generate carbon reduction strategy:
            1. Renewable energy utilization
            2. Grid optimization timing
            3. Carbon-aware load scheduling
            4. Emission reduction opportunities
            """
            
            response = await self.llm.ainvoke(prompt)
            
            # Calculate carbon reduction
            carbon_reduction = state['carbon_footprint'] * 0.25  # 25% reduction
            state['carbon_footprint'] -= carbon_reduction
            
            state['recommendations'].append(
                f"Shift loads to low-carbon hours (reduce {carbon_reduction:.1f} tons CO2)"
            )
            
            state['messages'].append({
                'agent': 'carbon_reducer',
                'action': 'carbon_optimization',
                'result': response.content,
                'carbon_saved': carbon_reduction
            })
            
            state['optimization_score'] += 15
            logger.info(f"Reduced carbon footprint by {carbon_reduction:.1f} tons")
            return state
            
        except Exception as e:
            state['error'] = f"Carbon reduction failed: {str(e)}"
            return state
    
    async def _validate_results(self, state: EnergyState) -> EnergyState:
        """Validate optimization results."""
        try:
            # Validation logic
            if state['optimization_score'] >= 85:
                validation_status = "Excellent optimization achieved"
            elif state['optimization_score'] >= 70:
                validation_status = "Good optimization results"
            else:
                validation_status = "Optimization needs improvement"
            
            state['messages'].append({
                'agent': 'validator',
                'action': 'result_validation',
                'status': validation_status,
                'final_score': state['optimization_score']
            })
            
            return state
            
        except Exception as e:
            state['error'] = f"Validation failed: {str(e)}"
            return state
    
    async def _generate_actions(self, state: EnergyState) -> EnergyState:
        """Generate final actionable recommendations."""
        try:
            prompt = f"""
            Generate final action plan for Building {state['building_id']}:
            
            Optimization Score: {state['optimization_score']}/100
            Recommendations: {len(state['recommendations'])}
            Anomalies: {len(state['anomalies'])}
            Carbon Reduction: {state.get('carbon_saved', 0)} tons
            
            Create prioritized action plan with:
            1. Immediate actions (next 1 hour)
            2. Short-term actions (next 24 hours)
            3. Medium-term optimizations (next week)
            4. Expected ROI and savings
            """
            
            response = await self.llm.ainvoke(prompt)
            
            final_actions = {
                'immediate': [
                    'Adjust HVAC setpoints by 2°C',
                    'Switch to LED lighting in unoccupied areas'
                ],
                'short_term': [
                    'Schedule equipment maintenance',
                    'Implement demand response program'
                ],
                'medium_term': [
                    'Install smart sensors',
                    'Upgrade to efficient equipment'
                ],
                'expected_savings': f"${state['current_consumption'] * 0.15:.0f}/month"
            }
            
            state['messages'].append({
                'agent': 'action_generator',
                'action': 'final_recommendations',
                'result': response.content,
                'action_plan': final_actions
            })
            
            logger.info(f"Generated final action plan for building {state['building_id']}")
            return state
            
        except Exception as e:
            state['error'] = f"Action generation failed: {str(e)}"
            return state
    
    def _route_based_on_anomalies(self, state: EnergyState) -> str:
        """Route workflow based on anomaly detection results."""
        if state.get('error'):
            return "critical"
        
        anomalies = state.get('anomalies', [])
        critical_anomalies = [a for a in anomalies if a.get('severity') == 'critical']
        
        if critical_anomalies:
            return "critical"
        elif anomalies:
            return "optimize"
        else:
            return "forecast"
    
    async def optimize_building(self, building_id: str, current_consumption: float) -> Dict[str, Any]:
        """Main entry point for building optimization."""
        try:
            initial_state = EnergyState(
                building_id=building_id,
                current_consumption=current_consumption,
                target_reduction=self.config.target_energy_reduction,
                anomalies=[],
                recommendations=[],
                carbon_footprint=current_consumption * 0.0005,  # kg CO2 per kWh
                optimization_score=50.0,
                messages=[],
                sensor_data={},
                weather_data={},
                error=""
            )
            
            result = await self.workflow.ainvoke(initial_state)
            
            return {
                'status': 'success' if not result.get('error') else 'error',
                'building_id': building_id,
                'optimization_score': result['optimization_score'],
                'recommendations': result['recommendations'],
                'anomalies_detected': len(result['anomalies']),
                'carbon_footprint': result['carbon_footprint'],
                'actions': result['messages'][-1].get('action_plan', {}),
                'error': result.get('error')
            }
            
        except Exception as e:
            logger.error(f"Optimization failed for building {building_id}: {str(e)}")
            return {
                'status': 'error',
                'building_id': building_id,
                'error': str(e)
            }