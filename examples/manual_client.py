#!/usr/bin/env python3
"""
Simple example client to demonstrate MCP communication.
This shows how an MCP client interacts with an MCP server.
"""
import subprocess
import json
import sys


class SimpleMCPClient:
    def __init__(self, command):
        """Start the MCP server as a subprocess."""
        self.process = subprocess.Popen(
            command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        self.request_id = 0

    def send_request(self, method, params=None):
        """Send a JSON-RPC request to the server."""
        self.request_id += 1
        request = {
            "jsonrpc": "2.0",
            "id": self.request_id,
            "method": method,
            "params": params or {}
        }

        print(f"\n→ Sending request:")
        print(json.dumps(request, indent=2))

        # Send request
        self.process.stdin.write(json.dumps(request) + "\n")
        self.process.stdin.flush()

        # Read response
        response_line = self.process.stdout.readline()
        if not response_line:
            return None

        response = json.loads(response_line)
        print(f"\n← Received response:")
        print(json.dumps(response, indent=2))

        return response

    def close(self):
        """Close the connection to the server."""
        self.process.stdin.close()
        self.process.stdout.close()
        self.process.terminate()
        self.process.wait()


def main():
    print("=" * 60)
    print("MCP Client Demo - NBP Server")
    print("=" * 60)

    # Start the server
    client = SimpleMCPClient(["python", "main.py"])

    try:
        # 1. Initialize the connection
        print("\n" + "=" * 60)
        print("Step 1: Initialize connection")
        print("=" * 60)
        client.send_request("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {
                "name": "simple-client",
                "version": "1.0.0"
            }
        })

        # 2. List available tools
        print("\n" + "=" * 60)
        print("Step 2: List available tools")
        print("=" * 60)
        response = client.send_request("tools/list")

        if response and "result" in response:
            tools = response["result"].get("tools", [])
            print(f"\n✓ Found {len(tools)} tools:")
            for tool in tools:
                print(f"  - {tool['name']}: {tool['description']}")

        # 3. Call a tool - get current USD rate
        print("\n" + "=" * 60)
        print("Step 3: Call get_currency_rate for USD")
        print("=" * 60)
        response = client.send_request("tools/call", {
            "name": "get_currency_rate",
            "arguments": {
                "code": "USD",
                "table": "a"
            }
        })

        if response and "result" in response:
            content = response["result"].get("content", [])
            if content:
                print(f"\n✓ Tool result:")
                print(content[0].get("text", "No text content"))

        # 4. Call another tool - get gold price
        print("\n" + "=" * 60)
        print("Step 4: Call get_gold_price")
        print("=" * 60)
        response = client.send_request("tools/call", {
            "name": "get_gold_price",
            "arguments": {}
        })

        if response and "result" in response:
            content = response["result"].get("content", [])
            if content:
                print(f"\n✓ Tool result:")
                print(content[0].get("text", "No text content"))

        print("\n" + "=" * 60)
        print("Demo completed successfully!")
        print("=" * 60)

    except Exception as e:
        print(f"\n✗ Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
    finally:
        client.close()


if __name__ == "__main__":
    main()
