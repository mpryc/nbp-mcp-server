import argparse
from src.nbp import mcp


def main():
    parser = argparse.ArgumentParser(description="NBP MCP Server")
    parser.add_argument(
        "--transport",
        choices=["stdio", "streamable-http"],
        default="stdio",
        help="Transport type: stdio for CLI or streamable-http for HTTP"
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host to bind to (for streamable-http transport)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind to (for streamable-http transport)"
    )

    args = parser.parse_args()

    if args.transport == "streamable-http":
        # Run with streamable-http transport using uvicorn
        import uvicorn
        # Call FastMCP's streamable_http_app method to get the ASGI app
        app = mcp.streamable_http_app()
        uvicorn.run(
            app,
            host=args.host,
            port=args.port,
            log_level="info"
        )
    else:
        mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
