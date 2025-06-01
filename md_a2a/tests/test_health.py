"""Tests for health check endpoints."""

from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient


class TestHealthEndpoints:
    """Test health check endpoints."""

    def test_health_check(self, client: TestClient) -> None:
        """Test the main health check endpoint."""
        response = client.get("/api/health")

        assert response.status_code == 200
        data = response.json()

        assert "status" in data
        assert "timestamp" in data
        assert "version" in data
        assert "checks" in data

        assert data["version"] == "0.2.0"
        assert data["status"] in ["healthy", "degraded", "unhealthy"]

        # Check that database check is included
        assert "database" in data["checks"]

    def test_readiness_check(self, client: TestClient) -> None:
        """Test the readiness probe endpoint."""
        response = client.get("/api/health/ready")

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "ready"

    def test_liveness_check(self, client: TestClient) -> None:
        """Test the liveness probe endpoint."""
        response = client.get("/api/health/live")

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "alive"


class TestAIHealthEndpoints:
    """Test AI-specific health check endpoints."""

    def test_ai_health_check(self, client: TestClient) -> None:
        """Test the AI service health check endpoint."""
        response = client.get("/api/health/ai")

        assert response.status_code == 200
        data = response.json()

        # Check AI health structure
        assert "status" in data
        assert "ai_service" in data
        assert "cost_tracking" in data
        assert "performance_metrics" in data

        # Check AI service details
        ai_service = data["ai_service"]
        assert "available" in ai_service
        assert "model" in ai_service
        assert "last_success" in ai_service
        assert "success_rate_24h" in ai_service
        assert "avg_response_time_ms" in ai_service
        assert "fallback_rate_24h" in ai_service

        # Check cost tracking
        cost_tracking = data["cost_tracking"]
        assert "total_cost_today_cents" in cost_tracking
        assert "budget_remaining_cents" in cost_tracking
        assert "cost_per_assessment_avg_cents" in cost_tracking

        # Check performance metrics
        performance = data["performance_metrics"]
        assert "total_assessments_24h" in performance
        assert "ai_assessments_24h" in performance
        assert "local_assessments_24h" in performance

    @patch('src.agents.openai_client')
    def test_ai_health_check_with_healthy_ai(self, mock_client, client: TestClient) -> None:
        """Test AI health check when AI service is healthy."""
        # Mock successful AI response
        mock_completion = AsyncMock()
        mock_completion.choices = [MagicMock()]
        mock_completion.choices[0].message.content = '{"test": "response"}'
        mock_client.chat.completions.create.return_value = mock_completion

        response = client.get("/api/health/ai")

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "healthy"
        assert data["ai_service"]["available"] is True

    @patch('src.agents.openai_client')
    def test_ai_health_check_with_unhealthy_ai(self, mock_client, client: TestClient) -> None:
        """Test AI health check when AI service is unhealthy."""
        # Mock AI failure
        mock_client.chat.completions.create.side_effect = Exception("API Error")

        response = client.get("/api/health/ai")

        assert response.status_code == 200
        data = response.json()

        assert data["status"] in ["degraded", "unhealthy"]
        assert data["ai_service"]["available"] is False

    def test_health_metrics_endpoint(self, client: TestClient) -> None:
        """Test the health metrics endpoint."""
        response = client.get("/api/health/metrics")

        assert response.status_code == 200
        data = response.json()

        # Check metrics structure
        assert "system_metrics" in data
        assert "ai_metrics" in data
        assert "database_metrics" in data

        # Check system metrics
        system_metrics = data["system_metrics"]
        assert "uptime_seconds" in system_metrics
        assert "memory_usage_mb" in system_metrics
        assert "cpu_usage_percent" in system_metrics

        # Check AI metrics
        ai_metrics = data["ai_metrics"]
        assert "total_ai_calls" in ai_metrics
        assert "successful_ai_calls" in ai_metrics
        assert "failed_ai_calls" in ai_metrics
        assert "total_cost_cents" in ai_metrics
        assert "avg_response_time_ms" in ai_metrics

        # Check database metrics
        db_metrics = data["database_metrics"]
        assert "total_cases" in db_metrics
        assert "cases_today" in db_metrics
        assert "database_size_mb" in db_metrics

    def test_health_check_includes_ai_status(self, client: TestClient) -> None:
        """Test that main health check includes AI status."""
        response = client.get("/api/health")

        assert response.status_code == 200
        data = response.json()

        # Should include AI service in checks
        assert "ai_service" in data["checks"]
        
        ai_check = data["checks"]["ai_service"]
        assert "status" in ai_check
        assert "response_time_ms" in ai_check

    def test_health_check_with_ai_degraded(self, client: TestClient) -> None:
        """Test health check when AI service is degraded."""
        with patch('src.agents.openai_client') as mock_client:
            # Mock AI failure
            mock_client.chat.completions.create.side_effect = Exception("API Error")

            response = client.get("/api/health")

            assert response.status_code == 200
            data = response.json()

            # Overall status should be degraded when AI fails
            assert data["status"] in ["degraded", "unhealthy"]
            assert data["checks"]["ai_service"]["status"] == "unhealthy"

    def test_cost_tracking_in_health_check(self, client: TestClient) -> None:
        """Test that cost tracking information is included in health checks."""
        response = client.get("/api/health/ai")

        assert response.status_code == 200
        data = response.json()

        cost_tracking = data["cost_tracking"]
        
        # Verify cost tracking fields are present and valid
        assert isinstance(cost_tracking["total_cost_today_cents"], (int, float))
        assert isinstance(cost_tracking["budget_remaining_cents"], (int, float))
        assert isinstance(cost_tracking["cost_per_assessment_avg_cents"], (int, float))
        
        # Cost values should be non-negative
        assert cost_tracking["total_cost_today_cents"] >= 0
        assert cost_tracking["budget_remaining_cents"] >= 0
        assert cost_tracking["cost_per_assessment_avg_cents"] >= 0

    def test_performance_metrics_validation(self, client: TestClient) -> None:
        """Test that performance metrics are valid."""
        response = client.get("/api/health/ai")

        assert response.status_code == 200
        data = response.json()

        ai_service = data["ai_service"]
        
        # Validate success rate
        assert 0.0 <= ai_service["success_rate_24h"] <= 1.0
        
        # Validate fallback rate
        assert 0.0 <= ai_service["fallback_rate_24h"] <= 1.0
        
        # Validate response time
        assert ai_service["avg_response_time_ms"] >= 0

    def test_ai_model_information(self, client: TestClient) -> None:
        """Test that AI model information is included."""
        response = client.get("/api/health/ai")

        assert response.status_code == 200
        data = response.json()

        ai_service = data["ai_service"]
        
        # Should include model information
        assert "model" in ai_service
        assert ai_service["model"] == "gpt-4o-mini"

    def test_health_check_response_time(self, client: TestClient) -> None:
        """Test that health check includes response time information."""
        response = client.get("/api/health")

        assert response.status_code == 200
        data = response.json()

        # Should include response time for health check
        assert "response_time_ms" in data
        assert isinstance(data["response_time_ms"], (int, float))
        assert data["response_time_ms"] >= 0

    def test_database_health_in_ai_check(self, client: TestClient) -> None:
        """Test that database health is considered in AI health check."""
        response = client.get("/api/health/ai")

        assert response.status_code == 200
        data = response.json()

        # Should include database status
        assert "database" in data
        db_status = data["database"]
        assert "status" in db_status
        assert "connection_pool_size" in db_status

    def test_configuration_validation_in_health(self, client: TestClient) -> None:
        """Test that configuration validation is included in health checks."""
        response = client.get("/api/health")

        assert response.status_code == 200
        data = response.json()

        # Should include configuration check
        assert "configuration" in data["checks"]
        config_check = data["checks"]["configuration"]
        assert "status" in config_check
        assert config_check["status"] in ["healthy", "degraded", "unhealthy"]
