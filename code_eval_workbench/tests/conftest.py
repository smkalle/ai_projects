"""
conftest.py — pytest configuration and shared fixtures.

Environment variables are set at the TOP of this file (before any other module
imports) so that when scorer.py is imported at test-module load time,
get_model_config() reads the dummy values and does not attempt real API calls.
"""
import os

os.environ.setdefault("ANTHROPIC_API_KEY", "sk-test-dummy-key-for-unit-tests")
os.environ.setdefault("ANTHROPIC_BASE_URL", "http://localhost:11434")

import pytest  # noqa: E402 (imported after env vars are set)

# Import scorer here so its module-level get_model_config() call uses our env vars.
#-scoring functions that don't need the LLM judge.
import scorer  # noqa: E402


@pytest.fixture(autouse=True)
def patch_llm_judge(monkeypatch):
    """Replace llm_judge_score with a mock so composite_score tests don't need an API."""
    original = scorer.llm_judge_score

    def mock(output, input_dict, reference):
        return 0.85, "Mocked reasoning for unit testing."

    monkeypatch.setattr(scorer, "llm_judge_score", mock)
    yield
    monkeypatch.setattr(scorer, "llm_judge_score", original)
