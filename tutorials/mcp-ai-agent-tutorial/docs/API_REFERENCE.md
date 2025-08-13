# API Reference

## Endpoints

### Health Check
- `GET /health` - Check API health status

### Agent Management
- `POST /agents/create` - Create new agent
- `GET /agents` - List all agents
- `GET /agents/{id}/status` - Get agent status
- `DELETE /agents/{id}` - Delete agent

### Chat
- `POST /agents/{id}/chat` - Send message to agent
- `POST /agents/{id}/chat/stream` - Stream chat with agent

### Tools
- `GET /agents/{id}/tools` - List available tools
- `POST /agents/{id}/tools` - Execute tool

### History
- `GET /agents/{id}/history` - Get conversation history
- `POST /agents/{id}/clear` - Clear history

## Request/Response Models

All endpoints use Pydantic models for validation. See `src/mcp_agent/models.py` for complete schemas.
