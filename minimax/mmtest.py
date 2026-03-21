from dotenv import load_dotenv
import os
import anthropic

# Load environment variables
load_dotenv()

# Fetch API key
api_key = os.getenv("ANTHROPIC_API_KEY")

if not api_key:
    raise ValueError("ANTHROPIC_API_KEY not found in environment variables")

# Initialize client with API key
client = anthropic.Anthropic(api_key=api_key)

message = client.messages.create(
    model="MiniMax-M2.7",
    max_tokens=1000,
    system="You are a helpful assistant.",
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "Hi, how are you?"
                }
            ]
        }
    ]
)

# Handle response
for block in message.content:
    if block.type == "thinking":
        print(f"Thinking:\n{block.thinking}\n")
    elif block.type == "text":
        print(f"Text:\n{block.text}\n")
