# Docker/Podman Usage Guide

This guide explains how to build and run the NBP MCP Server using Docker or Podman.

## Building the Image

Using Podman:
```bash
podman build -t nbp-mcp-server:latest .
```

Using Docker:
```bash
docker build -t nbp-mcp-server:latest .
```

## Running the Container

### With Podman

Run in foreground:
```bash
podman run --rm -p 8000:8000 nbp-mcp-server:latest
```

Run in background:
```bash
podman run -d --name nbp-mcp-server -p 8000:8000 nbp-mcp-server:latest
```

### With Docker

Run in foreground:
```bash
docker run --rm -p 8000:8000 nbp-mcp-server:latest
```

Run in background:
```bash
docker run -d --name nbp-mcp-server -p 8000:8000 nbp-mcp-server:latest
```

## Transport Modes

The server supports two transport modes:

### 1. streamable-http (Default in Docker)

The Docker container runs with `streamable-http` transport by default on port 8000.

This mode is suitable for:
- Web-based MCP clients
- Remote access
- Production deployments

### 2. stdio (for CLI usage)

To run with stdio transport (for testing with MCP Inspector):
```bash
podman run --rm -it nbp-mcp-server:latest python main.py --transport stdio
```

## Custom Configuration

You can override the default host and port:

```bash
podman run --rm -p 3000:3000 nbp-mcp-server:latest \
  python main.py --transport streamable-http --host 0.0.0.0 --port 3000
```

## Container Management

### View logs
```bash
podman logs nbp-mcp-server
# or
docker logs nbp-mcp-server
```

### Stop the container
```bash
podman stop nbp-mcp-server
# or
docker stop nbp-mcp-server
```

### Remove the container
```bash
podman rm nbp-mcp-server
# or
docker rm nbp-mcp-server
```

## Health Check

The server should start and display:
```
INFO:     Started server process [1]
INFO:     Waiting for application startup.
INFO:     StreamableHTTP session manager started
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

## Connecting MCP Clients

Once the server is running, MCP clients can connect to:
```
http://localhost:8000/mcp
```

**Important:** The MCP endpoint is at `/mcp`, not at the root path.

For connections from other Docker containers on the same network (e.g., n8n):
```
http://nbp:8000/mcp
```

The server implements the MCP streamable-HTTP protocol and exposes the following tools:
- `get_currency_rate` - Get current exchange rate for a currency
- `get_exchange_table` - Get current exchange rate table
- `get_currency_rate_history` - Get historical exchange rates
- `get_currency_rate_last_n` - Get last N exchange rates
- `get_gold_price` - Get current gold price
- `get_gold_price_history` - Get historical gold prices
- `get_gold_price_last_n` - Get last N gold prices

## Testing with MCP Inspector

To test the containerized server with MCP Inspector:

**Terminal 1** - Start the container:
```bash
podman run --rm -p 8000:8000 nbp-mcp-server:latest
# or with docker-compose:
docker-compose up
```

**Terminal 2** - Connect the inspector:
```bash
npx @modelcontextprotocol/inspector http://localhost:8000/mcp
```

**Note:** The MCP endpoint is at `/mcp`, not at the root path.

The inspector will open in your browser and allow you to test all available tools interactively.

## Environment Variables

The server uses the following environment variables (optional):
- `PYTHONUNBUFFERED=1` - Enables unbuffered Python output (set by default in Dockerfile)

## Notes

- The container runs as a non-root user by default (Python's default user)
- Port 8000 is exposed for HTTP communication
- The image is based on `python:3.13-slim` for minimal size
- Dependencies are managed using `uv` for faster installation
