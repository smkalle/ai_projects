"""
Tests for all Gemini API demo modules.

All google.genai calls are fully mocked — no credentials or network required.
Run with:
    python -m pytest tests/test_demos.py -v
"""

import sys
import os
from unittest.mock import MagicMock, patch, call

import pytest

# ---------------------------------------------------------------------------
# Add repo root to sys.path so `demos.*` and `main` are importable.
# ---------------------------------------------------------------------------
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


# ---------------------------------------------------------------------------
# Stub google.genai before any demo module is imported.
# Each test gets a fresh set of stubs via the autouse fixture.
# ---------------------------------------------------------------------------

def _build_stubs():
    mock_types = MagicMock(name="types")
    # Make types.GenerateContentConfig / SafetySetting / Tool etc. return
    # a MagicMock when called (i.e. they act like constructors).
    for attr in (
        "GenerateContentConfig",
        "EmbedContentConfig",
        "SafetySetting",
        "Tool",
        "ToolCodeExecution",
        "GoogleSearch",
        "ThinkingConfig",
        "ThinkingLevel",
        "HarmCategory",
        "HarmBlockThreshold",
    ):
        setattr(mock_types, attr, MagicMock(name=f"types.{attr}"))

    mock_genai = MagicMock(name="google.genai", types=mock_types)
    mock_google = MagicMock(name="google")
    mock_google.genai = mock_genai

    return mock_google, mock_genai, mock_types


@pytest.fixture(autouse=True)
def mock_genai_modules():
    """Inject google / google.genai / google.genai.types stubs for every test."""
    mock_google, mock_genai, mock_types = _build_stubs()
    sys.modules["google"] = mock_google
    sys.modules["google.genai"] = mock_genai
    sys.modules["google.genai.types"] = mock_types

    # Also clear any previously-imported demo modules so they re-import
    # with the fresh stubs.
    for key in list(sys.modules):
        if key.startswith("demos.") or key == "demos":
            sys.modules.pop(key, None)

    yield mock_google, mock_genai, mock_types

    for key in list(sys.modules):
        if key.startswith(("google", "demos")):
            sys.modules.pop(key, None)


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def _make_response(text="Gemini: OK"):
    resp = MagicMock(name="response")
    resp.text = text
    resp.candidates = []
    resp.function_calls = None
    resp.parsed = None
    resp.executable_code = None
    resp.code_execution_result = None
    return resp


def _make_client(response=None):
    client = MagicMock(name="client")
    resp = response or _make_response()
    client.models.generate_content.return_value = resp
    client.models.generate_content_stream.return_value = iter([resp])
    return client, resp


# ---------------------------------------------------------------------------
# 1. Text generation
# ---------------------------------------------------------------------------

class TestTextGeneration:
    def test_uses_default_prompt(self, capsys):
        client, resp = _make_client()
        from demos import text_generation
        text_generation.run(client)
        client.models.generate_content.assert_called_once()
        assert resp.text in capsys.readouterr().out

    def test_custom_prompt_and_model(self, capsys):
        client, resp = _make_client()
        from demos import text_generation
        text_generation.run(client, model="gemini-3.1-pro-preview", prompt="Hello")
        kwargs = client.models.generate_content.call_args.kwargs
        assert kwargs["model"] == "gemini-3.1-pro-preview"
        assert kwargs["contents"] == "Hello"


# ---------------------------------------------------------------------------
# 2. Chat
# ---------------------------------------------------------------------------

class TestChat:
    def test_sends_two_turns(self):
        client = MagicMock(name="client")
        chat_session = MagicMock(name="chat")
        chat_session.send_message.return_value = _make_response("story")
        client.chats.create.return_value = chat_session

        from demos import chat
        chat.run(client)

        assert chat_session.send_message.call_count == 2

    def test_custom_first_prompt(self):
        client = MagicMock(name="client")
        chat_session = MagicMock(name="chat")
        chat_session.send_message.return_value = _make_response("ok")
        client.chats.create.return_value = chat_session

        from demos import chat
        chat.run(client, prompt="Custom turn one")

        first_call_arg = chat_session.send_message.call_args_list[0].args[0]
        assert first_call_arg == "Custom turn one"


# ---------------------------------------------------------------------------
# 3. Streaming
# ---------------------------------------------------------------------------

