"""A2A Agents for Medical AI Assistant MVP with AI Integration."""

import json
import logging
import time
from typing import Any, Optional

from openai import AsyncOpenAI
from cachetools import TTLCache
from python_a2a import agent, skill
from tenacity import retry, stop_after_attempt, wait_exponential

from .config import settings
from .models import TriageAssessment

logger = logging.getLogger(__name__)

# Initialize OpenAI client
openai_client = AsyncOpenAI(api_key=settings.openai_api_key)

# Assessment cache for cost optimization
assessment_cache = TTLCache(
    maxsize=settings.cache_max_size,
    ttl=settings.cache_ttl_seconds
) if settings.enable_assessment_cache else None


# AI Prompt Templates
TRIAGE_SYSTEM_PROMPT = """You are a medical triage AI assistant for remote healthcare in underserved areas. Your role is to assess symptoms and provide first-aid guidance to community health volunteers.

<critical_safety_rules>
1. Always err on the side of caution - when in doubt, escalate
2. Escalate serious symptoms immediately to healthcare providers
3. Include clear, actionable first-aid steps that volunteers can safely perform
4. Consider age-specific factors (infants under 2 years, elderly over 65 years)
5. Flag any red flag symptoms that require immediate medical attention
6. Never provide medication dosing advice in triage assessments
</critical_safety_rules>

<response_format>
You must respond with valid JSON in exactly this format:
{{
  "urgency": "low|medium|high|emergency",
  "actions": ["action1", "action2", "action3"],
  "escalate": true|false,
  "confidence": 0.0-1.0,
  "red_flags": ["flag1", "flag2"],
  "reasoning": "Brief explanation of your assessment"
}}
</response_format>

<assessment_context>
Patient age: {age} years old
Reported symptoms: {symptoms}
Volunteer-assessed severity: {severity}
</assessment_context>

Think step by step about this assessment, considering the patient's age, symptoms, and any potential red flags before providing your JSON response."""

DOSAGE_SYSTEM_PROMPT = """You are a medication dosage calculator for basic medications in remote healthcare settings. You calculate safe dosages with appropriate warnings for community health volunteers.

<available_medications>
- acetaminophen (paracetamol): For pain and fever
- ibuprofen: For pain, inflammation, and fever  
- paracetamol: Same as acetaminophen
</available_medications>

<safety_requirements>
1. Always provide conservative, safe dosages
2. Include maximum daily limits and frequency
3. Add age-appropriate warnings
4. List contraindications and when NOT to give medication
5. Emphasize the need for healthcare provider consultation
</safety_requirements>

<response_format>
You must respond with valid JSON in exactly this format:
{{
  "medication": "medication_name",
  "dose_mg": number,
  "dose_type": "pediatric|adult",
  "frequency": "Every X hours",
  "max_daily_mg": number,
  "warnings": ["warning1", "warning2"],
  "contraindications": ["condition1", "condition2"]
}}
</response_format>

<calculation_context>
Medication requested: {medication}
Patient age: {age_years} years
Patient weight: {weight_kg} kg
</calculation_context>

Think carefully about the appropriate dosage for this patient's age and weight, then provide your JSON response."""


class CostOptimizer:
    """Intelligent routing for cost optimization."""
    
    @staticmethod
    def should_use_ai(symptoms: str, severity: str) -> bool:
        """Determine if AI call is cost-effective."""
        if not settings.ai_cost_optimization:
            return True
            
        # Emergency cases always use AI (check first)
        if severity == "emergency":
            return True
            
        # Simple cases use local processing
        simple_keywords = ["mild", "minor", "small", "slight"]
        if any(word in symptoms.lower() for word in simple_keywords):
            return False
            
        # Complex symptoms use AI
        complex_keywords = ["multiple", "severe", "unusual", "complex"]
        if any(word in symptoms.lower() for word in complex_keywords):
            return True
            
        return True  # Default to AI for better accuracy
    
    @staticmethod
    def get_cache_key(symptoms: str, age: int, severity: str) -> str:
        """Generate cache key for assessment."""
        # Normalize inputs for better cache hits
        symptoms_normalized = symptoms.lower().strip()
        age_range = f"{age//10*10}-{age//10*10+9}"  # Age ranges for privacy
        return f"{symptoms_normalized}:{age_range}:{severity}"


