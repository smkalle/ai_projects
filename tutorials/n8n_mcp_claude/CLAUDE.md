# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a tutorial project for building advanced AI agents using Claude Code with n8n's Model Context Protocol (MCP). The project focuses on creating reliable, production-grade n8n workflow automations that can be deployed on platforms like Hostinger VPS.

## Key Concepts

### Model Context Protocol (MCP)
The MCP approach is the recommended method for building n8n automations. It provides:
- Access to official n8n node documentation
- Proper node configuration and structure understanding
- Reliable, tested automations that follow best practices
- Significantly more detailed and functional workflows compared to basic JSON generation

### Project Structure
- `n8n_mcp_claude.txt` - Main tutorial documentation covering setup, configuration, and deployment
- `MCP.json` - Configuration file for n8n MCP server (to be created when setting up MCP)

## Common Development Tasks

### Setting Up n8n MCP Server
```bash
# Install n8n MCP dependencies if needed
npm install -g @anthropic-ai/claude-code

# Start the MCP server
npx n8n mcp
```

### Creating MCP Configuration
When setting up the project, create an `MCP.json` file with the n8n MCP configuration from the official repository (https://github.com/czlonkowski/n8n-mcp).

### Building n8n Workflows
1. Ensure MCP server is running
2. Configure Claude Code to use the MCP
3. Use detailed prompts to generate complete workflows
4. Grant permissions for MCP tools (`search nodes`, `get node essentials`)
5. Import generated JSON files into n8n instance

## Important Implementation Notes

### MCP Tool Permissions
- `search nodes` - Fetches official n8n node documentation
- `get node essentials` - Understands node structure and inputs
- Permissions are stored in `settings.json.local` for automatic approval

### Workflow Generation Best Practices
- Always use MCP method over basic JSON generation
- Enable auto-accept mode in Claude Code (Shift + Tab)
- Provide detailed prompts for complex automations
- Verify node configurations after import

### Credential Management
Manual steps required for:
- Telegram Bot connections (via BotFather)
- Google Calendar API setup
- OpenAI API keys
- Other service authentications

## Deployment Considerations

### Hostinger VPS Setup
- Recommended: KVM2 plan for unlimited workflows
- Use one-click n8n template during OS selection
- Apply coupon code for discounts
- Manage agents through Hostinger panel

### Testing and Validation
- Always test imported workflows before production deployment
- Verify all node connections and credentials
- Check trigger configurations
- Test voice transcription if using audio inputs

## Package Management
Use `uv` for Python package management if Python components are added to the project. Node.js dependencies should be managed with npm for n8n-related tools.

## Architecture Patterns

### Typical n8n Workflow Structure
1. **Trigger Node** - Initiates workflow (Telegram, webhook, schedule)
2. **Processing Nodes** - Handle data transformation and logic
3. **Integration Nodes** - Connect to external services (Calendar, Task managers)
4. **AI Agent Nodes** - Leverage AI for decision making
5. **Output Nodes** - Send results back to user or system

### Calendar Optimization Agent Example
- Telegram trigger for text/voice input
- OpenAI transcription for voice messages
- Google Calendar integration for gap analysis
- Vectara/task manager for priority determination
- Automatic calendar event creation

## Known Issues and Solutions

### Common MCP Setup Issues
- If Claude Code doesn't detect MCP.json, restart Claude Code instance
- Old JSON files may interfere - create new files instead of updating
- Ensure Node.js v18+ is installed

### Workflow Import Problems
- Unconfigured nodes indicate non-MCP generation - regenerate with MCP
- Generic HTTP nodes suggest missing dedicated tool nodes
- Empty "ghost blocks" require proper MCP-based regeneration