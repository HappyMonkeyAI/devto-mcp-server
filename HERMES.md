# HERMES.md — devto-mcp-server

## When to use this vs article-research-mcp

| Need | Server |
|------|--------|
| Single dev.to search/fetch/create/update | **devto** (this repo) |
| Planning brief, HN/RSS, methodology | **article_research** |

## Smoke

```bash
cd /home/stephen/projects/devto-mcp-server
uv sync && uv run devto-mcp-server
```

Read `CONTEXT.md` and `docs/adr/` before extending tools.

Write-tool smoke should use mocks unless the user explicitly asks to publish a real post. Real writes require `DEVTO_API_KEY`.