class TestStreaming:
    def test_consumes_stream(self, capsys):
        chunks = [_make_response("Hello "), _make_response("world")]
        client = MagicMock(name="client")
        client.models.generate_content_stream.return_value = iter(chunks)

        from demos import streaming
        streaming.run(client)

        out = capsys.readouterr().out
        assert "Hello " in out
        assert "world" in out
        client.models.generate_content_stream.assert_called_once()

    def test_custom_prompt_forwarded(self):
        client = MagicMock(name="client")
        client.models.generate_content_stream.return_value = iter([_make_response("x")])

        from demos import streaming
        streaming.run(client, prompt="My custom prompt")

        kwargs = client.models.generate_content_stream.call_args.kwargs
        assert kwargs["contents"] == "My custom prompt"


# ---------------------------------------------------------------------------
# 4. Structured output
# ---------------------------------------------------------------------------

class TestStructuredOutput:
    def test_parsed_recipes_printed(self, capsys):
        resp = _make_response()
        recipe = MagicMock()
        recipe.recipe_name = "Chocolate Chip Cookies"
        recipe.ingredients = ["flour", "sugar", "butter", "chocolate chips"]
        resp.parsed = [recipe]

        client, _ = _make_client(response=resp)
        from demos import structured_output
        structured_output.run(client)

        out = capsys.readouterr().out
        assert "Chocolate Chip Cookies" in out

    def test_falls_back_to_text_when_no_parsed(self, capsys):
        resp = _make_response(text='[{"recipe_name": "test", "ingredients": []}]')
        resp.parsed = None
        client, _ = _make_client(response=resp)

        from demos import structured_output
        structured_output.run(client)

        out = capsys.readouterr().out
        assert "recipe_name" in out

    def test_config_passes_json_schema(self, mock_genai_modules):
        _, _, mock_types = mock_genai_modules
        resp = _make_response()
        resp.parsed = []
        client, _ = _make_client(response=resp)

        from demos import structured_output
        structured_output.run(client)

        mock_types.GenerateContentConfig.assert_called_once()
        call_kwargs = mock_types.GenerateContentConfig.call_args.kwargs
        assert call_kwargs["response_mime_type"] == "application/json"


# ---------------------------------------------------------------------------
# 5. Function calling
# ---------------------------------------------------------------------------

class TestFunctionCalling:
    def test_executes_tool_calls(self, capsys):
        resp = _make_response()
        fc = MagicMock(name="function_call")
        fc.name = "get_current_weather"
        fc.args = {"location": "Boston"}
        resp.function_calls = [fc]

        client, _ = _make_client(response=resp)
        from demos import function_calling
        function_calling.run(client)

        out = capsys.readouterr().out
        assert "Boston" in out
        assert "Snowing" in out

    def test_prints_text_when_no_tool_calls(self, capsys):
        resp = _make_response(text="It is sunny today.")
        resp.function_calls = None
        client, _ = _make_client(response=resp)

        from demos import function_calling
        function_calling.run(client)

        assert "sunny" in capsys.readouterr().out

    def test_weather_tool_boston(self):
        from demos.function_calling import get_current_weather
        result = get_current_weather("Boston, MA")
        assert "28" in result

    def test_weather_tool_tokyo(self):
        from demos.function_calling import get_current_weather
        result = get_current_weather("Tokyo")
        assert "Tokyo" or "68" in result

    def test_weather_tool_unknown(self):
        from demos.function_calling import get_current_weather
        result = get_current_weather("Unknown City")
        assert "72" in result


# ---------------------------------------------------------------------------
# 6. Code execution
# ---------------------------------------------------------------------------

class TestCodeExecution:
    def test_prints_code_and_result(self, capsys):
        resp = _make_response()
        resp.executable_code = "print(sum(range(100)))"
        resp.code_execution_result = "4950"

        client, _ = _make_client(response=resp)
        from demos import code_execution
        code_execution.run(client)

        out = capsys.readouterr().out
        assert "print(sum" in out
        assert "4950" in out

    def test_falls_back_to_text(self, capsys):
        resp = _make_response(text="The answer is 42.")
        resp.executable_code = None
        resp.code_execution_result = None
        client, _ = _make_client(response=resp)

        from demos import code_execution
        code_execution.run(client)

        assert "42" in capsys.readouterr().out

    def test_code_execution_tool_passed(self, mock_genai_modules):
        _, _, mock_types = mock_genai_modules
        resp = _make_response()
        resp.executable_code = "x=1"
        resp.code_execution_result = "1"
        client, _ = _make_client(response=resp)

        from demos import code_execution
        code_execution.run(client)

        mock_types.Tool.assert_called_once()
        mock_types.ToolCodeExecution.assert_called_once()


