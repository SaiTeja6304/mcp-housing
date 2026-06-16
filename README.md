# Jump Off Campus MCP Project

This repository implements a Model Context Protocol (MCP) server and client for interacting with housing data from Jump Off Campus.

## Directory Structure

* **`mcp-server/`**: Contains the FastMCP server code exposing tools for querying schools, housing listings, and community posts.
* **`mcp-client/`**: Contains a test client to verify the MCP server's exposed tools.
* **`requirements.txt`**: Consolidated dependencies for the workspace.
* **`compose.yml`**: Docker Compose configuration for the client and server services.

---

## Local Setup & Quick Start

1. **Set Up a Virtual Environment & Install Dependencies**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Run the MCP Server (Stdio Transport)**:
   ```bash
   python mcp-server/apps/src/housing_server.py
   ```

3. **Run the Test Client**:
   ```bash
   python mcp-client/apps/src/housing_client.py
   ```

---

## Docker Setup

To build and run the services using Docker Compose:

1. **Build the Docker Images**:
   ```bash
   docker compose build
   ```
   *This command runs the build context from the repository root, allowing both services to share the same `requirements.txt`.*

2. **Start the Containers**:
   ```bash
   docker compose up -d
   ```

> [!NOTE]
> By default, the client spawns the server as a local subprocess via standard I/O (stdio) transport. In a multi-container Docker environment, if you want them to communicate across separate containers, they would require an network-based transport (like SSE), but this repository uses the local stdio transport setup.
