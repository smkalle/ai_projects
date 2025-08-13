"""
File Manager Agent Example
Demonstrates file operations with MCP.
"""

import asyncio
import os
from dotenv import load_dotenv
from src.mcp_agent.core import create_file_manager_agent

load_dotenv()

async def main():
    """Run file manager agent example."""
    print("📁 MCP AI Agent - File Manager Example")
    print("-" * 45)

    # Create file manager agent
    agent = await create_file_manager_agent(os.getenv("ANTHROPIC_API_KEY"))

    # File operations
    operations = [
        "List the files in the current directory",
        "Create a new file called 'test.txt' with some sample content",
        "Read the contents of the file we just created",
        "Create a backup copy of the file"
    ]

    for operation in operations:
        print(f"\n📁 Operation: {operation}")
        print("-" * 30)

        try:
            result = await agent.run(operation)
            print(f"✅ Result: {result[:200]}...")
        except Exception as e:
            print(f"❌ Error: {e}")

    print("\n✅ File manager example completed!")

if __name__ == "__main__":
    asyncio.run(main())
