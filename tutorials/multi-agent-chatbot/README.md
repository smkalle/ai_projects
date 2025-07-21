# Multi-Agent Chatbot with Streamlit Interface

A sophisticated multi-agent chatbot system built with LangGraph, Context Engineering, and Kimi K2, featuring a beautiful Streamlit web interface.

## 🚀 Features

- **Multi-Agent Architecture**: Specialized agents for different tasks
  - 🎯 **Coordinator Agent**: Routes queries to appropriate agents
  - 🔍 **Research Agent**: Information gathering and fact-checking  
  - ⚡ **Task Agent**: Action execution and workflows
  - 🧠 **Memory Agent**: Context management and conversation history
  - ❓ **QA Agent**: Question answering with deep understanding

- **Modern Web Interface**: Built with Streamlit
  - Real-time chat interface
  - System metrics and analytics
  - Agent selection visualization
  - Conversation export functionality

- **Beautiful CLI Interface**: Rich command-line experience
  - Colorful, formatted output with Rich library
  - Interactive chat with agent visualization
  - Command history and statistics
  - Session management and export

- **Advanced Context Management**: 
  - Token optimization
  - Context compression
  - Semantic chunking

- **Production-Ready Features**:
  - Error handling and fallbacks
  - Performance monitoring
  - Configurable settings
  - API key management

## 📁 Project Structure

```
multi-agent-chatbot/
├── streamlit_app/
│   └── main.py                 # Main Streamlit application
├── cli_app/
│   └── main.py                 # Beautiful CLI application
├── src/
│   ├── agents/
│   │   ├── base_agent.py       # Base agent class
│   │   └── simple_agent.py     # Simplified agent implementation
│   ├── utils/
│   │   ├── context_manager.py  # Context management utilities
│   │   └── kimi_client.py      # Kimi K2 API client
│   ├── config/
│   │   └── graph_config.py     # LangGraph configuration
│   └── multi_agent_system.py   # Main system orchestrator
├── requirements.txt            # Python dependencies
├── .env.example               # Environment variables template
├── run_streamlit.py           # Streamlit launcher
├── run_cli.py                 # CLI launcher
├── test_cli.py                # CLI test suite
└── README.md                  # This file
```

## 🛠️ Installation

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd multi-agent-chatbot
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Environment Setup

Copy the environment template and configure your API keys:

```bash
cp .env.example .env
```

Edit `.env` with your API keys:

```env
# Required for advanced features
OPENAI_API_KEY=your_openai_api_key_here
KIMI_API_KEY=your_kimi_k2_api_key_here

# Optional
KIMI_API_URL=https://api.kimi.ai/v1
```

**Note**: The application will work in demo mode without API keys, but with limited functionality.

## 🚀 Running the Application

### Streamlit Web Interface

```bash
python run_streamlit.py
```

This will:
- Check dependencies
- Setup environment variables
- Launch the Streamlit app at http://localhost:8501

### CLI Interface

```bash
python run_cli.py
```

This will:
- Launch the beautiful command-line interface
- Provide rich formatting and colors
- Enable interactive chat with the multi-agent system

### Manual Launch

```bash
# Streamlit
streamlit run streamlit_app/main.py --server.port=8501

# CLI
python cli_app/main.py
```

## 💬 Using the Chatbot

### Streamlit Web Interface
1. **Chat Interface**: Type messages in the chat input at the bottom
2. **Agent Selection**: The system automatically selects the best agent for each query
3. **View Metrics**: Check the Analytics tab for system performance data
4. **Export Conversations**: Download chat history as JSON
5. **Configure Settings**: Adjust API keys and system parameters in Settings

### CLI Interface
1. **Interactive Chat**: Type messages directly in the terminal
2. **Rich Formatting**: Enjoy colorful, formatted responses
3. **Commands**: Use built-in commands like `help`, `stats`, `agents`, `history`
4. **Export**: Save conversations with the `export` command
5. **Statistics**: View session stats with the `stats` command

## 🤖 Agent Capabilities

### Research Agent
- Information gathering
- Fact-checking and verification
- Web search simulation
- Data analysis

**Example queries:**
- "Research the latest developments in AI"
- "Find information about climate change"
- "What are the facts about renewable energy?"

### Task Agent  
- Action execution
- Workflow automation
- Step-by-step guidance
- Process management

**Example queries:**
- "Help me create a project plan"
- "Execute a data backup process"
- "Generate a report"

### Memory Agent
- Conversation history management
- Context retrieval
- User preference tracking
- Pattern recognition

**Example queries:**
- "What did we discuss earlier?"
- "Remember my preferences"
- "Summarize our conversation"

### QA Agent
- Question answering
- Detailed explanations
- Educational content
- Clarifications

**Example queries:**
- "Explain how neural networks work"
- "What is the difference between AI and ML?"
- "How does this system work?"

## 📊 System Analytics

The application provides real-time analytics including:

- **Response Times**: Average processing time per request
- **Agent Usage**: Distribution of queries across agents
- **System Metrics**: Total requests, errors, and performance data
- **Conversation Analytics**: Message counts and patterns

## ⚙️ Configuration

### API Keys

Configure in the `.env` file or through the Settings tab in the web interface:

- **OpenAI API Key**: For embeddings and LangGraph functionality
- **Kimi K2 API Key**: For advanced reasoning capabilities

### System Settings

Adjustable parameters:
- Maximum context length (1024-8192 tokens)
- Enable/disable conversation memory
- Analytics collection toggle
- Agent selection preferences

## 🔧 Development

### Adding New Agents

1. Create a new agent class inheriting from `BaseAgent`:

```python
from src.agents.base_agent import BaseAgent

class CustomAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Custom",
            description="Custom agent description",
            capabilities=["custom_capability"]
        )
    
    async def can_handle(self, task: str) -> float:
        # Return confidence score 0-1
        return 0.8 if "custom" in task.lower() else 0.1
    
    async def process(self, state):
        # Process the state and return updated state
        return state
```

2. Register the agent in `MultiAgentSystem`:

```python
self.agents["custom"] = CustomAgent()
```

### Extending the Streamlit Interface

The main Streamlit app is modular. Add new features by:

1. Creating new tabs in `main.py`
2. Adding new metrics to the analytics dashboard
3. Implementing new visualization components

### Testing

Run basic tests:

```bash
python -m pytest tests/  # When test files are added
```

## 🐛 Troubleshooting

### Common Issues

1. **Import Errors**
   ```bash
   # Ensure you're in the project directory
   cd multi-agent-chatbot
   python run_streamlit.py
   ```

2. **Missing Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **API Key Issues**
   - Check `.env` file configuration
   - Verify API key validity
   - The app works in demo mode without keys

4. **Port Already in Use**
   ```bash
   streamlit run streamlit_app/main.py --server.port=8502
   ```

### Performance Issues

- Reduce `MAX_CONTEXT_LENGTH` in settings
- Disable analytics if experiencing slowdown
- Check system resources and memory usage

## 📝 License

This project is part of the Multi-Agent Chatbot tutorial series. See the full tutorial in `multi-agent-chatbot-langgraph-tutorial.md`.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📚 Learn More

- Read the complete tutorial: `multi-agent-chatbot-langgraph-tutorial.md`
- [LangGraph Documentation](https://github.com/langchain-ai/langgraph)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [Kimi K2 API Documentation](https://kimi.ai/docs)

## 🆘 Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review the full tutorial for detailed explanations
3. Open an issue in the repository
4. Check the console output for error details

---

**Happy Chatting!** 🎉