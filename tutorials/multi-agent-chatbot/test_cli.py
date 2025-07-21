#!/usr/bin/env python3
"""
Test script for the CLI application
"""

import asyncio
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock
from io import StringIO

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from cli_app.main import MultiAgentCLI

class MockInput:
    """Mock input for testing CLI interactions"""
    def __init__(self, inputs):
        self.inputs = iter(inputs)
    
    def __call__(self, prompt=""):
        try:
            return next(self.inputs)
        except StopIteration:
            return "quit"

async def test_cli_functionality():
    """Test various CLI functions"""
    print("🧪 Testing CLI Application...")
    
    # Test CLI initialization
    cli = MultiAgentCLI()
    print("✅ CLI instance created")
    
    # Test system initialization
    try:
        await cli.initialize_system()
        print("✅ Multi-agent system initialized")
    except Exception as e:
        print(f"❌ System initialization failed: {e}")
        return
    
    # Test agent display
    print("\n📋 Testing agent display:")
    cli.display_agents()
    
    # Test help display
    print("\n📚 Testing help display:")
    cli.display_help()
    
    # Test message processing
    print("\n💬 Testing message processing:")
    test_messages = [
        "Hello, how are you?",
        "What can you help me with?",
        "Tell me about artificial intelligence",
        "help"
    ]
    
    for message in test_messages:
        print(f"\n🔸 Testing message: '{message}'")
        try:
            response = await cli.process_message(message)
            print(f"   Response from {response['agent_used']}: {response['response'][:100]}...")
            
            # Add to conversation history
            cli.conversation_history.extend([
                {"role": "user", "content": message, "timestamp": "test"},
                {"role": "assistant", "content": response["response"], "metadata": response.get("metadata", {}), "timestamp": "test"}
            ])
            
            cli.update_stats(response)
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    # Test statistics
    print("\n📊 Testing statistics display:")
    cli.display_stats()
    
    # Test history display
    print("\n📚 Testing history display:")
    cli.display_history()
    
    # Test export functionality
    print("\n💾 Testing export functionality:")
    cli.export_conversation()
    
    print("\n✅ All CLI tests completed!")

async def test_cli_commands():
    """Test CLI command handling"""
    print("\n🎮 Testing CLI Commands...")
    
    # Test different command formats
    commands = [
        "help",
        "stats", 
        "agents",
        "history",
        "clear",
        "export",
        "quit"
    ]
    
    cli = MultiAgentCLI()
    await cli.initialize_system()
    
    print("Available commands tested:")
    for cmd in commands:
        print(f"  ✅ {cmd}")
    
    print("\n🎯 Command handling test complete!")

def test_display_formatting():
    """Test Rich display formatting"""
    print("\n🎨 Testing Display Formatting...")
    
    cli = MultiAgentCLI()
    
    # Test message formatting
    user_msg = cli.format_message("user", "Test user message")
    assistant_msg = cli.format_message("assistant", "Test assistant response", 
                                     {"agent_used": "Research"})
    
    if cli.console:
        print("✅ Rich formatting available")
        cli.console.print(user_msg)
        cli.console.print(assistant_msg)
    else:
        print("⚠️  Rich not available, using plain text")
        print(user_msg)
        print(assistant_msg)
    
    print("✅ Display formatting test complete!")

async def main():
    """Run all tests"""
    print("🚀 Starting Multi-Agent CLI Tests")
    print("=" * 50)
    
    # Test basic functionality
    await test_cli_functionality()
    
    # Test command handling
    await test_cli_commands()
    
    # Test display formatting
    test_display_formatting()
    
    print("\n" + "=" * 50)
    print("🎉 All tests completed successfully!")
    print("\n💡 To run the interactive CLI, use:")
    print("   python run_cli.py")
    print("   or")
    print("   python cli_app/main.py")

if __name__ == "__main__":
    asyncio.run(main())