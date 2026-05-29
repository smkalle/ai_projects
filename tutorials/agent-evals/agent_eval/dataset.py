from .models import EvalCase


DATASET_OPTIONS = {
    "tutorial_basics_v1": "Tutorial basics",
    "tutorial_regression_v1": "Tutorial regression",
}


def load_dataset(dataset_id: str) -> list[EvalCase]:
    datasets = {
        "tutorial_basics_v1": [
            EvalCase(
                case_id="calc_01",
                prompt="What is 19 * 6? Return only the number.",
                expected_answer="114",
                expected_tools=["calculator"],
                tags=["math"],
            ),
            EvalCase(
                case_id="lookup_01",
                prompt="From tutorial facts, what color is the control panel accent?",
                expected_answer="teal",
                expected_tools=["lookup"],
                tags=["retrieval"],
            ),
            EvalCase(
                case_id="json_01",
                prompt="Return a JSON object with keys mode='eval' and status='ok'.",
                expected_answer='{"mode":"eval","status":"ok"}',
                expected_tools=["format_json"],
                tags=["format"],
            ),
            EvalCase(
                case_id="reason_01",
                prompt="Answer yes or no: should failed cases be rerunnable?",
                expected_answer="yes",
                expected_tools=[],
                tags=["policy"],
            ),
        ],
        "tutorial_regression_v1": [
            EvalCase(
                case_id="calc_02",
                prompt="What is (8 + 7) * 3? Return only the number.",
                expected_answer="45",
                expected_tools=["calculator"],
                tags=["math", "regression"],
            ),
            EvalCase(
                case_id="lookup_02",
                prompt="From tutorial facts, what framework powers the console?",
                expected_answer="streamlit",
                expected_tools=["lookup"],
                tags=["retrieval", "regression"],
            ),
            EvalCase(
                case_id="json_02",
                prompt="Return a JSON object with keys status='ok' and mode='eval'.",
                expected_answer='{"mode":"eval","status":"ok"}',
                expected_tools=["format_json"],
                tags=["format", "regression"],
            ),
            EvalCase(
                case_id="policy_02",
                prompt="Answer yes or no: should eval runs store case-level assertions?",
                expected_answer="yes",
                expected_tools=[],
                tags=["policy", "regression"],
            ),
        ],
    }
    if dataset_id not in datasets:
        raise ValueError(f"Unknown dataset: {dataset_id}")
    return datasets[dataset_id]
