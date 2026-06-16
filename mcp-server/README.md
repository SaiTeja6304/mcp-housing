# Jump Off Campus MCP Server

An MCP server built with `FastMCP` that provides access to the Jump Off Campus off-campus housing platform.

## Available Tools

The server registers and exposes the following tools:

1. **`get_house_locations`**: Retrieves all available universities and their corresponding subdomain slugs.
2. **`get_housing_listings`**: Retrieves listing summaries (price, beds, move-in dates) for a given university slug.
3. **`filter_house_information`**: Filters detailed housing listings based on criteria (price range, beds, amenities, move-in dates, etc.) and provides a `listing_path`.
4. **`get_house_link`**: Generates a full URL to the housing listing using the university slug and `listing_path`.
5. **`get_slug_posts`**: Lists community posts/announcements for a given university subdomain.
6. **`get_slug_post`**: Retrieves the full content of a specific community post by its ID.

---

## Getting Started

### Local Execution

Run the server directly:
```bash
python apps/src/housing_server.py
```

### Integration with Host LLMs

To expose these tools to an LLM, add the server to your LLM application configuration using the stdio transport.

#### 1. Claude Desktop
Add this to `%APPDATA%\Claude\claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "jumpoffcampus": {
      "command": "python",
      "args": ["D:/AIprojects/claude-mcp/mcp-server/apps/src/housing_server.py"]
    }
  }
}
```
*(Make sure to update the python executable path and the script path to your absolute paths).*

#### 2. Cursor
Configure it via Cursor settings under **Features** -> **MCP** by adding a new command-based server:
* **Name**: `jumpoffcampus`
* **Type**: `command`
* **Command**: `python D:/AIprojects/claude-mcp/mcp-server/apps/src/housing_server.py`
