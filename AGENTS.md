# Project Context & Operations

**Project:** Claude Marketplace (Monorepo)
**Description:** A registry and collection of plugins for Claude Code, including MCP servers, agentic workflows, and markdown commands.
**Core Stack:** Mixed (TypeScript for MCP, Python for agents, Markdown/YAML for simple plugins).

## Operational Commands
Since this is a monorepo, build and test commands are specific to each plugin.
- **Dependency Install:** See specific plugin directories.
- **Global Registry:** `.claude-plugin/marketplace.json` must be updated when adding plugins.

# Golden Rules

## Immutable Standards
1.  **Registry Synchronization:** Every new plugin MUST be registered in `.claude-plugin/marketplace.json`.
2.  **Manifest Compliance:** All plugins MUST have a `.claude-plugin/plugin.json` adhering to the core schema.
3.  **No Broken Links:** The `README.md` table of plugins MUST be kept in sync with the file structure.

## Do's & Don'ts
-   **DO** use strict semantic versioning in `plugin.json`.
-   **DO** provide a dedicated `README.md` for every plugin.
-   **DON'T** mix language stacks within a single plugin unless necessary (keep Python and TS plugins distinct).
-   **DON'T** commit credentials or `.env` files.

# Standards & References

## Git Strategy
-   Commit messages: Conventional Commits (feat, fix, docs, chore).
-   Branching: Feature branches merged into main.

## Maintenance Policy
-   If you find this document outdated, propose an update immediately.
-   Ensure `CLAUDE.md` is kept in sync with these governance rules.

# Context Map (Action-Based Routing)

- **[SQL Server MCP Plugin (TypeScript)](./plugins/mssql/AGENTS.md)** — Backend logic, MCP server implementation, Node.js tooling.
- **[Context Aware Workflow (Python)](./plugins/context-aware-workflow/AGENTS.md)** — Agent logic, complex workflows, Python/Pytest tasks, OMC integration.
- **[Codex CLI (Markdown)](./plugins/codex-cli/AGENTS.md)** — Static command definitions, pure Markdown/YAML editing.
- **[Gemini CLI (Markdown)](./plugins/gemini-cli/README.md)** — Google Gemini CLI integration for code review, commits, docs.
- **[Intent-Based Skills (Python)](./plugins/intent-based-skills/README.md)** — Intent framework, project analyzers, research orchestrator.
- **[AZ Skill Pack (Markdown)](./plugins/az-skill-pack/README.md)** — Brainstorming, security audits, documentation generation.
