"""
Basic MCP Agent Example
Demonstrates simple agent creation and usage.
"""

import asyncio
import os
from dotenv import load_dotenv
from src.mcp_agent.core import MCPAgent, AgentConfig, LLMProvider

# Load environment variables
load_dotenv()

async def main():
    """Run basic agent example."""
    print("🚀 MCP AI Agent - Basic Example")
    print("-" * 40)

    # Configuration
    config = AgentConfig(
        model="gpt-4o",
        provider=LLMProvider.OPENAI,
        api_key=os.getenv("OPENAI_API_KEY"),
        mcp_servers=["web-browser"],
        system_prompt="You are a helpful research assistant."
    )

    # Create agent
    print("Creating agent...")
    agent = MCPAgent(config)

    # Test queries
    queries = [
        "Hello! Can you tell me about yourself?",
        "What tools do you have access to?",
        "Search for information about Python 3.12 features",
    ]

    for i, query in enumerate(queries, 1):
        print(f"\n📝 Query {i}: {query}")
        print("-" * 20)

        try:
            response = await agent.run(query)
            print(f"🤖 Response: {response}")
        except Exception as e:
            print(f"❌ Error: {e}")

        print()

    print("✅ Basic example completed!")

if __name__ == "__main__":
    asyncio.run(main())
