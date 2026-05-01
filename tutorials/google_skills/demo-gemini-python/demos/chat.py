"""
Section 2 — Chat (Multi-turn Conversations)
Maintain conversation history across multiple turns using a chat session.
"""

DEFAULT_MODEL = "gemini-3-flash-preview"


def run(client, *, model: str = DEFAULT_MODEL, prompt: str | None = None, **_) -> None:
    print(f"Model: {model}\n")

    chat_session = client.chats.create(model=model)

    # Two-turn conversation; first turn uses --prompt if provided.
    turns = [
        prompt or "Tell me a one-sentence story about a robot.",
        "Now rewrite it as a horror story.",
    ]

    for user_input in turns:
        print(f"You    : {user_input}")
        response = chat_session.send_message(user_input)
        print(f"Gemini : {response.text}\n")
