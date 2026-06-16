# Jump Off Campus MCP Client

A lightweight, asynchronous MCP client to test and verify the Jump Off Campus MCP server.

## Features
* Connects to the local server via Stdio transport.
* Discovers and lists all tools registered on the server.
* Invokes tools (e.g., `get_house_locations`) and formats the JSON outputs for verification.

## Getting Started

Run the client:
```bash
python apps/src/housing_client.py
```

*Note: The client is configured to locate the server script relatively at `../../../mcp-server/apps/src/housing_server.py`. Ensure that the folder structure is maintained when running.*
