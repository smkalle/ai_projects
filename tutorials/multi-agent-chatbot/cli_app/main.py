#!/usr/bin/env python3
"""
CLI Interface for Multi-Agent Chatbot System
A beautiful command-line interface with rich formatting and colors
"""

import asyncio
import sys
import os
import signal
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

# Rich imports for beautiful CLI
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.text import Text
    from rich.table import Table
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.prompt import Prompt, Confirm
    from rich.markdown import Markdown
    from rich.syntax import Syntax
    from rich.layout import Layout
    from rich.live import Live
    from rich import box
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    print("⚠️  Rich not available. Install with: pip install rich")

from src.multi_agent_system import MultiAgentSystem
from src.utils.context_manager import ContextManager

class MultiAgentCLI:
    """Command Line Interface for Multi-Agent Chatbot"""
    
    def __init__(self):
        self.console = Console() if RICH_AVAILABLE else None
        self.multi_agent_system = None
        self.conversation_history = []
        self.user_id = f"cli_user_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.session_id = f"session_{int(datetime.now().timestamp())}"
        self.running = True
        
        # Statistics
        self.stats = {
            "messages_sent": 0,
            "agents_used": {},
            "total_response_time": 0.0,
            "session_start": datetime.now()
        }
        
        # Setup signal handling for graceful exit
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle Ctrl+C gracefully"""
        self.running = False
        if self.console:
            self.console.print("\n👋 Goodbye! Thanks for using Multi-Agent Chatbot!")
        else:
            print("\n👋 Goodbye! Thanks for using Multi-Agent Chatbot!")
    
    def print_welcome(self):
        """Display welcome message"""
        if not self.console:
            print("🤖 Multi-Agent Chatbot CLI")
            print("=" * 50)
            print("Welcome to the Multi-Agent Chatbot!")
            print("Type 'help' for commands, 'quit' to exit")
            print("=" * 50)
            return
        
        # Rich welcome screen
        welcome_text = """
# 🤖 Multi-Agent Chatbot CLI

Welcome to the advanced multi-agent chatbot system!

## Available Agents:
- 🎯 **Coordinator**: Routes queries to specialized agents
- 🔍 **Research**: Information gathering and fact-checking
- ⚡ **Task**: Action execution and workflows  
- 🧠 **Memory**: Context management and conversation history
- ❓ **QA**: Question answering with deep understanding

## Commands:
- `help` - Show this help message
- `stats` - Display session statistics
- `history` - Show conversation history
- `export` - Export conversation to JSON
- `clear` - Clear conversation history
- `agents` - List available agents
- `quit` or `exit` - Exit the application

**Start chatting by typing your message!**
        """
        
        self.console.print(Panel(
            Markdown(welcome_text),
            title="🚀 Multi-Agent Chatbot",
            border_style="bright_blue",
            padding=(1, 2)
        ))
    
    async def initialize_system(self):
        """Initialize the multi-agent system"""
        if not self.console:
            print("🔧 Initializing Multi-Agent System...")
        else:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console,
                transient=True
            ) as progress:
                task = progress.add_task("Initializing Multi-Agent System...", total=None)
                
                try:
                    self.multi_agent_system = MultiAgentSystem()
                    await self.multi_agent_system.initialize()
                    progress.update(task, description="✅ System Ready!")
                    await asyncio.sleep(0.5)  # Show success message briefly
                except Exception as e:
                    progress.update(task, description=f"❌ Error: {str(e)}")
                    raise
    
    def format_message(self, role: str, content: str, metadata: Optional[Dict] = None) -> str:
        """Format a message for display"""
        if not self.console:
            return f"[{role.upper()}] {content}"
        
        if role == "user":
            return Panel(
                content,
                title="👤 You",
                border_style="bright_green",
                padding=(0, 1)
            )
        else:
            # Assistant message with metadata
            title = "🤖 Assistant"
            if metadata and "agent_used" in metadata:
                agent_icons = {
                    "Research": "🔍",
                    "Task": "⚡",
                    "Memory": "🧠", 
                    "QA": "❓",
                    "General": "🎯"
                }
                agent = metadata["agent_used"]
                icon = agent_icons.get(agent, "🤖")
                title = f"{icon} {agent} Agent"
            
            return Panel(
                content,
                title=title,
                border_style="bright_cyan",
                padding=(0, 1)
            )
    
    def display_help(self):
        """Display help information"""
        if not self.console:
            help_text = """
