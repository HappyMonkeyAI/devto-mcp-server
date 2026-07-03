# devto-mcp-server

MCP server providing tools to search, retrieve, create, and update articles via the dev.to API.

**For agent planning workflows**, use the umbrella server **`article-research-mcp`** (`article_research` in Dynamic MCP catalogue) — dedupe, ranked briefs, methodology, and `save_research_note`.

**Agent docs:** `CONTEXT.md`, `HERMES.md`, `docs/adr/`

## Tools

- `search_devto_posts`: Search dev.to articles by query, with optional tag, limit, etc.
- `get_devto_article`: Fetch full article by ID or slug.
- `search_by_tech`: Search articles by technology/tag (e.g., python, ai, mcp).
- `create_devto_article`: Create a draft or published dev.to article. Uses `DEVTO_API_KEY` unless `api_key` is passed.
- `update_devto_article`: Update fields on an existing dev.to article. Uses `DEVTO_API_KEY` unless `api_key` is passed.

## Auth for write tools

Create a DEV API key at https://dev.to/settings/extensions, then set:

```bash
export DEVTO_API_KEY=your_key_here
```

For local development, you can also put the key in the repo-local `.env` file:

```dotenv
DEVTO_API_KEY=your_key_here
```

`.env` is ignored by git; `.env.example` documents the expected variable.

`create_devto_article` defaults `published` to `false` so new API-created posts are drafts unless explicitly published.

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

