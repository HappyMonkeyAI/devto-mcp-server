#!/usr/bin/env python3
"""dev.to MCP Server - Wraps dev.to public API with useful research tools."""

import httpx
from mcp.server.fastmcp import FastMCP
from typing import Optional, List, Dict, Any

# Create the MCP server
mcp = FastMCP("devto-mcp-server")

DEVTO_API_BASE = "https://dev.to/api"


async def _fetch_json(url: str, params: Optional[Dict] = None) -> Any:
    """Helper to fetch JSON from dev.to API."""
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.get(url, params=params)
        resp.raise_for_status()
        return resp.json()


@mcp.tool()
async def search_devto_posts(
    query: str,
    tag: Optional[str] = None,
    per_page: int = 10,
    page: int = 1,
    top: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """
    Search dev.to articles.

    Args:
        query: Search term (searches title, body, tags, user).
        tag: Optional tag filter (e.g. 'python', 'ai').
        per_page: Number of results (max 30).
        page: Pagination page.
        top: If set (e.g. 7 for past week), returns top articles instead of search.

    Returns:
        List of article summaries with id, title, url, tags, etc.
    """
    params: Dict[str, Any] = {
        "search": query,
        "per_page": min(per_page, 30),
        "page": page,
    }
    if tag:
        params["tag"] = tag
    if top:
        params["top"] = top
        # When using top, search param may be ignored; use tag instead

    url = f"{DEVTO_API_BASE}/articles"
    articles = await _fetch_json(url, params)
    return articles


@mcp.tool()
async def get_devto_article(article_id: int) -> Dict[str, Any]:
    """
    Retrieve a full dev.to article by its ID.

    Args:
        article_id: The numeric ID of the article.

    Returns:
        Full article object including body_markdown, tags, reactions, etc.
    """
    url = f"{DEVTO_API_BASE}/articles/{article_id}"
    return await _fetch_json(url)


@mcp.tool()
async def search_by_tech(
    tech: str,
    per_page: int = 15,
    top_days: Optional[int] = 30,
) -> List[Dict[str, Any]]:
    """
    Search articles by technology/tag. Convenience wrapper around search.

    Args:
        tech: Technology or tag (e.g. 'python', 'fastapi', 'mcp', 'ai').
        per_page: Number of results.
        top_days: Return top articles from last N days (7, 30, etc.). If None, does text search on tag.

    Returns:
        List of matching articles.
    """
    params: Dict[str, Any] = {
        "tag": tech.lower(),
        "per_page": min(per_page, 30),
    }
    if top_days:
        params["top"] = top_days

    url = f"{DEVTO_API_BASE}/articles"
    articles = await _fetch_json(url, params)
    return articles


@mcp.resource("devto://article/{article_id}")
async def get_article_resource(article_id: str) -> str:
    """Resource URI for fetching article content as markdown."""
    article = await get_devto_article(int(article_id))
    return article.get("body_markdown", article.get("description", ""))


def main():
    """Entry point for the MCP server."""
    mcp.run(show_banner=False, log_level="WARNING")


if __name__ == "__main__":
    main()
