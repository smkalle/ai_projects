from dotenv import load_dotenv
import os
import sys
from datetime import datetime
import anthropic


def log(step: str, message: str) -> None:
    """Simple timestamped console logger for learning/debugging."""
    now = datetime.now().strftime("%H:%M:%S")
    print(f"[{now}] [{step}] {message}")


def require_env(name: str) -> str:
    """Read an environment variable and fail loudly if missing."""
    value = os.getenv(name)
    if not value:
        raise RuntimeError(
            f"Missing required environment variable: {name}\n"
            f"Please add it to your .env file."
        )
    return value


def print_divider(title: str = "") -> None:
    line = "=" * 80
    if title:
        print(f"\n{line}\n{title}\n{line}")
    else:
        print(f"\n{line}")


def main() -> None:
    print_divider("MiniMax M2.7 + python-dotenv + Anthropic SDK Tutorial")

    # Step 1: Load environment variables from .env
    log("INIT", "Loading environment variables from .env")
    load_dotenv()

    # Step 2: Read required variables
    log("ENV", "Reading ANTHROPIC_BASE_URL and ANTHROPIC_API_KEY")
    base_url = require_env("ANTHROPIC_BASE_URL")
    api_key = require_env("ANTHROPIC_API_KEY")

    # Optional: show safe debug info
    masked_key = f"{api_key[:6]}...{api_key[-4:]}" if len(api_key) > 10 else "***"
    log("ENV", f"ANTHROPIC_BASE_URL = {base_url}")
    log("ENV", f"ANTHROPIC_API_KEY = {masked_key}")

    # Step 3: Create the client
    log("CLIENT", "Creating Anthropic client configured for MiniMax")
    client = anthropic.Anthropic(
        api_key=api_key,
        base_url=base_url,
    )
    log("CLIENT", "Client created successfully")

    # Step 4: Define the request
    system_prompt = (
        "You are a helpful assistant. "
        "Be clear, concise, and educational in your answers."
    )

    user_text = (
        "Hi, how are you? "
        "Please introduce yourself briefly and explain what you can help with."
    )

    request_payload = {
        "model": "MiniMax-M2.7",
        "max_tokens": 1000,
        "system": system_prompt,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": user_text
                    }
                ]
            }
        ],
    }

    print_divider("Request Preview")
    log("REQUEST", f"Model = {request_payload['model']}")
    log("REQUEST", f"Max tokens = {request_payload['max_tokens']}")
    log("REQUEST", f"System prompt = {system_prompt}")
    log("REQUEST", f"User text = {user_text}")

    # Step 5: Call the API
    print_divider("Calling MiniMax API")
    try:
        log("API", "Sending request to MiniMax...")
        message = client.messages.create(**request_payload)
        log("API", "Response received successfully")
    except Exception as e:
        log("ERROR", f"API call failed: {type(e).__name__}: {e}")
        sys.exit(1)

    # Step 6: Inspect high-level response metadata if available
    print_divider("Response Metadata")
    log("RESPONSE", f"Message object type = {type(message).__name__}")

    # These attributes may vary by SDK version / compatibility layer
    for attr in ["id", "model", "role", "stop_reason", "stop_sequence", "type"]:
        if hasattr(message, attr):
            log("RESPONSE", f"{attr} = {getattr(message, attr)}")

    # Step 7: Parse returned content blocks
    print_divider("Content Blocks")
    if not hasattr(message, "content") or not message.content:
        log("WARN", "No content blocks returned")
        return

    for i, block in enumerate(message.content, start=1):
        block_type = getattr(block, "type", "unknown")
        log("BLOCK", f"Block #{i} type = {block_type}")

        if block_type == "thinking":
            thinking = getattr(block, "thinking", "")
            print("\n--- Thinking Block ---")
            print(thinking)

        elif block_type == "text":
            text = getattr(block, "text", "")
            print("\n--- Text Block ---")
            print(text)

        else:
            print("\n--- Unknown Block ---")
            print(block)

    print_divider("Tutorial Complete")
    log("DONE", "You have successfully called MiniMax-M2.7 using dotenv + detailed logging")


if __name__ == "__main__":
    main()
