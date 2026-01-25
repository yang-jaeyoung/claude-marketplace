# Project Context

**Project:** Claude Code Plugins Marketplace
**Purpose:** Monorepo hosting multiple Claude Code plugins for extended functionality.
**Owner:** jyyang

## Tech Stack

- Plugin Definition: Markdown with YAML frontmatter
- MCP Servers: TypeScript, Node.js, `@modelcontextprotocol/sdk`
- Testing: Python 3.x, Pytest (for caw plugin)
- Package Management: npm (per MCP server)

## Operational Commands

```bash
# Install marketplace
claude plugins add github:jyyang/claude-marketplace

# Install specific plugin
claude plugins install <plugin-name>
```

---

# Golden Rules

## Immutable

- **plugin.json Schema:** Only `name`, `version`, `description`, `mcpServers` fields allowed. Any other field causes validation failure.
- **No Hardcoded Secrets:** Never commit API keys, tokens, or credentials.
- **File-Based Discovery:** Commands (`commands/*.md`), agents (`agents/*.md`), skills (`skills/*/SKILL.md`), hooks (`hooks/hooks.json`) are auto-discovered by path, not declared in plugin.json.
- **Registry Sync:** Every plugin MUST be registered in `.claude-plugin/marketplace.json`.

## Do's

- **DO** use lowercase-with-hyphens for plugin names.
- **DO** include `README.md` with usage examples for every plugin.
- **DO** validate YAML frontmatter syntax before committing.
- **DO** use `${CLAUDE_PLUGIN_ROOT}` in hook commands for plugin-relative paths.
- **DO** update `marketplace.json` and root `README.md` when adding/removing plugins.
- **DO** use strict semantic versioning in `plugin.json`.

## Don'ts

- **DON'T** add `author`, `features`, `commands`, `agents`, `skills`, or `hooks` fields to plugin.json.
- **DON'T** use `type: "prompt"` hooks outside of `Stop`/`SubagentStop` events.
- **DON'T** create MCP servers without proper error handling and Zod validation.
- **DON'T** mix language stacks within a single plugin unless necessary.

---

# Standards

## Plugin Types

1. **Markdown-only:** Commands defined as `.md` files (codex-cli, gemini-cli)
2. **MCP Server:** TypeScript server + optional commands (mssql)
3. **Full-featured:** Agents, skills, hooks, commands (context-aware-workflow, intent-based-skills, az-skill-pack)

## Required Plugin Structure

```
plugins/<name>/
  .claude-plugin/plugin.json  # Required: name, version, description
  README.md                   # Required: usage documentation
  commands/*.md               # Optional: slash commands
  agents/*.md                 # Optional: sub-agents
  skills/*/SKILL.md           # Optional: skills
  hooks/hooks.json            # Optional: lifecycle hooks
  mcp-server/                 # Optional: MCP server source
```

## Git Strategy

- Branch: Feature branches from `master`
- Commits: Conventional commits (`feat:`, `fix:`, `docs:`, `chore:`)
- PR: Update CHANGELOG if user-facing changes

## Maintenance Policy

When rules diverge from actual code patterns, propose an update immediately. Ensure `CLAUDE.md` stays in sync with these governance rules.

---

# Context Map

- **[MSSQL Plugin (MCP Server)](./plugins/mssql/AGENTS.md)** — TypeScript MCP server for SQL Server connectivity.
- **[MSSQL MCP Server Source](./plugins/mssql/mcp-server/AGENTS.md)** — TypeScript implementation details and patterns.
- **[Context-Aware Workflow](./plugins/context-aware-workflow/AGENTS.md)** — Advanced agents, skills, hooks orchestration with OMC integration.
- **[Intent-Based Skills](./plugins/intent-based-skills/AGENTS.md)** — Intent-driven skill execution with feedback loops.
- **[AZ Skill Pack](./plugins/az-skill-pack/AGENTS.md)** — Brainstorming, security audit, documentation generation.
- **[Codex CLI](./plugins/codex-cli/AGENTS.md)** — Codex CLI integration commands.
- **[Gemini CLI](./plugins/gemini-cli/AGENTS.md)** — Gemini CLI integration commands.
- **[Rails 8 + Hotwire](./plugins/rails8-hotwire/AGENTS.md)** — Rails 8 full-stack development with Hotwire, specialized agents, and automated hooks.
