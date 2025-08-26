# Documentation

This directory contains comprehensive documentation for the Energy Document AI system.

## Documentation Overview

### 📋 [Architecture Documentation](ARCHITECTURE.md)
Detailed system architecture, component descriptions, data flow, and design patterns.

**Contents**:
- System overview and component diagram
- PDF processing pipeline details
- RAG system architecture
- LangGraph agent workflow
- Database schema and storage patterns
- Performance optimization strategies

### 🔌 [API Reference](API_REFERENCE.md)
Complete API documentation for both REST endpoints and WebSocket connections.

**Contents**:
- FastAPI endpoint specifications
- Request/response schemas
- Authentication and rate limiting
- WebSocket event documentation
- Python SDK usage examples
- Error codes and troubleshooting

### 🚀 [Deployment Guide](DEPLOYMENT.md)
Comprehensive deployment instructions for development and production environments.

**Contents**:
- Development setup instructions
- Production deployment with systemd
- Docker and Kubernetes deployment
- Cloud platform deployment (AWS, GCP, Azure)
- SSL/TLS configuration
- Monitoring and logging setup
- Backup and recovery procedures

## Quick Navigation

### For Developers
- Start with [Architecture Documentation](ARCHITECTURE.md) to understand the system
- Refer to [API Reference](API_REFERENCE.md) for integration details
- Use [Deployment Guide](DEPLOYMENT.md) for local development setup

### For DevOps/SysAdmins
- Follow [Deployment Guide](DEPLOYMENT.md) for production setup
- Reference monitoring and troubleshooting sections
- Configure SSL, logging, and backup procedures

### For API Users
- Review [API Reference](API_REFERENCE.md) for endpoint documentation
- Check rate limits and authentication requirements
- Use SDK examples for quick integration

## Additional Resources

### Code Documentation
- **CLAUDE.md**: Guidance for future Claude Code instances
- **README.md**: Main project overview and quick start guide
- **Inline comments**: Detailed code-level documentation

### Sample Data
- **data/README.md**: Sample PDF documents and testing guidance
- **scripts/**: Utility scripts for generating test data

### Configuration
- **.env.example**: Environment configuration template
- **requirements.txt**: Python dependencies with versions
- **docker-compose.yml**: Container orchestration setup

## Contributing to Documentation

When updating documentation:

1. **Keep it current**: Update docs when making code changes
2. **Be specific**: Include exact commands, file paths, and examples
3. **Test instructions**: Verify all procedures work as documented
4. **Cross-reference**: Link between related documentation sections
5. **Use clear headers**: Make content easy to navigate and search

## Documentation Standards

- Use Markdown formatting for consistency
- Include code examples with proper syntax highlighting
- Provide both beginner and advanced usage examples
- Document error conditions and troubleshooting steps
- Include performance considerations and best practices

## Getting Help

If documentation is unclear or incomplete:

1. Check the troubleshooting sections in each document
2. Review the API documentation for specific integration questions
3. Examine sample code and test cases
4. Submit issues for documentation improvements