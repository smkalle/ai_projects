"""
Section 8 — Code Execution
Let the model write and run Python code to compute a precise answer.
"""

DEFAULT_PROMPT = "Calculate the sum of the first 50 Fibonacci numbers."
DEFAULT_MODEL = "gemini-3-flash-preview"


def run(client, *, model: str = DEFAULT_MODEL, prompt: str | None = None, **_) -> None:
    from google.genai import types  # pylint: disable=import-outside-toplevel

    prompt = prompt or DEFAULT_PROMPT
    print(f"Model : {model}")
    print(f"Prompt: {prompt}\n")

    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config=types.GenerateContentConfig(
            tools=[types.Tool(code_execution=types.ToolCodeExecution())],
        ),
    )

    code = getattr(response, "executable_code", None)
    result = getattr(response, "code_execution_result", None)

    if code:
        print("--- Generated code ---")
        print(code)
    if result:
        print("--- Execution result ---")
        print(result)
    if not code and not result:
        # Model answered without running code (e.g. simple prompt)
        print(response.text)
