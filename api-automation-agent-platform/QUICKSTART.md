# Quick Start Guide

Get started with the API Automation Agent Platform in 5 minutes!

## Installation

### 1. Clone the repository

```bash
git clone <repository-url>
cd api-automation-agent-platform
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment

```bash
cp .env.example .env
# Edit .env and add your API keys
```

### 4. Initialize database

```bash
python -c "from api_agent.db import init_db; init_db()"
```

## Running the Platform

### Start the server

```bash
python -m api_agent.main
```

The server will start on `http://localhost:8000`

### Access API documentation

Open your browser to:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Basic Usage

### 1. Generate Tests from API Documentation

```bash
curl -X POST "http://localhost:8000/api/v1/agents/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "api_source": "https://petstore.swagger.io/v2/swagger.json",
    "format": "playwright"
  }'
```

### 2. Chat with AI Agent

```bash
curl -X POST "http://localhost:8000/api/v1/agents/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Generate tests for the login API",
    "user_id": "user_123"
  }'
```

### 3. Query Knowledge Base

```bash
curl -X POST "http://localhost:8000/api/v1/agents/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Find all authentication endpoints",
    "mode": "mix"
  }'
```

### 4. Execute Tests

```bash
curl -X POST "http://localhost:8000/api/v1/executions/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "suite_id": "suite_001",
    "config": {
      "parallel": true
    }
  }'
```

### 5. Check Task Status

```bash
curl -X GET "http://localhost:8000/api/v1/tasks/{task_id}"
```

## Python API Usage

```python
import asyncio
from agents.orchestrator import create_orchestrator

async def main():
    # Create orchestrator
    orchestrator = await create_orchestrator()

    # Process request
    async for update in orchestrator.process_request(
        user_request="Generate tests for the user API",
        user_id="user_123"
    ):
        print(update)

asyncio.run(main())
```

## Running Examples

```bash
# Run all examples
python examples/quickstart.py

# Run specific example
python examples/api_planner_example.py
python examples/test_generator_example.py
python examples/agent_chat_example.py
```

## MCP Server Usage

### Start RAG MCP Server

```bash
python -m mcp_servers.rag_server
```

### Start Chart MCP Server

```bash
python -m mcp_servers.chart_server
```

### Start Automation-Quality MCP Server

```bash
python -m mcp_servers.automation_quality
```

## Configuration

Key environment variables:

```bash
# LLM Settings
LLM_PROVIDER=openai  # or anthropic
LLM_MODEL=gpt-4-turbo-preview
OPENAI_API_KEY=your-key-here

# Database
DATABASE_URL=sqlite+aiosqlite:///./api_agent.db

# RAG Settings
RAG_MODE=mix
RAG_TOP_K=10

# Test Framework
DEFAULT_TEST_FRAMEWORK=playwright
```

## Next Steps

- Read the [Architecture Documentation](docs/ARCHITECTURE.md)
- Explore [Examples](examples/)
- Check [API Reference](docs/API.md)
- Join our [Community](https://github.com/your-repo/discussions)

## Troubleshooting

### Database locked error

```bash
rm api_agent.db
python -c "from api_agent.db import init_db; init_db()"
```

### MCP server not responding

Check if the MCP server is running:

```bash
curl http://localhost:8001/health
```

### LLM API errors

Verify your API keys are correct in `.env`:

```bash
echo $OPENAI_API_KEY
```

## Support

- Documentation: [docs/](docs/)
- Issues: [GitHub Issues](https://github.com/your-repo/issues)
- Discord: [Join our server](https://discord.gg/your-server)

---

Happy Testing! 🚀