Available Commands:
- help: Show this help message
- stats: Display session statistics  
- history: Show conversation history
- export: Export conversation to JSON
- clear: Clear conversation history
- agents: List available agents
- quit/exit: Exit the application
            """
            print(help_text)
            return
        
        # Create help table
        table = Table(title="📚 Available Commands", box=box.ROUNDED)
        table.add_column("Command", style="bright_yellow", width=12)
        table.add_column("Description", style="white")
        
        commands = [
            ("help", "Show this help message"),
            ("stats", "Display session statistics"),
            ("history", "Show conversation history"),
            ("export", "Export conversation to JSON"),
            ("clear", "Clear conversation history"),
            ("agents", "List available agents and capabilities"),
            ("quit/exit", "Exit the application")
        ]
        
        for cmd, desc in commands:
            table.add_row(cmd, desc)
        
        self.console.print(table)
    
    def display_stats(self):
        """Display session statistics"""
        session_duration = datetime.now() - self.stats["session_start"]
        avg_response_time = (
            self.stats["total_response_time"] / max(self.stats["messages_sent"], 1)
        )
        
        if not self.console:
            print(f"""
Session Statistics:
- Messages sent: {self.stats['messages_sent']}
- Session duration: {session_duration}
- Average response time: {avg_response_time:.2f}s
- Agents used: {dict(self.stats['agents_used'])}
            """)
            return
        
        # Create stats table
        table = Table(title="📊 Session Statistics", box=box.ROUNDED)
        table.add_column("Metric", style="bright_yellow")
        table.add_column("Value", style="bright_white")
        
        table.add_row("Messages Sent", str(self.stats["messages_sent"]))
        table.add_row("Session Duration", str(session_duration).split('.')[0])
        table.add_row("Avg Response Time", f"{avg_response_time:.2f}s")
        table.add_row("Total Conversations", str(len(self.conversation_history) // 2))
        
        self.console.print(table)
        
        # Agent usage chart
        if self.stats["agents_used"]:
            agent_table = Table(title="🤖 Agent Usage", box=box.SIMPLE)
            agent_table.add_column("Agent", style="bright_cyan")
            agent_table.add_column("Usage Count", style="bright_green")
            
            for agent, count in self.stats["agents_used"].items():
                agent_table.add_row(agent, str(count))
            
            self.console.print(agent_table)
    
    def display_agents(self):
        """Display available agents and their capabilities"""
        if not self.multi_agent_system:
            msg = "❌ System not initialized"
            if self.console:
                self.console.print(msg, style="red")
            else:
                print(msg)
            return
        
        if not self.console:
            print("Available Agents:")
            for name, agent in self.multi_agent_system.agents.items():
                print(f"- {name}: {agent.description}")
            return
        
        # Create agents table
        table = Table(title="🤖 Available Agents", box=box.ROUNDED)
        table.add_column("Agent", style="bright_cyan", width=12)
        table.add_column("Description", style="white")
        table.add_column("Capabilities", style="bright_yellow")
        
        for name, agent in self.multi_agent_system.agents.items():
            capabilities = ", ".join(agent.capabilities[:3])  # Show first 3
            if len(agent.capabilities) > 3:
                capabilities += "..."
            table.add_row(name.title(), agent.description, capabilities)
        
        self.console.print(table)
    
    def display_history(self):
        """Display conversation history"""
        if not self.conversation_history:
            msg = "No conversation history yet."
            if self.console:
                self.console.print(msg, style="yellow")
            else:
                print(msg)
            return
        
        if not self.console:
            print("\nConversation History:")
            print("-" * 50)
            for msg in self.conversation_history:
                print(f"[{msg['role'].upper()}] {msg['content']}")
            print("-" * 50)
            return
        
        self.console.print("\n[bright_yellow]📚 Conversation History[/bright_yellow]")
        
        for msg in self.conversation_history[-10:]:  # Show last 10 messages
            role = msg['role']
            content = msg['content']
            metadata = msg.get('metadata', {})
            
            formatted_msg = self.format_message(role, content, metadata)
            self.console.print(formatted_msg)
    
    def export_conversation(self):
        """Export conversation to JSON file"""
        if not self.conversation_history:
            msg = "No conversation to export."
            if self.console:
                self.console.print(msg, style="yellow")
            else:
                print(msg)
            return
        
        filename = f"conversation_{self.user_id}.json"
        export_data = {
            "user_id": self.user_id,
            "session_id": self.session_id,
            "export_time": datetime.now().isoformat(),
            "conversation": self.conversation_history,
            "stats": self.stats
        }
        
        try:
            with open(filename, 'w') as f:
                json.dump(export_data, f, indent=2, default=str)
            
            msg = f"✅ Conversation exported to {filename}"
            if self.console:
                self.console.print(msg, style="green")
            else:
                print(msg)
        except Exception as e:
            error_msg = f"❌ Export failed: {str(e)}"
            if self.console:
                self.console.print(error_msg, style="red")
            else:
                print(error_msg)
    
    def clear_history(self):
        """Clear conversation history"""
        if self.console:
            if Confirm.ask("Are you sure you want to clear the conversation history?"):
                self.conversation_history = []
                self.console.print("✅ Conversation history cleared.", style="green")
        else:
            response = input("Clear conversation history? (y/N): ")
            if response.lower() in ['y', 'yes']:
                self.conversation_history = []
                print("✅ Conversation history cleared.")
    
    async def process_message(self, message: str) -> Dict[str, Any]:
        """Process user message through the multi-agent system"""
        if not self.multi_agent_system:
            return {
                "response": "❌ System not initialized. Please restart the application.",
                "metadata": {"error": "System not initialized"},
                "agent_used": "error"
            }
        
        # Show processing indicator
        if self.console:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console,
                transient=True
            ) as progress:
                task = progress.add_task("🤖 Processing your message...", total=None)
                
                try:
                    response = await self.multi_agent_system.process_message(
                        message=message,
                        user_id=self.user_id
                    )
                    progress.update(task, description="✅ Response ready!")
                    await asyncio.sleep(0.3)  # Brief pause to show completion
                    return response
                except Exception as e:
                    progress.update(task, description=f"❌ Error: {str(e)}")
                    await asyncio.sleep(1)
                    raise
        else:
            print("🤖 Processing...")
            return await self.multi_agent_system.process_message(
                message=message,
                user_id=self.user_id
            )
    
    def update_stats(self, response: Dict[str, Any]):
        """Update session statistics"""
        self.stats["messages_sent"] += 1
        
        agent_used = response.get("agent_used", "Unknown")
        self.stats["agents_used"][agent_used] = (
            self.stats["agents_used"].get(agent_used, 0) + 1
        )
        
        if "processing_time" in response:
            self.stats["total_response_time"] += response["processing_time"]
    
    async def chat_loop(self):
        """Main chat interaction loop"""
        while self.running:
            try:
                # Get user input
                if self.console:
                    user_input = Prompt.ask("\n[bright_green]You[/bright_green]", default="").strip()
                else:
                    user_input = input("\nYou: ").strip()
                
                if not user_input or not self.running:
                    continue
                
                # Handle commands
                command = user_input.lower()
                
                if command in ['quit', 'exit', 'q']:
                    self.running = False
                    break
                elif command == 'help':
                    self.display_help()
                    continue
                elif command == 'stats':
                    self.display_stats()
                    continue
                elif command == 'history':
                    self.display_history()
                    continue
                elif command == 'export':
                    self.export_conversation()
                    continue
                elif command == 'clear':
                    self.clear_history()
                    continue
                elif command == 'agents':
                    self.display_agents()
                    continue
                
                # Process message through multi-agent system
                response = await self.process_message(user_input)
                
                # Store conversation
                self.conversation_history.append({
                    "role": "user",
                    "content": user_input,
                    "timestamp": datetime.now().isoformat()
                })
                
                self.conversation_history.append({
                    "role": "assistant",
                    "content": response["response"],
                    "metadata": response.get("metadata", {}),
                    "timestamp": datetime.now().isoformat()
                })
                
                # Update statistics
                self.update_stats(response)
                
                # Display response
                formatted_response = self.format_message(
                    "assistant", 
                    response["response"], 
                    response.get("metadata", {})
                )
                
                if self.console:
                    self.console.print(formatted_response)
                else:
                    print(f"\n[ASSISTANT] {response['response']}")
                
            except KeyboardInterrupt:
                self.running = False
                break
            except Exception as e:
                error_msg = f"❌ Error: {str(e)}"
                if self.console:
                    self.console.print(error_msg, style="red")
                else:
                    print(error_msg)
    
    async def run(self):
        """Main application runner"""
        try:
            # Display welcome
            self.print_welcome()
            
            # Initialize system
            await self.initialize_system()
            
            # Start chat loop
            await self.chat_loop()
            
        except Exception as e:
            error_msg = f"❌ Fatal error: {str(e)}"
            if self.console:
                self.console.print(error_msg, style="red")
            else:
                print(error_msg)
        finally:
            # Goodbye message
            if self.console:
                self.console.print("\n👋 Thanks for using Multi-Agent Chatbot CLI!", style="bright_blue")
            else:
                print("\n👋 Thanks for using Multi-Agent Chatbot CLI!")

def main():
    """Main entry point"""
    cli = MultiAgentCLI()
    
    try:
        asyncio.run(cli.run())
    except KeyboardInterrupt:
        pass  # Handled gracefully by signal handler

if __name__ == "__main__":
    main()