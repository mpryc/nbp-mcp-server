# NBP MCP Server - Examples

This directory contains examples showing how to interact with the NBP MCP server.

## Understanding MCP Communication

### What Happens When You Use the Server

1. **Client Starts Server Process**
   ```
   Client executes: uv run main.py
   Server starts and waits for JSON-RPC messages on stdin
   ```

2. **Client Sends Initialize Request**
   ```json
   {
     "jsonrpc": "2.0",
     "id": 1,
     "method": "initialize",
     "params": {
       "protocolVersion": "2024-11-05",
       "capabilities": {},
       "clientInfo": {"name": "client", "version": "1.0.0"}
     }
   }
   ```

3. **Server Responds with Capabilities**
   ```json
   {
     "jsonrpc": "2.0",
     "id": 1,
     "result": {
       "protocolVersion": "2024-11-05",
       "capabilities": {...},
       "serverInfo": {"name": "NBP", "version": "1.0.0"}
     }
   }
   ```

4. **Client Discovers Available Tools**
   ```json
   Request: {"jsonrpc": "2.0", "id": 2, "method": "tools/list"}

   Response: {
     "jsonrpc": "2.0",
     "id": 2,
     "result": {
       "tools": [
         {
           "name": "get_currency_rate",
           "description": "Get current exchange rate...",
           "inputSchema": {...}
         },
         ...
       ]
     }
   }
   ```

5. **Client Calls Tools**
   ```json
   Request: {
     "jsonrpc": "2.0",
     "id": 3,
     "method": "tools/call",
     "params": {
       "name": "get_currency_rate",
       "arguments": {"code": "USD", "table": "a"}
     }
   }

   Response: {
     "jsonrpc": "2.0",
     "id": 3,
     "result": {
       "content": [
         {"type": "text", "text": "Currency: dolar amerykański\n..."}
       ]
     }
   }
   ```

## Running the Example Client

The `manual_client.py` demonstrates the full communication flow:

```bash
cd nbp-mcp-server
python examples/manual_client.py
```

### What the Example Does

1. Starts the NBP MCP server as a subprocess
2. Sends an initialization request
3. Lists all available tools
4. Calls `get_currency_rate` for USD
5. Calls `get_gold_price`
6. Shows all JSON-RPC messages being exchanged

### Expected Output

```
============================================================
MCP Client Demo - NBP Server
============================================================

============================================================
Step 1: Initialize connection
============================================================

→ Sending request:
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "initialize",
  ...
}

← Received response:
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {...}
}

...

✓ Found 7 tools:
  - get_currency_rate: Get current exchange rate for a currency.
  - get_exchange_table: Get current exchange rate table.
  ...

✓ Tool result:
Currency: dolar amerykański
Code: USD
Table: A
Mid Rate: 3.9876 PLN
...
```

## How Real Clients Use This

### Claude Desktop

Claude Desktop:
1. Reads your config file
2. Starts the server: `uv --directory /path/to/nbp-mcp-server run main.py`
3. Maintains the stdin/stdout connection
4. When you ask "What's the USD rate?", Claude:
   - Decides to call `get_currency_rate`
   - Sends JSON-RPC request via stdin
   - Reads response from stdout
   - Incorporates the result into its response to you

### Other MCP Clients

Any program can be an MCP client if it:
1. Can spawn a subprocess
2. Can send JSON-RPC messages to stdin
3. Can read JSON-RPC responses from stdout
4. Implements the MCP protocol

## Key Concepts

### Why stdio Instead of HTTP?

- **Security**: No network exposure, runs locally
- **Simplicity**: No ports, no networking configuration
- **Process Isolation**: Each client gets its own server instance
- **Standard**: Works everywhere (Windows, Mac, Linux)

### Message Format

All messages are JSON-RPC 2.0:
- Each message is a single line (newline-delimited)
- Request has: `jsonrpc`, `id`, `method`, `params`
- Response has: `jsonrpc`, `id`, `result` (or `error`)

### Tool Execution Flow

```
User asks question
     ↓
Claude decides to use tool
     ↓
Claude sends tools/call request
     ↓
MCP Server executes tool function
     ↓
Server makes HTTP request to NBP API
     ↓
Server formats response
     ↓
Server sends JSON-RPC response
     ↓
Claude incorporates result
     ↓
Claude responds to user
```

## Creating Your Own Client

Here's a minimal example:

```python
import subprocess
import json

# Start server
process = subprocess.Popen(
    ["python", "main.py"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    text=True
)

# Send request
request = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/list",
    "params": {}
}
process.stdin.write(json.dumps(request) + "\n")
process.stdin.flush()

# Read response
response = json.loads(process.stdout.readline())
print(response)
```

## Further Reading

- MCP Specification: https://spec.modelcontextprotocol.io/
- FastMCP Documentation: https://github.com/jlowin/fastmcp
- JSON-RPC 2.0 Spec: https://www.jsonrpc.org/specification