# ---------------------------------------------------------------------------
# 7. Embeddings
# ---------------------------------------------------------------------------

class TestEmbeddings:
    def _make_embed_response(self, num=3, dim=5):
        resp = MagicMock(name="embed_response")
        resp.embeddings = [
            MagicMock(values=[float(i + j * 0.1) for j in range(dim)])
            for i in range(num)
        ]
        return resp

    def test_embed_called_with_correct_args(self):
        client = MagicMock(name="client")
        client.models.embed_content.return_value = self._make_embed_response()

        from demos import embeddings
        embeddings.run(client)

        client.models.embed_content.assert_called_once()
        kwargs = client.models.embed_content.call_args.kwargs
        assert kwargs["model"] == "gemini-embedding-001"
        assert isinstance(kwargs["contents"], list)

    def test_cosine_similarity_computed(self, capsys):
        client = MagicMock(name="client")
        client.models.embed_content.return_value = self._make_embed_response(num=2)

        from demos import embeddings
        embeddings.run(client)

        assert "Cosine similarity" in capsys.readouterr().out

    def test_cosine_similarity_helper(self):
        from demos.embeddings import cosine_similarity
        a = [1.0, 0.0]
        b = [1.0, 0.0]
        assert abs(cosine_similarity(a, b) - 1.0) < 1e-6

        c = [0.0, 1.0]
        assert abs(cosine_similarity(a, c)) < 1e-6

    def test_custom_prompt_prepended(self):
        client = MagicMock(name="client")
        client.models.embed_content.return_value = self._make_embed_response()

        from demos import embeddings
        embeddings.run(client, prompt="My custom query")

        contents = client.models.embed_content.call_args.kwargs["contents"]
        assert contents[0] == "My custom query"


# ---------------------------------------------------------------------------
# 8. Thinking / Reasoning
# ---------------------------------------------------------------------------

class TestThinking:
    def test_splits_thought_from_answer(self, capsys):
        resp = _make_response()
        thought_part = MagicMock()
        thought_part.thought = True
        thought_part.text = "Let me reason..."
        answer_part = MagicMock()
        answer_part.thought = False
        answer_part.text = "The answer is $0.05."

        content = MagicMock()
        content.parts = [thought_part, answer_part]
        candidate = MagicMock()
        candidate.content = content
        resp.candidates = [candidate]

        client, _ = _make_client(response=resp)
        from demos import thinking
        thinking.run(client)

        out = capsys.readouterr().out
        assert "Let me reason" in out
        assert "$0.05" in out
        assert "Reasoning" in out
        assert "Final answer" in out

    def test_falls_back_to_text_when_no_candidates(self, capsys):
        resp = _make_response(text="The answer is 5 cents.")
        resp.candidates = []
        client, _ = _make_client(response=resp)

        from demos import thinking
        thinking.run(client)

        assert "5 cents" in capsys.readouterr().out

    def test_thinking_config_passed(self, mock_genai_modules):
        _, _, mock_types = mock_genai_modules
        resp = _make_response()
        resp.candidates = []
        client, _ = _make_client(response=resp)

        from demos import thinking
        thinking.run(client)

        mock_types.ThinkingConfig.assert_called_once()


# ---------------------------------------------------------------------------
# 9. Safety
# ---------------------------------------------------------------------------

class TestSafety:
    def test_prints_text_response(self, capsys):
        resp = _make_response(text="Why did the dev cross the road? To get to the other IDE.")
        resp.candidates = []
        client, _ = _make_client(response=resp)

        from demos import safety
        safety.run(client)

        assert "IDE" in capsys.readouterr().out

    def test_reports_blocked_response(self, capsys):
        resp = MagicMock(name="blocked_response")
        resp.text = None
        candidate = MagicMock()
        candidate.finish_reason = "SAFETY"
        candidate.safety_ratings = []
        resp.candidates = [candidate]

        client, _ = _make_client(response=resp)
        from demos import safety
        safety.run(client)

        assert "BLOCKED" in capsys.readouterr().out

    def test_safety_settings_sent(self, mock_genai_modules):
        _, _, mock_types = mock_genai_modules
        resp = _make_response()
        resp.candidates = []
        client, _ = _make_client(response=resp)

        from demos import safety
        safety.run(client)

        # GenerateContentConfig must have been called with safety_settings
        mock_types.GenerateContentConfig.assert_called_once()
        call_kwargs = mock_types.GenerateContentConfig.call_args.kwargs
        assert "safety_settings" in call_kwargs
        assert len(call_kwargs["safety_settings"]) == 3

    def test_prints_safety_ratings(self, capsys):
        resp = _make_response(text="A joke.")
        rating = MagicMock()
        rating.category = "HARM_CATEGORY_DANGEROUS_CONTENT"
        rating.probability = "NEGLIGIBLE"
        rating.blocked = False
        candidate = MagicMock()
        candidate.safety_ratings = [rating]
        resp.candidates = [candidate]

        client, _ = _make_client(response=resp)
        from demos import safety
        safety.run(client)

        out = capsys.readouterr().out
        assert "NEGLIGIBLE" in out


