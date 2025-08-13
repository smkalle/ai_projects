"""
Web Search Agent Example
Demonstrates web searching capabilities.
"""

import asyncio
import os
from dotenv import load_dotenv
from src.mcp_agent.core import create_web_search_agent

load_dotenv()

async def main():
    """Run web search agent example."""
    print("🔍 MCP AI Agent - Web Search Example")
    print("-" * 45)

    # Create specialized web search agent
    agent = await create_web_search_agent(os.getenv("OPENAI_API_KEY"))

    # Search queries
    search_queries = [
        "Latest developments in AI and machine learning 2025",
        "Best practices for Python web development",
        "Current weather in San Francisco",
        "Top 5 programming languages for beginners"
    ]

    for query in search_queries:
        print(f"\n🔍 Searching: {query}")
        print("-" * 30)

        try:
            result = await agent.run(f"Please search for: {query}")
            print(f"📋 Results: {result[:200]}...")
        except Exception as e:
            print(f"❌ Error: {e}")

    print("\n✅ Web search example completed!")

if __name__ == "__main__":
    asyncio.run(main())
