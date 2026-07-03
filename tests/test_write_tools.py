import asyncio

import pytest

from devto_mcp_server import server


def test_article_payload_keeps_false_and_omits_none():
    payload = server._article_payload(
        title="Draft",
        body_markdown="# Body",
        published=False,
        tags=None,
        canonical_url="https://example.com/post",
    )

    assert payload == {
        "article": {
            "title": "Draft",
            "body_markdown": "# Body",
            "published": False,
            "canonical_url": "https://example.com/post",
        }
    }


def test_get_api_key_prefers_explicit_key(monkeypatch):
    monkeypatch.setenv("DEVTO_API_KEY", "from-env")

    assert server._get_api_key("explicit") == "explicit"


def test_get_api_key_requires_value(tmp_path, monkeypatch):
    monkeypatch.delenv("DEVTO_API_KEY", raising=False)
    monkeypatch.setattr(server, "DOTENV_PATH", tmp_path / ".env")

    with pytest.raises(ValueError, match="DEVTO_API_KEY"):
        server._get_api_key()


def test_get_api_key_loads_local_dotenv(tmp_path, monkeypatch):
    monkeypatch.delenv("DEVTO_API_KEY", raising=False)
    dotenv = tmp_path / ".env"
    dotenv.write_text("DEVTO_API_KEY=from-dotenv\n", encoding="utf-8")

    server._load_local_env(dotenv)

    assert server._get_api_key() == "from-dotenv"


def test_create_devto_article_posts_wrapped_payload(monkeypatch):
    calls = []

    class FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {"id": 123, "title": "Draft"}

    class FakeAsyncClient:
        def __init__(self, timeout):
            self.timeout = timeout

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def request(self, method, url, json, headers):
            calls.append(
                {
                    "method": method,
                    "url": url,
                    "json": json,
                    "headers": headers,
                }
            )
            return FakeResponse()

    monkeypatch.setattr(server.httpx, "AsyncClient", FakeAsyncClient)

    result = asyncio.run(
        server.create_devto_article(
            title="Draft",
            body_markdown="# Body",
            published=False,
            tags="ai,mcp",
            api_key="secret-key",
        )
    )

    assert result == {"id": 123, "title": "Draft"}
    assert calls == [
        {
            "method": "POST",
            "url": "https://dev.to/api/articles",
            "json": {
                "article": {
                    "title": "Draft",
                    "body_markdown": "# Body",
                    "published": False,
                    "tags": "ai,mcp",
                }
            },
            "headers": {"api-key": "secret-key", "Content-Type": "application/json"},
        }
    ]


def test_update_devto_article_rejects_empty_update():
    with pytest.raises(ValueError, match="at least one article field"):
        asyncio.run(server.update_devto_article(article_id=123, api_key="secret-key"))