# ---------------------------------------------------------------------------
# 10. Search grounding
# ---------------------------------------------------------------------------

class TestSearchGrounding:
    def test_calls_generate_with_search_tool(self, mock_genai_modules):
        _, _, mock_types = mock_genai_modules
        resp = _make_response(text="Fusion energy progress...")
        resp.candidates = []
        client, _ = _make_client(response=resp)

        from demos import search_grounding
        search_grounding.run(client)

        mock_types.Tool.assert_called_once()
        mock_types.GoogleSearch.assert_called_once()

    def test_prints_response_text(self, capsys):
        resp = _make_response(text="Latest fusion research shows...")
        resp.candidates = []
        client, _ = _make_client(response=resp)

        from demos import search_grounding
        search_grounding.run(client)

        assert "fusion" in capsys.readouterr().out.lower()

    def test_prints_grounding_metadata(self, capsys):
        resp = _make_response(text="Answer.")
        meta = MagicMock()
        meta.web_search_queries = ["fusion energy 2025"]
        web = MagicMock()
        web.title = "Nature: Fusion Breakthrough"
        chunk = MagicMock()
        chunk.web = web
        meta.grounding_chunks = [chunk]
        candidate = MagicMock()
        candidate.grounding_metadata = meta
        resp.candidates = [candidate]

        client, _ = _make_client(response=resp)
        from demos import search_grounding
        search_grounding.run(client)

        out = capsys.readouterr().out
        assert "fusion energy 2025" in out
        assert "Nature" in out


# ---------------------------------------------------------------------------
# CLI integration (main.py)
# ---------------------------------------------------------------------------

class TestCLI:
    def test_routes_to_text_demo(self):
        with patch("main.get_client") as mock_get_client, \
             patch("main.run_demo") as mock_run:
            mock_get_client.return_value = MagicMock()
            import main
            result = main.main(["text"])
            mock_run.assert_called_once()
            assert mock_run.call_args.args[0] == "text"
            assert result == 0

    def test_unknown_command_exits(self):
        import main
        with pytest.raises(SystemExit):
            main.main(["unknown_command"])

    def test_all_command_runs_every_demo(self):
        with patch("main.get_client") as mock_get_client, \
             patch("main.run_demo") as mock_run:
            mock_get_client.return_value = MagicMock()
            import main
            result = main.main(["all"])
            assert mock_run.call_count == len(main.DEMOS)
            assert result == 0

    def test_all_command_returns_1_on_error(self):
        with patch("main.get_client") as mock_get_client, \
             patch("main.run_demo", side_effect=RuntimeError("boom")):
            mock_get_client.return_value = MagicMock()
            import main
            result = main.main(["all"])
            assert result == 1

    def test_model_flag_forwarded(self):
        with patch("main.get_client") as mock_get_client, \
             patch("main.run_demo") as mock_run:
            mock_get_client.return_value = MagicMock()
            import main
            main.main(["text", "--model", "gemini-3.1-pro-preview"])
            assert mock_run.call_args.kwargs["model"] == "gemini-3.1-pro-preview"

    def test_prompt_flag_forwarded(self):
        with patch("main.get_client") as mock_get_client, \
             patch("main.run_demo") as mock_run:
            mock_get_client.return_value = MagicMock()
            import main
            main.main(["text", "--prompt", "Custom question"])
            assert mock_run.call_args.kwargs["prompt"] == "Custom question"


# ---------------------------------------------------------------------------
# get_client() — dotenv / auth resolution
# ---------------------------------------------------------------------------

class TestGetClient:
    def test_uses_gemini_api_key_when_set(self, mock_genai_modules):
        _, mock_genai, _ = mock_genai_modules
        with patch.dict(os.environ, {"GEMINI_API_KEY": "test-key-123"}, clear=False):
            sys.modules.pop("main", None)
            import main
            main.get_client()
            mock_genai.Client.assert_called_with(api_key="test-key-123")

    def test_falls_back_to_default_client_when_no_key(self, mock_genai_modules):
        _, mock_genai, _ = mock_genai_modules
        import main
        mock_genai.Client.reset_mock()
        with patch("main.os.getenv", return_value=None):
            main.get_client()
        mock_genai.Client.assert_called_with()


