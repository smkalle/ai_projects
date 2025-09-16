# PagerDuty AI Agent MVP

A comprehensive AI agent inspired by PagerDuty's incident management system, built with LangChain, LangGraph, Streamlit, and OpenAI GPT-4 omni.

[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## 🚀 Features
- Multi-session, context-aware conversations
- Reliable analytics with error handling
- Natural language queries on incident data
- Streamlit web interface
- SQLite database for incident storage
- LangGraph workflow orchestration
- Memory persistence across sessions

## 🛠 Technology Stack
- **Frontend**: Streamlit
- **AI Framework**: LangChain + LangGraph
- **LLM**: OpenAI GPT-4 omni
- **Database**: SQLite
- **Memory**: LangChain Memory with SQLite backend
- **Observability**: LangSmith (optional)

## 📦 Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/pagerduty-ai-agent.git
   cd pagerduty-ai-agent
   ```

2. Create and activate virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

5. Initialize the database:
   ```bash
   python scripts/init_database.py
   ```

6. Run the application:
   ```bash
   streamlit run app.py
   ```

## 🎯 Usage Examples

### Basic Queries
- "How many high priority incidents are open?"
- "Show me incidents from the last 24 hours"
- "What's the average resolution time for database incidents?"

### Advanced Analytics
- "Which service has the most incidents this week?"
- "Compare incident trends between this month and last month"
- "Show me incidents that took longer than 4 hours to resolve"

## 🔧 Configuration

Edit `.env` file:
```
OPENAI_API_KEY=your_openai_api_key_here
LANGCHAIN_TRACING_V2=true  # Optional: for LangSmith
LANGCHAIN_API_KEY=your_langsmith_key  # Optional
DATABASE_URL=sqlite:///incidents.db
```

## 🧪 Testing

Run tests:
```bash
python -m pytest tests/ -v
```

## 🚀 Deployment

For production deployment, consider:
- Using PostgreSQL instead of SQLite
- Adding authentication
- Setting up monitoring and logging
- Containerizing with Docker (if needed)

## 🤝 Contributing

Please see [CONTRIBUTING.md](CONTRIBUTING.md) for detailed contribution guidelines.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`python -m pytest tests/ -v`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## 📄 License

MIT License - see LICENSE file for details.

## 📁 Project Structure

```
pagerduty-ai-agent/
├── src/
│   ├── agents/          # LangGraph workflow definitions
│   ├── data/            # Database models and management
│   ├── tools/           # LangChain tools for database/analytics
│   └── utils/           # Configuration and logging
├── tests/               # Test suite
├── scripts/             # Database initialization scripts
├── app.py              # Main Streamlit application
└── requirements.txt    # Python dependencies
```

## 🙏 Acknowledgments

- Inspired by PagerDuty's AI agent implementation
- Built with LangChain and LangGraph frameworks
- Uses OpenAI's GPT-4 omni model