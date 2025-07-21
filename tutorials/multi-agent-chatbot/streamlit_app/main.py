import streamlit as st
import asyncio
import os
import sys
from typing import Dict, Any, List
import json
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.multi_agent_system import MultiAgentSystem
from src.utils.context_manager import ContextManager
from streamlit_chat import message

# Page configuration
st.set_page_config(
    page_title="Multi-Agent Chatbot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .agent-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 4px solid #1f77b4;
    }
    .metrics-container {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    .user-message {
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
    }
    .assistant-message {
        background-color: #f3e5f5;
        border-left: 4px solid #9c27b0;
    }
</style>
""", unsafe_allow_html=True)

class StreamlitMultiAgentApp:
    def __init__(self):
        self.multi_agent_system = None
        self.context_manager = ContextManager()
        self.initialize_session_state()
    
    def initialize_session_state(self):
        """Initialize Streamlit session state variables"""
        if 'messages' not in st.session_state:
            st.session_state.messages = []
        if 'agent_metrics' not in st.session_state:
            st.session_state.agent_metrics = {}
        if 'system_initialized' not in st.session_state:
            st.session_state.system_initialized = False
        if 'user_id' not in st.session_state:
            st.session_state.user_id = f"user_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        if 'conversation_history' not in st.session_state:
            st.session_state.conversation_history = []
    
    async def initialize_system(self):
        """Initialize the multi-agent system"""
        if not st.session_state.system_initialized:
            with st.spinner("Initializing Multi-Agent System..."):
                try:
                    self.multi_agent_system = MultiAgentSystem()
                    await self.multi_agent_system.initialize()
                    st.session_state.system_initialized = True
                    st.success("✅ Multi-Agent System initialized successfully!")
                except Exception as e:
                    st.error(f"❌ Failed to initialize system: {str(e)}")
                    st.stop()
    
    def render_header(self):
        """Render the application header"""
        st.markdown('<h1 class="main-header">🤖 Multi-Agent Chatbot</h1>', unsafe_allow_html=True)
        st.markdown("### Powered by LangGraph, Context Engineering & Kimi K2")
        
        # System status
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.session_state.system_initialized:
                st.success("🟢 System Online")
            else:
                st.warning("🟡 Initializing...")
        with col2:
            st.info(f"👤 User ID: {st.session_state.user_id}")
        with col3:
            st.info(f"💬 Messages: {len(st.session_state.conversation_history)}")
    
    def render_sidebar(self):
        """Render the sidebar with system information and controls"""
        with st.sidebar:
            st.header("🎛️ System Control")
            
            # Environment settings
            st.subheader("Environment")
            api_key_status = "✅ Set" if os.getenv("OPENAI_API_KEY") else "❌ Missing"
            st.write(f"OpenAI API: {api_key_status}")
            
            kimi_key_status = "✅ Set" if os.getenv("KIMI_API_KEY") else "❌ Missing"
            st.write(f"Kimi K2 API: {kimi_key_status}")
            
            # Agent information
            st.subheader("🤖 Available Agents")
            agents_info = [
                {"name": "Coordinator", "desc": "Routes tasks to appropriate agents", "icon": "🎯"},
                {"name": "Research", "desc": "Conducts research and fact-checking", "icon": "🔍"},
                {"name": "Task", "desc": "Executes specific actions", "icon": "⚡"},
                {"name": "Memory", "desc": "Manages conversation context", "icon": "🧠"},
                {"name": "QA", "desc": "Handles questions with deep understanding", "icon": "❓"}
            ]
            
            for agent in agents_info:
                with st.expander(f"{agent['icon']} {agent['name']}"):
                    st.write(agent['desc'])
            
            # Conversation controls
            st.subheader("💬 Conversation")
            if st.button("🗑️ Clear History"):
                st.session_state.conversation_history = []
                st.session_state.messages = []
                st.rerun()
            
            if st.button("📥 Export Chat"):
                self.export_conversation()
            
            # System metrics
            if st.session_state.agent_metrics:
                st.subheader("📊 System Metrics")
                self.render_metrics_sidebar()
    
    def render_metrics_sidebar(self):
        """Render system metrics in sidebar"""
        metrics = st.session_state.agent_metrics
        
        if 'response_times' in metrics:
            avg_response = sum(metrics['response_times']) / len(metrics['response_times'])
            st.metric("Avg Response Time", f"{avg_response:.2f}s")
        
        if 'agent_usage' in metrics:
            most_used = max(metrics['agent_usage'], key=metrics['agent_usage'].get)
            st.metric("Most Used Agent", most_used)
        
        if 'total_requests' in metrics:
            st.metric("Total Requests", metrics['total_requests'])
    
    def render_chat_interface(self):
        """Render the main chat interface"""
        st.subheader("💬 Chat Interface")
        
        # Chat container
        chat_container = st.container()
        
        with chat_container:
            # Display conversation history
            for i, msg in enumerate(st.session_state.conversation_history):
                if msg['role'] == 'user':
                    with st.chat_message("user"):
                        st.write(msg['content'])
                else:
                    with st.chat_message("assistant"):
                        st.write(msg['content'])
                        
                        # Show agent metadata if available
                        if 'metadata' in msg:
                            with st.expander("🔍 Response Details"):
                                st.json(msg['metadata'])
        
        # Chat input
        user_input = st.chat_input("Type your message here...")
        
        if user_input:
            # Add user message to history
            st.session_state.conversation_history.append({
                'role': 'user',
                'content': user_input,
                'timestamp': datetime.now().isoformat()
            })
            
            # Process message asynchronously
            with st.spinner("🤖 Thinking..."):
                try:
                    response = asyncio.run(self.process_message(user_input))
                    
                    # Add assistant response to history
                    st.session_state.conversation_history.append({
                        'role': 'assistant',
                        'content': response['response'],
                        'metadata': response.get('metadata', {}),
                        'agent_used': response.get('agent_used', 'unknown'),
                        'timestamp': datetime.now().isoformat()
                    })
                    
                    # Update metrics
                    self.update_metrics(response)
                    
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Error processing message: {str(e)}")
    
    async def process_message(self, message: str) -> Dict[str, Any]:
        """Process user message through the multi-agent system"""
        if not self.multi_agent_system:
            # Fallback response if system isn't initialized
            return {
                "response": "I'm sorry, the multi-agent system is not available right now. Please try again later.",
                "metadata": {"error": "System not initialized"},
                "agent_used": "fallback"
            }
        
        try:
            response = await self.multi_agent_system.process_message(
                message=message,
                user_id=st.session_state.user_id
            )
            return response
        except Exception as e:
            return {
                "response": f"I encountered an error: {str(e)}",
                "metadata": {"error": str(e)},
                "agent_used": "error_handler"
            }
    
    def update_metrics(self, response: Dict[str, Any]):
        """Update system metrics"""
        if 'agent_metrics' not in st.session_state:
            st.session_state.agent_metrics = {
                'response_times': [],
                'agent_usage': {},
                'total_requests': 0
            }
        
        metrics = st.session_state.agent_metrics
        
        # Update agent usage
        agent_used = response.get('agent_used', 'unknown')
        metrics['agent_usage'][agent_used] = metrics['agent_usage'].get(agent_used, 0) + 1
        
        # Update request count
        metrics['total_requests'] += 1
        
        # Add response time if available
        if 'processing_time' in response:
            metrics['response_times'].append(response['processing_time'])
        
        st.session_state.agent_metrics = metrics
    
    def render_analytics_tab(self):
        """Render analytics and metrics"""
        st.subheader("📊 Analytics Dashboard")
        
        if not st.session_state.agent_metrics:
            st.info("No metrics available yet. Start chatting to see analytics!")
            return
        
        metrics = st.session_state.agent_metrics
        
        # Metrics overview
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_requests = metrics.get('total_requests', 0)
            st.metric("Total Requests", total_requests)
        
        with col2:
            if 'response_times' in metrics and metrics['response_times']:
                avg_time = sum(metrics['response_times']) / len(metrics['response_times'])
                st.metric("Avg Response Time", f"{avg_time:.2f}s")
            else:
                st.metric("Avg Response Time", "N/A")
        
        with col3:
            agent_count = len(metrics.get('agent_usage', {}))
            st.metric("Agents Used", agent_count)
        
        with col4:
            conversation_length = len(st.session_state.conversation_history)
            st.metric("Messages", conversation_length)
        
        # Charts
        if 'agent_usage' in metrics and metrics['agent_usage']:
            col1, col2 = st.columns(2)
            
            with col1:
                # Agent usage pie chart
                st.subheader("Agent Usage Distribution")
                agent_df = pd.DataFrame(
                    list(metrics['agent_usage'].items()),
                    columns=['Agent', 'Usage']
                )
                fig_pie = px.pie(agent_df, values='Usage', names='Agent', title="Agent Usage")
                st.plotly_chart(fig_pie, use_container_width=True)
            
            with col2:
                # Response times over time
                if 'response_times' in metrics and len(metrics['response_times']) > 1:
                    st.subheader("Response Times")
                    times_df = pd.DataFrame({
                        'Request': range(1, len(metrics['response_times']) + 1),
                        'Response Time (s)': metrics['response_times']
                    })
                    fig_line = px.line(times_df, x='Request', y='Response Time (s)', 
                                     title="Response Times Over Time")
                    st.plotly_chart(fig_line, use_container_width=True)
    
    def export_conversation(self):
        """Export conversation history"""
        if not st.session_state.conversation_history:
            st.warning("No conversation to export!")
            return
        
        export_data = {
            'user_id': st.session_state.user_id,
            'export_time': datetime.now().isoformat(),
            'conversation': st.session_state.conversation_history,
            'metrics': st.session_state.agent_metrics
        }
        
        json_str = json.dumps(export_data, indent=2)
        st.download_button(
            label="💾 Download Conversation",
            data=json_str,
            file_name=f"conversation_{st.session_state.user_id}.json",
            mime="application/json"
        )
    
    def render_settings_tab(self):
        """Render settings and configuration"""
        st.subheader("⚙️ Settings")
        
        # API Configuration
        st.subheader("API Configuration")
        
        with st.expander("OpenAI Settings"):
            openai_key = st.text_input(
                "OpenAI API Key",
                value=os.getenv("OPENAI_API_KEY", ""),
                type="password",
                help="Your OpenAI API key for LangGraph and embedding models"
            )
            if st.button("Update OpenAI Key"):
                os.environ["OPENAI_API_KEY"] = openai_key
                st.success("OpenAI API key updated!")
        
        with st.expander("Kimi K2 Settings"):
            kimi_key = st.text_input(
                "Kimi K2 API Key",
                value=os.getenv("KIMI_API_KEY", ""),
                type="password",
                help="Your Kimi K2 API key for advanced reasoning"
            )
            kimi_url = st.text_input(
                "Kimi K2 API URL",
                value=os.getenv("KIMI_API_URL", "https://api.kimi.ai/v1"),
                help="Kimi K2 API endpoint URL"
            )
            if st.button("Update Kimi Settings"):
                os.environ["KIMI_API_KEY"] = kimi_key
                os.environ["KIMI_API_URL"] = kimi_url
                st.success("Kimi K2 settings updated!")
        
        # System Configuration
        st.subheader("System Configuration")
        
        max_context = st.slider(
            "Maximum Context Length",
            min_value=1024,
            max_value=8192,
            value=4096,
            step=512,
            help="Maximum number of tokens for context windows"
        )
        
        enable_memory = st.checkbox(
            "Enable Conversation Memory",
            value=True,
            help="Store and use conversation history for context"
        )
        
        enable_analytics = st.checkbox(
            "Enable Analytics",
            value=True,
            help="Collect and display system metrics"
        )
        
        if st.button("💾 Save Settings"):
            settings = {
                'max_context': max_context,
                'enable_memory': enable_memory,
                'enable_analytics': enable_analytics
            }
            # In a real app, you'd save these settings
            st.success("Settings saved!")
    
    def run(self):
        """Main application runner"""
        # Initialize system
        asyncio.run(self.initialize_system())
        
        # Render header
        self.render_header()
        
        # Render sidebar
        self.render_sidebar()
        
        # Main content tabs
        tab1, tab2, tab3 = st.tabs(["💬 Chat", "📊 Analytics", "⚙️ Settings"])
        
        with tab1:
            self.render_chat_interface()
        
        with tab2:
            self.render_analytics_tab()
        
        with tab3:
            self.render_settings_tab()

def main():
    """Main entry point"""
    app = StreamlitMultiAgentApp()
    app.run()

if __name__ == "__main__":
    main()