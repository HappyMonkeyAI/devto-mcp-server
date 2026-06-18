# devto-mcp-server

MCP server providing tools to search and retrieve articles from dev.to API.

## Tools

- `search_devto_posts`: Search dev.to articles by query, with optional tag, limit, etc.
- `get_devto_article`: Fetch full article by ID or slug.
- `search_by_tech`: Search articles by technology/tag (e.g., python, ai, mcp).

## Usage with dynamic-mcp-proxy-server

Add to catalogue.json:

```json
{
  "name": "devto",
  "description": "dev.to MCP server — search and read technical articles, tutorials, and posts",
  "command": "uvx devto-mcp-server",
  "tags": ["devto", "articles", "blog", "tech", "research", "tutorials"],
  "tech_stack": ["any"],
  "runtime": "stdio",
  "env_vars": []
}
```

Run directly:
```bash
uv run devto-mcp-server
```

Or with uvx after publishing (for now local: uvx --from . devto-mcp-server)

## Configuration for Claude Desktop

Add the following to your `claude_desktop_config.json` (located at `~/Library/Application Support/Claude/claude_desktop_config.json` on macOS, or `%APPDATA%\Claude\claude_desktop_config.json` on Windows):

```json
{
  "mcpServers": {
    "devto": {
      "command": "uv",
      "args": [
        "--directory",
        "/absolute/path/to/devto-mcp-server",
        "run",
        "devto-mcp-server"
      ]
    }
  }
}
```

## License

This project is licensed under the MIT License - see the [LICENSE](file:///home/stephen/projects/devto-mcp-server/LICENSE) file for details.