@agent(
    name="Hybrid Triage Agent",
    description="AI-powered medical triage with local fallback",
    version="0.2.0",
)
class HybridTriageAgent:
    """AI-powered triage agent with intelligent fallback."""

    def __init__(self) -> None:
        """Initialize the hybrid triage agent."""
        self.local_agent = MVPTriageAgent()  # Fallback agent
        self.cost_optimizer = CostOptimizer()
        logger.info("Hybrid Triage Agent initialized with AI integration")

    @retry(
        stop=stop_after_attempt(settings.openai_max_retries),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def _ai_assessment(
        self, symptoms: str, age: int, severity: str
    ) -> TriageAssessment:
        """Perform AI-powered assessment with retry logic."""
        start_time = time.time()
        
        try:
            # Prepare prompt with proper parameter substitution
            system_prompt = TRIAGE_SYSTEM_PROMPT.format(
                age=age,
                symptoms=symptoms,
                severity=severity
            )
            
            # Call OpenAI API
            response = await openai_client.chat.completions.create(
                model=settings.openai_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Please assess these symptoms: {symptoms}"}
                ],
                max_tokens=settings.openai_max_tokens,
                temperature=settings.openai_temperature,
                timeout=settings.openai_timeout,
            )
            
            # Parse response
            content = response.choices[0].message.content.strip()
            
            # Try to extract JSON if it's wrapped in markdown or other text
            if "```json" in content:
                # Extract JSON from markdown code block
                start = content.find("```json") + 7
                end = content.find("```", start)
                content = content[start:end].strip()
            elif "{" in content and "}" in content:
                # Extract JSON from mixed content
                start = content.find("{")
                end = content.rfind("}") + 1
                content = content[start:end]
            
            assessment_data = json.loads(content)
            
            # Apply safety mode adjustments
            if settings.ai_safety_mode:
                assessment_data = self._apply_safety_mode(assessment_data, age)
            
            # Create assessment object
            assessment = TriageAssessment(**assessment_data)
            
            # Log metrics
            processing_time = (time.time() - start_time) * 1000
            logger.info(f"AI assessment completed in {processing_time:.0f}ms")
            
            return assessment
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI response as JSON: {e}")
            logger.error(f"Raw response content: {content}")
            raise
        except Exception as e:
            logger.error(f"AI assessment failed: {e}")
            raise

    def _apply_safety_mode(self, assessment_data: dict, age: int) -> dict:
        """Apply safety mode adjustments to AI assessment."""
        # More conservative for infants and elderly
        if age < 2 or age > 65:
            if assessment_data.get("urgency") == "low":
                assessment_data["urgency"] = "medium"
            if not assessment_data.get("escalate") and assessment_data.get("urgency") in ["high", "emergency"]:
                assessment_data["escalate"] = True
        
        # Always include safety disclaimer
        if "actions" in assessment_data:
            assessment_data["actions"].append("consult_healthcare_provider_if_concerned")
        
        return assessment_data

    @skill(name="assess_symptoms")
    async def assess_symptoms(
        self, symptoms: str, age: int, severity: str = "medium"
    ) -> TriageAssessment:
        """Assess symptoms using AI with local fallback."""
        logger.info(f"Assessing symptoms: {symptoms} for age {age}")
        
        # Check cache first
        if assessment_cache:
            cache_key = self.cost_optimizer.get_cache_key(symptoms, age, severity)
            cached_result = assessment_cache.get(cache_key)
            if cached_result:
                logger.info("Using cached assessment")
                return cached_result
        
        # Determine if we should use AI
        use_ai = (
            settings.ai_fallback_enabled and 
            self.cost_optimizer.should_use_ai(symptoms, severity) and
            not settings.dev_mock_ai
        )
        
        if use_ai:
            try:
                # Try AI-powered assessment
                assessment = await self._ai_assessment(symptoms, age, severity)
                
                # Cache the result
                if assessment_cache:
                    cache_key = self.cost_optimizer.get_cache_key(symptoms, age, severity)
                    assessment_cache[cache_key] = assessment
                
                logger.info(f"AI assessment result: urgency={assessment.urgency}, escalate={assessment.escalate}")
                return assessment
                
            except Exception as e:
                logger.warning(f"AI assessment failed: {e}, falling back to local")
        
        # Fallback to local assessment
        logger.info("Using local fallback assessment")
        return await self.local_agent.assess_symptoms(symptoms, age, severity)


