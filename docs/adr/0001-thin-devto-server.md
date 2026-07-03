# ADR 0001: Thin dev.to server; planning in article-research-mcp

- **Status:** accepted
- **Date:** 2026-06-21

## Context

Agents need dev.to access for tutorials. Planning workflows also need dedupe, ranked briefs, and optional HN/RSS — scope creep if added to this package.

## Decision

Keep **devto-mcp-server** as a **lite**, direct DEV API stdio server. Catalogue entry `devto` remains for single-source dev.to workflows, including authenticated article create/update. All planning surfaces live in **article-research-mcp** (`article_research`).

## Consequences

- README and CONTEXT must point planners to the umbrella server.
- Launcher registry tracks both slugs with same path discipline (no duplicate planning tools).
- Write tools require DEV API key auth and should default new posts to drafts unless the caller explicitly publishes.

## Alternatives considered

- Merge into article-research-mcp only — rejected for agents that want minimal tool surface.