# ---------------------------------------------------------------------------
# 11. Insurance Claims Intake Workflow
# ---------------------------------------------------------------------------

class TestInsuranceClaims:
    def _claim_resp(self, **fields):
        """Return a mock response whose .parsed is a plain dict."""
        resp = _make_response()
        resp.parsed = fields
        return resp

    def _full_resp(self, claim=None, classification=None, coverage=None, fraud=None, checklist=None):
        """Five mock responses for the five LLM steps, returned in sequence."""
        claim = claim or {}
        classification = classification or {"claim_type": "auto", "severity": "medium", "policy_line": "Personal Auto"}
        coverage = coverage or {"coverage_applies": True, "evidence_required": ["Police report"], "deductible_applies": True, "notes": "Covered."}
        fraud = fraud or {"fraud_risk": False, "siu_referral_required": False, "safety_concerns": False, "escalation_type": "ready_for_adjuster"}
        checklist = checklist or {"required_documents": ["Police report", "Photos"], "optional_documents": ["Medical records"]}
        resp1 = self._claim_resp(**claim)
        resp2 = self._claim_resp(**classification)
        resp3 = self._claim_resp(**coverage)
        resp4 = self._claim_resp(**fraud)
        resp5 = self._claim_resp(**checklist)
        return [resp1, resp2, resp3, resp4, resp5]

    def test_extraction_output_printed(self, capsys):
        responses = self._full_resp(
            claim={"claimant_name": "Jane Doe", "policy_number": "P-999",
                   "incident_date": "2024-12-01", "incident_location": "I-95",
                   "incident_description": "Rear-ended at stop.", "damage_items": ["Bumper"]},
        )
        client = MagicMock(name="client")
        client.models.generate_content.side_effect = responses
        from demos import insurance_claims
        insurance_claims.run(client)
        out = capsys.readouterr().out
        assert "Jane Doe" in out
        assert "P-999" in out
        assert client.models.generate_content.call_count == 5

    def test_validation_detects_missing_fields(self, capsys):
        responses = self._full_resp(
            claim={"claimant_name": "Bob", "policy_number": "X",
                   "incident_date": None,  # missing
                   "incident_location": "",  # missing
                   "incident_description": "Crash"},
        )
        client = MagicMock(name="client")
        client.models.generate_content.side_effect = responses
        from demos import insurance_claims
        insurance_claims.run(client)
        out = capsys.readouterr().out
        assert "MISSING" in out
        assert "incident_date" in out
        assert "incident_location" in out

    def test_routing_siu_flag(self, capsys):
        responses = self._full_resp(
            fraud={"fraud_risk": True, "siu_referral_required": True,
                   "safety_concerns": False, "escalation_type": "special_investigation"},
        )
        client = MagicMock(name="client")
        client.models.generate_content.side_effect = responses
        from demos import insurance_claims
        insurance_claims.run(client)
        out = capsys.readouterr().out
        assert "SIU" in out
        assert "special_investigation" in out
        assert "priority : 90" in out

    def test_final_packet_printed(self, capsys):
        responses = self._full_resp(
            claim={"claimant_name": "John Doe", "policy_number": "POL-2024-789456",
                   "incident_date": "last Tuesday", "incident_location": "I-95 exit 42",
                   "incident_description": "Car accident", "damage_items": ["Bumper", "Door"]},
        )
        client = MagicMock(name="client")
        client.models.generate_content.side_effect = responses
        from demos import insurance_claims
        insurance_claims.run(client)
        out = capsys.readouterr().out
        assert "FINAL CLAIM INTAKE PACKET" in out
        assert "Ready for human adjuster review" in out

    def test_config_uses_response_schema_and_json_mime(self, mock_genai_modules):
        _, _, mock_types = mock_genai_modules
        responses = self._full_resp()
        client = MagicMock(name="client")
        client.models.generate_content.side_effect = responses
        from demos import insurance_claims
        insurance_claims.run(client)
        mock_types.GenerateContentConfig.assert_called()
        call_kwargs = mock_types.GenerateContentConfig.call_args.kwargs
        assert call_kwargs.get("response_mime_type") == "application/json"
        assert "response_schema" in call_kwargs or "responseJsonSchema" in call_kwargs
