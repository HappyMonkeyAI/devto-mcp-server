# CONTEXT — devto-mcp-server

Thin **dev.to API** MCP — search, fetch, create, and update posts. Not the planning umbrella.

## Stack

- Python ≥ 3.10, **uv**, **FastMCP** stdio
- **httpx** → `https://dev.to/api`
- Entrypoint: `devto-mcp-server`

## Non-negotiable rules

1. **Thin API tools only** — search, get article, tag/tech search, create article, update article; no briefs/dedupe/ranking here
2. **Planning** — agents use **`article-research-mcp`** (`article_research` catalogue) for `build_topic_brief`, methodology, multi-source
3. **Clean stdio** — `mcp.run(show_banner=False, log_level="WARNING")`
4. **Shared patterns** — httpx helpers may mirror article-research `sources/devto.py`; extract shared lib only with an ADR

## Workflow

- Quick dev.to lookup in isolation → this server
- Before writing implementation plans → `article-research-planning` skill + umbrella MCP
- Doc changes with architecture impact → update ADRs + this file

## Exposure

| Channel | Id |
|---------|-----|
| Dynamic MCP catalogue | `devto` (lite alias) |
| Launcher registry | slug `devto-mcp-server` |

## What not to do

- Do not add Horizon-style scoring or RSS/HN adapters
- Do not duplicate `save_research_note` / `plan_article_research`
- Do not publish catalogue command that omits `--directory` for local dev

## Tools

| Tool | Role |
|------|------|
| `search_devto_posts` | Query search API |
| `get_devto_article` | By id or slug |
| `search_by_tech` | Tag-oriented search |
| `create_devto_article` | Authenticated article/draft creation via DEV API |
| `update_devto_article` | Authenticated article update via DEV API |

## Write auth

- Write tools use `DEVTO_API_KEY` by default, or explicit `api_key` parameter.
- The server also loads repo-local `.env` for `DEVTO_API_KEY` without overriding process env.
- Create defaults to `published=false` for safety.