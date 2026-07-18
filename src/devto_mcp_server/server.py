#!/usr/bin/env python3
"""dev.to MCP Server - Wraps dev.to public API with useful research tools."""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import httpx
from mcp.server.fastmcp import FastMCP

# Create the MCP server
mcp = FastMCP("devto-mcp-server")

DEVTO_API_BASE = "https://dev.to/api"
DEVTO_API_KEY_ENV = "DEVTO_API_KEY"
DOTENV_PATH = Path.cwd() / ".env"


def _load_local_env(path: Optional[Path] = None) -> None:
    """Load simple KEY=VALUE pairs from a local .env without overriding process env."""
    dotenv_path = path or DOTENV_PATH
    if not dotenv_path.exists():
        return
    for raw_line in dotenv_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


async def _fetch_json(url: str, params: Optional[Dict[str, Any]] = None) -> Any:
    """Helper to fetch JSON from dev.to API."""
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.get(url, params=params)
        resp.raise_for_status()
        return resp.json()


def _get_api_key(api_key: Optional[str] = None) -> str:
    """Resolve a DEV API key from an explicit parameter, process env, or local .env."""
    if not api_key:
        _load_local_env()
    resolved = api_key or os.getenv(DEVTO_API_KEY_ENV)
    if not resolved:
        raise ValueError(
            f"dev.to write tools require an API key. Pass api_key or set {DEVTO_API_KEY_ENV}."
        )
    return resolved


def _article_payload(
    *,
    title: Optional[str] = None,
    body_markdown: Optional[str] = None,
    published: Optional[bool] = None,
    tags: Optional[str] = None,
    description: Optional[str] = None,
    canonical_url: Optional[str] = None,
    series: Optional[str] = None,
    main_image: Optional[str] = None,
    organization_id: Optional[int] = None,
) -> Dict[str, Dict[str, Any]]:
    """Build the wrapped Article payload expected by the DEV/Forem API."""
    article: Dict[str, Any] = {}
    normalized_tags = None
    if tags is not None:
        normalized_tags = [tag.strip() for tag in tags.split(",") if tag.strip()]
    for key, value in {
        "title": title,
        "body_markdown": body_markdown,
        "published": published,
        # Forem's current API accepts tags as an array. It may silently discard
        # the legacy comma-delimited string while still returning HTTP 201.
        "tags": normalized_tags,
        "description": description,
        "canonical_url": canonical_url,
        "series": series,
        "main_image": main_image,
        "organization_id": organization_id,
    }.items():
        if value is not None:
            article[key] = value
    return {"article": article}


async def _send_article_request(
    method: str,
    url: str,
    payload: Dict[str, Dict[str, Any]],
    api_key: Optional[str] = None,
) -> Dict[str, Any]:
    """Send an authenticated article create/update request to DEV."""
    key = _get_api_key(api_key)
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.request(
            method,
            url,
            json=payload,
            headers={"api-key": key, "Content-Type": "application/json"},
        )
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


@mcp.tool()
async def create_devto_article(
    title: str,
    body_markdown: str,
    published: bool = False,
    tags: Optional[str] = None,
    description: Optional[str] = None,
    canonical_url: Optional[str] = None,
    series: Optional[str] = None,
    main_image: Optional[str] = None,
    organization_id: Optional[int] = None,
    api_key: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Create a dev.to article or draft using the authenticated DEV API.

    Args:
        title: Article title.
        body_markdown: Article body in markdown.
        published: Publish immediately when true. Defaults to false for safety.
        tags: Comma-separated tags, e.g. "python,ai,mcp".
        description: Short article description.
        canonical_url: Original/canonical URL when cross-posting.
        series: Optional DEV series name.
        main_image: Optional main image URL.
        organization_id: Optional DEV organization id.
        api_key: Optional DEV API key. If omitted, DEVTO_API_KEY is used.

    Returns:
        The created article object from dev.to.
    """
    payload = _article_payload(
        title=title,
        body_markdown=body_markdown,
        published=published,
        tags=tags,
        description=description,
        canonical_url=canonical_url,
        series=series,
        main_image=main_image,
        organization_id=organization_id,
    )
    return await _send_article_request("POST", f"{DEVTO_API_BASE}/articles", payload, api_key)


@mcp.tool()
async def update_devto_article(
    article_id: int,
    title: Optional[str] = None,
    body_markdown: Optional[str] = None,
    published: Optional[bool] = None,
    tags: Optional[str] = None,
    description: Optional[str] = None,
    canonical_url: Optional[str] = None,
    series: Optional[str] = None,
    main_image: Optional[str] = None,
    organization_id: Optional[int] = None,
    api_key: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Update an existing dev.to article by numeric article id.

    Only fields provided as non-null arguments are sent. Pass api_key or set DEVTO_API_KEY.
    """
    payload = _article_payload(
        title=title,
        body_markdown=body_markdown,
        published=published,
        tags=tags,
        description=description,
        canonical_url=canonical_url,
        series=series,
        main_image=main_image,
        organization_id=organization_id,
    )
    if not payload["article"]:
        raise ValueError("update_devto_article requires at least one article field to update.")
    return await _send_article_request(
        "PUT", f"{DEVTO_API_BASE}/articles/{article_id}", payload, api_key
    )


@mcp.resource("devto://article/{article_id}")
async def get_article_resource(article_id: str) -> str:
    """Resource URI for fetching article content as markdown."""
    article = await get_devto_article(int(article_id))
    return article.get("body_markdown", article.get("description", ""))


def main():
    """Entry point for the MCP server."""
    # mcp.server.fastmcp.FastMCP.run() no longer accepts the newer
    # fastmcp package's show_banner/log_level keyword arguments.
    mcp.run()


if __name__ == "__main__":
    main()
