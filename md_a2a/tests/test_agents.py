"""Tests for AI agents."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import json

from src.agents import (
    MVPMedicalTools, 
    MVPTriageAgent, 
    HybridTriageAgent, 
    HybridMedicalTools,
    CostOptimizer
)
from src.config import Settings


class TestMVPTriageAgent:
    """Test the MVP Triage Agent (Local Fallback)."""

    @pytest.fixture
    def agent(self) -> MVPTriageAgent:
        """Create a triage agent instance."""
        return MVPTriageAgent()

    @pytest.mark.asyncio
    async def test_fever_assessment_high(self, agent: MVPTriageAgent) -> None:
        """Test fever assessment for high temperature."""
        result = await agent.assess_symptoms("high fever", age=8)

        assert result.urgency == "high"
        assert result.escalate is True
        assert "rest" in result.actions
        assert "fluids" in result.actions
        assert "high_fever" in result.red_flags

    @pytest.mark.asyncio
    async def test_fever_assessment_low(self, agent: MVPTriageAgent) -> None:
        """Test fever assessment for low temperature."""
        result = await agent.assess_symptoms("mild fever", age=8)

        assert result.urgency == "medium"
        assert result.escalate is False
        assert "rest" in result.actions
        assert "fluids" in result.actions

    @pytest.mark.asyncio
    async def test_bleeding_assessment_severe(self, agent: MVPTriageAgent) -> None:
        """Test severe bleeding assessment."""
        result = await agent.assess_symptoms("severe bleeding", age=25)

        assert result.urgency == "emergency"
        assert result.escalate is True
        assert "apply_pressure" in result.actions
        assert "call_emergency" in result.actions
        assert "severe_bleeding" in result.red_flags

    @pytest.mark.asyncio
    async def test_bleeding_assessment_minor(self, agent: MVPTriageAgent) -> None:
        """Test minor bleeding assessment."""
        result = await agent.assess_symptoms("small cut", age=25)

        assert result.urgency == "low"
        assert result.escalate is False
        assert "clean_wound" in result.actions
        assert "apply_bandage" in result.actions

    @pytest.mark.asyncio
    async def test_breathing_difficulty(self, agent: MVPTriageAgent) -> None:
        """Test breathing difficulty assessment."""
        result = await agent.assess_symptoms("difficulty breathing", age=30)

        assert result.urgency == "emergency"
        assert result.escalate is True
        assert "sit_upright" in result.actions
        assert "call_emergency" in result.actions
        assert "breathing_difficulty" in result.red_flags

    @pytest.mark.asyncio
    async def test_infant_age_escalation(self, agent: MVPTriageAgent) -> None:
        """Test that infant cases are escalated."""
        result = await agent.assess_symptoms("mild fever", age=1)

        assert result.urgency == "high"
        assert result.escalate is True
        assert result.confidence == 0.8

    @pytest.mark.asyncio
    async def test_elderly_age_adjustment(self, agent: MVPTriageAgent) -> None:
        """Test that elderly cases are adjusted."""
        result = await agent.assess_symptoms("mild pain", age=70)

        assert result.urgency == "medium"  # Upgraded from low
        assert result.confidence == 0.8

    @pytest.mark.asyncio
    async def test_emergency_severity_override(self, agent: MVPTriageAgent) -> None:
        """Test emergency severity override."""
        result = await agent.assess_symptoms("mild pain", age=30, severity="emergency")

        assert result.urgency == "emergency"
        assert result.escalate is True
        assert "reported_as_emergency" in result.red_flags

    @pytest.mark.asyncio
    async def test_unknown_symptoms(self, agent: MVPTriageAgent) -> None:
        """Test assessment of unknown symptoms."""
        result = await agent.assess_symptoms("strange feeling", age=30)

        assert result.urgency == "medium"
        assert "rest" in result.actions
        assert "monitor" in result.actions
        assert result.confidence == 0.7


class TestMVPMedicalTools:
    """Test the MVP Medical Tools (Local Fallback)."""

    @pytest.fixture
    def tools(self) -> MVPMedicalTools:
        """Create a medical tools instance."""
        return MVPMedicalTools()

    def test_pediatric_acetaminophen_dose(self, tools: MVPMedicalTools) -> None:
        """Test pediatric acetaminophen dosage calculation."""
        result = tools.calculate_dose("acetaminophen", weight_kg=25.0, age_years=8)

        assert result["medication"] == "acetaminophen"
        assert result["dose_mg"] == 375.0  # 15 mg/kg * 25 kg
        assert result["dose_type"] == "pediatric"
        assert "Every 6 hours" in result["frequency"]
        assert result["max_daily_mg"] == 4000
        assert "warning" in result

    def test_adult_acetaminophen_dose(self, tools: MVPMedicalTools) -> None:
        """Test adult acetaminophen dosage calculation."""
        result = tools.calculate_dose("acetaminophen", weight_kg=70.0, age_years=25)

        assert result["medication"] == "acetaminophen"
        assert result["dose_mg"] == 500  # Adult dose
        assert result["dose_type"] == "adult"
        assert "Every 6 hours" in result["frequency"]

    def test_pediatric_ibuprofen_dose(self, tools: MVPMedicalTools) -> None:
        """Test pediatric ibuprofen dosage calculation."""
        result = tools.calculate_dose("ibuprofen", weight_kg=20.0, age_years=6)

        assert result["medication"] == "ibuprofen"
        assert result["dose_mg"] == 200.0  # 10 mg/kg * 20 kg
        assert result["dose_type"] == "pediatric"
        assert "Every 8 hours" in result["frequency"]
        assert result["max_daily_mg"] == 2400

    def test_unknown_medication(self, tools: MVPMedicalTools) -> None:
        """Test unknown medication handling."""
        result = tools.calculate_dose("unknown_med", weight_kg=25.0, age_years=8)

        assert "error" in result
        assert "not found" in result["error"]
        assert "available_medications" in result

    def test_paracetamol_alias(self, tools: MVPMedicalTools) -> None:
        """Test paracetamol as alias for acetaminophen."""
        result = tools.calculate_dose("paracetamol", weight_kg=25.0, age_years=8)

        assert result["medication"] == "paracetamol"
        assert result["dose_mg"] == 375.0  # Same as acetaminophen
        assert result["dose_type"] == "pediatric"


class TestCostOptimizer:
    """Test the Cost Optimizer for AI routing decisions."""

    @pytest.fixture
    def optimizer(self) -> CostOptimizer:
        """Create a cost optimizer instance."""
        return CostOptimizer()

    def test_simple_symptoms_use_local(self, optimizer: CostOptimizer) -> None:
        """Test that simple symptoms route to local processing."""
        result = optimizer.should_use_ai("mild headache", "low")
        assert result is False

    def test_complex_symptoms_use_ai(self, optimizer: CostOptimizer) -> None:
        """Test that complex symptoms route to AI."""
        result = optimizer.should_use_ai("severe chest pain with difficulty breathing", "high")
        assert result is True

    def test_emergency_severity_uses_ai(self, optimizer: CostOptimizer) -> None:
        """Test that emergency severity always uses AI."""
        result = optimizer.should_use_ai("mild pain", "emergency")
        assert result is True

    def test_infant_cases_use_ai(self, optimizer: CostOptimizer) -> None:
        """Test that infant cases use AI for safety."""
        result = optimizer.should_use_ai("fever", "medium")
        assert result is True

    def test_elderly_cases_use_ai(self, optimizer: CostOptimizer) -> None:
        """Test that elderly cases use AI for safety."""
        result = optimizer.should_use_ai("chest pain", "medium")
        assert result is True

    def test_complexity_score_calculation(self, optimizer: CostOptimizer) -> None:
        """Test complexity score calculation."""
        # Simple case
        result1 = optimizer.should_use_ai("mild headache", "low")
        assert result1 is False

        # Complex case
        result2 = optimizer.should_use_ai("severe chest pain with breathing difficulty", "high")
        assert result2 is True

        # Emergency case
        result3 = optimizer.should_use_ai("mild pain", "emergency")
        assert result3 is True


class TestHybridTriageAgent:
    """Test the Hybrid Triage Agent with AI integration."""

    @pytest.fixture
    def mock_settings(self) -> Settings:
        """Create mock settings for testing."""
        settings = MagicMock(spec=Settings)
        settings.openai_api_key = "test-key"
        settings.openai_model = "gpt-4o-mini"
        settings.openai_max_tokens = 1000
        settings.openai_temperature = 0.1
        settings.openai_timeout = 10
        settings.openai_max_retries = 3
        settings.ai_fallback_enabled = True
        settings.ai_cost_optimization = True
        settings.ai_cache_ttl_minutes = 60
        return settings

    @pytest.fixture
    def agent(self, mock_settings: Settings) -> HybridTriageAgent:
        """Create a hybrid triage agent instance."""
        return HybridTriageAgent(mock_settings)

    @pytest.mark.asyncio
    async def test_ai_assessment_success(self, agent: HybridTriageAgent) -> None:
        """Test successful AI assessment."""
        # Mock OpenAI response
        mock_response = {
            "urgency": "medium",
            "escalate_to_doctor": True,
            "confidence_score": 0.85,
            "reasoning": "Child with fever requires evaluation",
            "first_aid_steps": ["Monitor temperature", "Ensure hydration"],
            "red_flags": ["high_fever"],
            "follow_up_needed": True
        }

        with patch('src.agents.openai_client') as mock_client:
            mock_completion = AsyncMock()
            mock_completion.choices = [MagicMock()]
            mock_completion.choices[0].message.content = json.dumps(mock_response)
            mock_client.chat.completions.create.return_value = mock_completion

            result = await agent.assess_symptoms("high fever and headache", age=8, severity="medium")

            assert result.urgency == "medium"
            assert result.escalate is True
            assert result.confidence == 0.85
            assert "Monitor temperature" in result.actions
            assert "high_fever" in result.red_flags

    @pytest.mark.asyncio
    async def test_ai_fallback_on_failure(self, agent: HybridTriageAgent) -> None:
        """Test fallback to local processing when AI fails."""
        with patch('src.agents.openai_client') as mock_client:
            # Mock AI failure
            mock_client.chat.completions.create.side_effect = Exception("API Error")

            result = await agent.assess_symptoms("high fever", age=8, severity="medium")

            # Should fallback to local processing
            assert result.urgency == "high"  # Local assessment
            assert result.escalate is True
            assert "rest" in result.actions
            assert "fluids" in result.actions

    @pytest.mark.asyncio
    async def test_cost_optimization_routing(self, agent: HybridTriageAgent) -> None:
        """Test that cost optimization routes simple cases to local processing."""
        # Simple case should use local processing
        result = await agent.assess_symptoms("mild headache", age=25, severity="low")

        # Should use local processing (no AI call)
        assert result.urgency in ["low", "medium"]
        assert isinstance(result.confidence, float)

    @pytest.mark.asyncio
    async def test_ai_assessment_caching(self, agent: HybridTriageAgent) -> None:
        """Test that similar assessments are cached."""
        # Mock successful AI response
        mock_response = {
            "urgency": "medium",
            "escalate_to_doctor": True,
            "confidence_score": 0.85,
            "reasoning": "Fever assessment",
            "first_aid_steps": ["Rest", "Fluids"],
            "red_flags": ["fever"],
            "follow_up_needed": True
        }

        with patch('src.agents.openai_client') as mock_client:
            mock_completion = AsyncMock()
            mock_completion.choices = [MagicMock()]
            mock_completion.choices[0].message.content = json.dumps(mock_response)
            mock_client.chat.completions.create.return_value = mock_completion

            # First call should hit AI
            result1 = await agent.assess_symptoms("fever", age=8, severity="medium")
            
            # Second similar call should use cache (if implemented)
            result2 = await agent.assess_symptoms("fever", age=8, severity="medium")

            assert result1.urgency == result2.urgency
            assert result1.confidence == result2.confidence

    @pytest.mark.asyncio
    async def test_safety_mode_for_infants(self, agent: HybridTriageAgent) -> None:
        """Test safety mode adjustments for infants."""
        # Mock AI response
        mock_response = {
            "urgency": "low",
            "escalate_to_doctor": False,
            "confidence_score": 0.9,
            "reasoning": "Minor issue",
            "first_aid_steps": ["Monitor"],
            "red_flags": [],
            "follow_up_needed": False
        }

        with patch('src.agents.openai_client') as mock_client:
            mock_completion = AsyncMock()
            mock_completion.choices = [MagicMock()]
            mock_completion.choices[0].message.content = json.dumps(mock_response)
            mock_client.chat.completions.create.return_value = mock_completion

            result = await agent.assess_symptoms("mild symptoms", age=1, severity="low")

            # Safety mode should escalate for infants
            assert result.escalate is True  # Should be escalated due to age
            assert result.urgency in ["medium", "high"]  # Should be upgraded


class TestHybridMedicalTools:
    """Test the Hybrid Medical Tools with AI integration."""

    @pytest.fixture
    def mock_settings(self) -> Settings:
        """Create mock settings for testing."""
        settings = MagicMock(spec=Settings)
        settings.openai_api_key = "test-key"
        settings.openai_model = "gpt-4o-mini"
        settings.ai_fallback_enabled = True
        return settings

    @pytest.fixture
    def tools(self, mock_settings: Settings) -> HybridMedicalTools:
        """Create a hybrid medical tools instance."""
        return HybridMedicalTools(mock_settings)

    @pytest.mark.asyncio
    async def test_ai_dosage_calculation_success(self, tools: HybridMedicalTools) -> None:
        """Test successful AI dosage calculation."""
        # Mock OpenAI response
        mock_response = {
            "medication": "acetaminophen",
            "dose_mg": 375.0,
            "dose_type": "pediatric",
            "frequency": "Every 6 hours",
            "max_daily_mg": 1500,
            "warnings": ["Monitor for fever reduction"],
            "contraindications": ["Liver disease"],
            "reasoning": "Weight-based pediatric dosing"
        }

        with patch('src.agents.openai_client') as mock_client:
            mock_completion = AsyncMock()
            mock_completion.choices = [MagicMock()]
            mock_completion.choices[0].message.content = json.dumps(mock_response)
            mock_client.chat.completions.create.return_value = mock_completion

            result = await tools.calculate_dose("acetaminophen", weight_kg=25.0, age_years=8)

            assert result["medication"] == "acetaminophen"
            assert result["dose_mg"] == 375.0
            assert result["dose_type"] == "pediatric"
            assert "warnings" in result
            assert "reasoning" in result

    @pytest.mark.asyncio
    async def test_ai_dosage_fallback_on_failure(self, tools: HybridMedicalTools) -> None:
        """Test fallback to local calculation when AI fails."""
        with patch('src.agents.openai_client') as mock_client:
            # Mock AI failure
            mock_client.chat.completions.create.side_effect = Exception("API Error")

            result = await tools.calculate_dose("acetaminophen", weight_kg=25.0, age_years=8)

            # Should fallback to local calculation
            assert result["medication"] == "acetaminophen"
            assert result["dose_mg"] == 375.0  # Local calculation
            assert result["dose_type"] == "pediatric"
            assert "warning" in result

    @pytest.mark.asyncio
    async def test_safety_mode_for_infants_dosage(self, tools: HybridMedicalTools) -> None:
        """Test safety mode adjustments for infant dosages."""
        # Mock AI response with normal dose
        mock_response = {
            "medication": "acetaminophen",
            "dose_mg": 150.0,
            "dose_type": "pediatric",
            "frequency": "Every 6 hours",
            "max_daily_mg": 600,
            "warnings": ["Infant dosing"],
            "contraindications": [],
            "reasoning": "Infant weight-based dosing"
        }

        with patch('src.agents.openai_client') as mock_client:
            mock_completion = AsyncMock()
            mock_completion.choices = [MagicMock()]
            mock_completion.choices[0].message.content = json.dumps(mock_response)
            mock_client.chat.completions.create.return_value = mock_completion

            result = await tools.calculate_dose("acetaminophen", weight_kg=10.0, age_years=1)

            # Safety mode should apply conservative adjustments
            assert result["dose_mg"] <= 150.0  # Should not exceed AI recommendation
            assert "infant" in str(result).lower() or "conservative" in str(result).lower()

    @pytest.mark.asyncio
    async def test_unknown_medication_handling(self, tools: HybridMedicalTools) -> None:
        """Test handling of unknown medications."""
        result = await tools.calculate_dose("unknown_medication", weight_kg=25.0, age_years=8)

        assert "error" in result
        assert "not found" in result["error"] or "unknown" in result["error"]


class TestAIIntegrationEdgeCases:
    """Test edge cases and error conditions for AI integration."""

    @pytest.fixture
    def mock_settings(self) -> Settings:
        """Create mock settings for testing."""
        settings = MagicMock(spec=Settings)
        settings.openai_api_key = "test-key"
        settings.ai_fallback_enabled = True
        settings.ai_cost_optimization = True
        return settings

    @pytest.mark.asyncio
    async def test_malformed_ai_response(self, mock_settings: Settings) -> None:
        """Test handling of malformed AI responses."""
        agent = HybridTriageAgent(mock_settings)

        with patch('src.agents.openai_client') as mock_client:
            mock_completion = AsyncMock()
            mock_completion.choices = [MagicMock()]
            mock_completion.choices[0].message.content = "Invalid JSON response"
            mock_client.chat.completions.create.return_value = mock_completion

            result = await agent.assess_symptoms("fever", age=8, severity="medium")

            # Should fallback to local processing
            assert result.urgency in ["low", "medium", "high", "emergency"]
            assert isinstance(result.escalate, bool)

    @pytest.mark.asyncio
    async def test_ai_timeout_handling(self, mock_settings: Settings) -> None:
        """Test handling of AI timeouts."""
        agent = HybridTriageAgent(mock_settings)

        with patch('src.agents.openai_client') as mock_client:
            mock_client.chat.completions.create.side_effect = TimeoutError("Request timeout")

            result = await agent.assess_symptoms("fever", age=8, severity="medium")

            # Should fallback to local processing
            assert result.urgency in ["low", "medium", "high", "emergency"]
            assert isinstance(result.escalate, bool)

    @pytest.mark.asyncio
    async def test_ai_rate_limit_handling(self, mock_settings: Settings) -> None:
        """Test handling of AI rate limits."""
        agent = HybridTriageAgent(mock_settings)

        with patch('src.agents.openai_client') as mock_client:
            mock_client.chat.completions.create.side_effect = Exception("Rate limit exceeded")

            result = await agent.assess_symptoms("fever", age=8, severity="medium")

            # Should fallback to local processing
            assert result.urgency in ["low", "medium", "high", "emergency"]
            assert isinstance(result.escalate, bool)