@agent(
    name="AI Medical Tools",
    description="AI-powered medication calculator with local fallback",
    version="0.2.0",
)
class HybridMedicalTools:
    """AI-powered medical tools with intelligent fallback."""

    def __init__(self) -> None:
        """Initialize the hybrid medical tools."""
        self.local_tools = MVPMedicalTools()  # Fallback tools
        logger.info("Hybrid Medical Tools initialized with AI integration")

    @retry(
        stop=stop_after_attempt(settings.openai_max_retries),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def _ai_dosage_calculation(
        self, medication: str, weight_kg: float, age_years: int
    ) -> dict[str, Any]:
        """Perform AI-powered dosage calculation."""
        try:
            # Prepare prompt with proper parameter substitution
            system_prompt = DOSAGE_SYSTEM_PROMPT.format(
                medication=medication,
                age_years=age_years,
                weight_kg=weight_kg
            )
            
            # Call OpenAI API
            response = await openai_client.chat.completions.create(
                model=settings.openai_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Please calculate the dosage for {medication}"}
                ],
                max_tokens=settings.openai_max_tokens,
                temperature=settings.openai_temperature,
                timeout=settings.openai_timeout,
            )
            
            # Parse response
            content = response.choices[0].message.content.strip()
            
            # Try to extract JSON if it's wrapped in markdown or other text
            if "```json" in content:
                # Extract JSON from markdown code block
                start = content.find("```json") + 7
                end = content.find("```", start)
                content = content[start:end].strip()
            elif "{" in content and "}" in content:
                # Extract JSON from mixed content
                start = content.find("{")
                end = content.rfind("}") + 1
                content = content[start:end]
            
            dosage_data = json.loads(content)
            
            # Apply safety checks
            if settings.ai_safety_mode:
                dosage_data = self._apply_dosage_safety(dosage_data, age_years)
            
            return dosage_data
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI dosage response as JSON: {e}")
            logger.error(f"Raw response content: {content}")
            raise
        except Exception as e:
            logger.error(f"AI dosage calculation failed: {e}")
            raise

    def _apply_dosage_safety(self, dosage_data: dict, age_years: int) -> dict:
        """Apply safety checks to dosage calculations."""
        # Add extra warnings for pediatric patients
        if age_years < 12:
            if "warnings" not in dosage_data:
                dosage_data["warnings"] = []
            dosage_data["warnings"].append("Pediatric dosing - verify with healthcare provider")
        
        # Always include safety disclaimer
        if "warnings" not in dosage_data:
            dosage_data["warnings"] = []
        dosage_data["warnings"].append("Always consult healthcare provider before administering")
        
        return dosage_data

    async def calculate_dose(
        self, medication: str, weight_kg: float, age_years: int
    ) -> dict[str, Any]:
        """Calculate medication dosage using AI with local fallback."""
        logger.info(f"Calculating dose for {medication}, age {age_years}, weight {weight_kg}kg")
        
        # Determine if we should use AI
        use_ai = (
            settings.ai_fallback_enabled and 
            not settings.dev_mock_ai
        )
        
        if use_ai:
            try:
                # Try AI-powered calculation
                result = await self._ai_dosage_calculation(medication, weight_kg, age_years)
                logger.info(f"AI dosage calculation completed for {medication}")
                return result
                
            except Exception as e:
                logger.warning(f"AI dosage calculation failed: {e}, falling back to local")
        
        # Fallback to local calculation
        logger.info("Using local fallback dosage calculation")
        return self.local_tools.calculate_dose(medication, weight_kg, age_years)

    @retry(
        stop=stop_after_attempt(settings.openai_max_retries),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def get_medical_advice(self, prompt: str) -> str:
        """Get AI-powered medical advice for image analysis and general consultation."""
        try:
            logger.info("Getting AI medical advice")
            
            # Enhanced system prompt for medical image analysis
            system_prompt = """You are an experienced medical AI assistant specializing in clinical assessment and image analysis. 
            
            Your role is to provide detailed, structured medical analysis for healthcare providers in remote settings.
            
            Guidelines:
            - Provide thorough but concise medical assessments
            - Focus on actionable insights for healthcare providers
            - Consider conditions common in remote/underserved areas
            - Always recommend clinical correlation
            - Be specific about urgency levels and reasoning
            - Include relevant red flags and warning signs
            - Structure your response clearly with sections
            
            Remember: You are assisting healthcare providers, not replacing clinical judgment."""
            
            # Call OpenAI API
            response = await openai_client.chat.completions.create(
                model=settings.openai_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,  # Longer response for detailed analysis
                temperature=0.3,  # Lower temperature for more consistent medical advice
                timeout=settings.openai_timeout,
            )
            
            content = response.choices[0].message.content.strip()
            logger.info("AI medical advice completed")
            return content
            
        except Exception as e:
            logger.error(f"AI medical advice failed: {e}")
            # Return fallback advice
            return """Medical Assessment:

VISUAL OBSERVATIONS:
- Image requires clinical evaluation
- Unable to complete automated analysis

POSSIBLE CONDITIONS:
- Multiple differential diagnoses possible
- Clinical examination needed for accurate assessment

URGENCY ASSESSMENT:
- Medium priority - clinical evaluation recommended
- Consider patient symptoms and history

RECOMMENDED ACTIONS:
- Seek clinical evaluation by healthcare provider
- Document symptoms and progression
- Monitor for changes

RED FLAGS:
- Any rapid changes in appearance
- Associated systemic symptoms
- Signs of infection or inflammation

Note: Automated analysis unavailable - manual clinical assessment required."""


# Original MVP agents for fallback
@agent(
    name="MVP Triage Agent",
    description="Basic first-aid decision support for MVP",
    version="0.1.0",
)
class MVPTriageAgent:
    """Simple triage agent with hardcoded decision trees."""

    def __init__(self) -> None:
        """Initialize the triage agent."""
        self.decision_trees = self._load_basic_trees()
        logger.info("MVP Triage Agent initialized")

    def _load_basic_trees(self) -> dict[str, dict[str, Any]]:
        """Load basic hardcoded decision trees for MVP."""
        return {
            "fever": {
                "high_temp": {
                    "urgency": "high",
                    "actions": [
                        "rest",
                        "fluids",
                        "monitor_temperature",
                        "seek_medical_care",
                    ],
                    "escalate": True,
                    "red_flags": ["high_fever"],
                },
                "low_temp": {
                    "urgency": "medium",
                    "actions": ["rest", "fluids", "monitor_temperature"],
                    "escalate": False,
                    "red_flags": [],
                },
            },
            "bleeding": {
                "severe": {
                    "urgency": "emergency",
                    "actions": ["apply_pressure", "elevate_wound", "call_emergency"],
                    "escalate": True,
                    "red_flags": ["severe_bleeding", "shock_signs"],
                },
                "minor": {
                    "urgency": "low",
                    "actions": ["clean_wound", "apply_bandage", "monitor"],
                    "escalate": False,
                    "red_flags": [],
                },
            },
            "pain": {
                "severe": {
                    "urgency": "high",
                    "actions": ["rest", "position_comfort", "seek_medical_care"],
                    "escalate": True,
                    "red_flags": ["severe_pain"],
                },
                "mild": {
                    "urgency": "low",
                    "actions": ["rest", "position_comfort", "monitor"],
                    "escalate": False,
                    "red_flags": [],
                },
            },
            "breathing": {
                "difficulty": {
                    "urgency": "emergency",
                    "actions": ["sit_upright", "loosen_clothing", "call_emergency"],
                    "escalate": True,
                    "red_flags": ["breathing_difficulty", "chest_pain"],
                }
            },
            "nausea": {
                "with_vomiting": {
                    "urgency": "medium",
                    "actions": ["rest", "small_sips_water", "monitor"],
                    "escalate": False,
                    "red_flags": [],
                }
            },
            "injury": {
                "head": {
                    "urgency": "high",
                    "actions": [
                        "keep_still",
                        "monitor_consciousness",
                        "seek_medical_care",
                    ],
                    "escalate": True,
                    "red_flags": ["head_injury", "loss_of_consciousness"],
                },
                "limb": {
                    "urgency": "medium",
                    "actions": ["immobilize", "ice_if_swelling", "monitor"],
                    "escalate": False,
                    "red_flags": [],
                },
            },
        }

    @skill(name="assess_symptoms")
    async def assess_symptoms(
        self, symptoms: str, age: int, severity: str = "medium"
    ) -> TriageAssessment:
        """Assess patient symptoms and provide first-aid guidance."""
        logger.info(f"Assessing symptoms: {symptoms} for age {age}")

        # Simple keyword-based assessment for MVP
        symptoms_lower = symptoms.lower()

        # Initialize default assessment
        urgency = "medium"
        actions = ["rest", "monitor", "seek_medical_advice_if_worsens"]
        escalate = False
        red_flags = []
        confidence = 0.7  # Default confidence for MVP

        # Check for fever
        if any(
            word in symptoms_lower
            for word in ["fever", "temperature", "hot", "burning"]
        ):
            if age < 2 or any(
                word in symptoms_lower for word in ["high", "very", "severe"]
            ):
                assessment = self.decision_trees["fever"]["high_temp"]
            else:
                assessment = self.decision_trees["fever"]["low_temp"]
            urgency = assessment["urgency"]
            actions = assessment["actions"]
            escalate = assessment["escalate"]
            red_flags.extend(assessment["red_flags"])

        # Check for bleeding
        elif any(
            word in symptoms_lower for word in ["bleeding", "blood", "cut", "wound"]
        ):
            if any(
                word in symptoms_lower for word in ["severe", "heavy", "lot", "much"]
            ):
                assessment = self.decision_trees["bleeding"]["severe"]
            else:
                assessment = self.decision_trees["bleeding"]["minor"]
            urgency = assessment["urgency"]
            actions = assessment["actions"]
            escalate = assessment["escalate"]
            red_flags.extend(assessment["red_flags"])

        # Check for breathing issues
        elif any(
            word in symptoms_lower for word in ["breathing", "breath", "chest", "air"]
        ):
            assessment = self.decision_trees["breathing"]["difficulty"]
            urgency = assessment["urgency"]
            actions = assessment["actions"]
            escalate = assessment["escalate"]
            red_flags.extend(assessment["red_flags"])

        # Check for pain
        elif any(word in symptoms_lower for word in ["pain", "hurt", "ache"]):
            if any(
                word in symptoms_lower for word in ["severe", "intense", "unbearable"]
            ):
                assessment = self.decision_trees["pain"]["severe"]
            else:
                assessment = self.decision_trees["pain"]["mild"]
            urgency = assessment["urgency"]
            actions = assessment["actions"]
            escalate = assessment["escalate"]
            red_flags.extend(assessment["red_flags"])

        # Check for nausea/vomiting
        elif any(
            word in symptoms_lower for word in ["nausea", "vomit", "sick", "stomach"]
        ):
            assessment = self.decision_trees["nausea"]["with_vomiting"]
            urgency = assessment["urgency"]
            actions = assessment["actions"]
            escalate = assessment["escalate"]
            red_flags.extend(assessment["red_flags"])

        # Check for injuries
        elif any(
            word in symptoms_lower
            for word in ["injury", "injured", "hurt", "fall", "hit"]
        ):
            if any(word in symptoms_lower for word in ["head", "skull", "brain"]):
                assessment = self.decision_trees["injury"]["head"]
            else:
                assessment = self.decision_trees["injury"]["limb"]
            urgency = assessment["urgency"]
            actions = assessment["actions"]
            escalate = assessment["escalate"]
            red_flags.extend(assessment["red_flags"])

        # Age-based adjustments
        if age < 2:  # Infants
            if urgency == "low":
                urgency = "medium"
            escalate = True
            red_flags.append("infant_patient")
        elif age > 65:  # Elderly
            if urgency == "low":
                urgency = "medium"
            red_flags.append("elderly_patient")

        # Severity override
        if severity == "emergency":
            urgency = "emergency"
            escalate = True
            actions = ["call_emergency", "monitor_vital_signs"] + actions

        logger.info(f"Assessment result: urgency={urgency}, escalate={escalate}")

        return TriageAssessment(
            urgency=urgency,
            actions=actions,
            escalate=escalate,
            confidence=confidence,
            red_flags=red_flags,
            reasoning=f"Local assessment based on keywords and age {age}",
        )


class MVPMedicalTools:
    """Simple medical tools for MVP."""

    def __init__(self) -> None:
        """Initialize medical tools."""
        self.medications = {
            "acetaminophen": {
                "pediatric_dose_mg_per_kg": 10,
                "adult_dose_mg": 500,
                "frequency_hours": 6,
                "max_daily_mg": 4000,
            },
            "ibuprofen": {
                "pediatric_dose_mg_per_kg": 5,
                "adult_dose_mg": 200,
                "frequency_hours": 6,
                "max_daily_mg": 2400,
            },
            "paracetamol": {
                "pediatric_dose_mg_per_kg": 10,
                "adult_dose_mg": 500,
                "frequency_hours": 6,
                "max_daily_mg": 4000,
            },
        }
        logger.info("MVP Medical Tools initialized")

    def calculate_dose(
        self, medication: str, weight_kg: float, age_years: int
    ) -> dict[str, Any]:
        """Calculate medication dosage."""
        medication_lower = medication.lower()

        if medication_lower not in self.medications:
            return {
                "error": f"Medication '{medication}' not found in database",
                "available_medications": list(self.medications.keys()),
            }

        med_info = self.medications[medication_lower]

        if age_years < 12 and weight_kg:
            # Pediatric dosing
            dose_mg = med_info["pediatric_dose_mg_per_kg"] * weight_kg
            dose_type = "pediatric"
        else:
            # Adult dosing
            dose_mg = med_info["adult_dose_mg"]
            dose_type = "adult"

        return {
            "medication": medication,
            "dose_mg": round(dose_mg, 1),
            "dose_type": dose_type,
            "frequency": f"Every {med_info['frequency_hours']} hours",
            "max_daily_mg": med_info["max_daily_mg"],
            "warnings": ["Always consult healthcare provider before administering medication"],
            "contraindications": ["Known allergies", "Liver disease (for acetaminophen)", "Kidney disease (for ibuprofen)"],
        }
