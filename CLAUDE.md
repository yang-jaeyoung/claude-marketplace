# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

# Project Context

**Project:** Claude Code Plugins Marketplace
**Purpose:** Monorepo hosting multiple Claude Code plugins for extended functionality.
**Owner:** jyyang

## Tech Stack

- Plugin Definition: Markdown with YAML frontmatter
- Hook Scripts: Python 3.x
- Testing: Pytest (context-aware-workflow plugin)
- Package Management: npm (for future MCP servers)

## Operational Commands

```bash
# Install marketplace
claude plugins add github:jyyang/claude-marketplace

# Install specific plugin
claude plugins install <plugin-name>

# Clear plugin cache
rm -rf ~/.claude/plugins/cache/<marketplace>/<plugin>/

# Run tests (context-aware-workflow)
cd plugins/context-aware-workflow && python -m pytest tests/
```

---

# Golden Rules

## Immutable

- **plugin.json Schema:** Only `name`, `version`, `description`, `mcpServers` fields allowed. Any other field causes validation failure.
- **File-Based Discovery:** Commands (`commands/*.md`), agents (`agents/*.md`), skills (`skills/*/SKILL.md`), hooks (`hooks/hooks.json`) are auto-discovered by path, not declared in plugin.json.
- **Registry Sync:** Every plugin MUST be registered in `.claude-plugin/marketplace.json`.

## Cross-Platform (REQUIRED)

- **Paths:** Use `/` (auto-handled), `path.join()`, `os.path.join()`
- **Commands:** Use `python3` or `node` (NOT cat/rm/type/sh)
- **Wrap paths:** `"${CLAUDE_PLUGIN_ROOT}/path"`
- **Note:** `${CLAUDE_PLUGIN_ROOT}` is runtime substitution, NOT env var

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

---

# Standards

## Plugin Types

1. **Markdown-only:** Commands as `.md` files (codex-cli, gemini-cli)
2. **Full-featured:** Agents, skills, hooks, commands (context-aware-workflow)
3. **MCP Server:** TypeScript server + optional commands (future plugins)

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

## Components Reference

| Type | Location | Key Fields |
|------|----------|------------|
| Commands | `commands/*.md` | description, allowed-tools, context, agent, model, hooks |
| Agents | `agents/*.md` | name, description, model(sonnet/opus/haiku), tools, mcp_servers |
| Skills | `skills/*/SKILL.md` | name, description, allowed-tools, context:fork |
| Hooks | `hooks/hooks.json` | PreToolUse, PostToolUse, Stop, Setup, SessionStart, etc |

## Agents Tiering

- **Base:** `<name>.md` (Sonnet)
- **Fast:** `<name>-haiku.md`
- **Complex:** `<name>-opus.md`

## Hooks

- `type:command` — all events
- `type:prompt` — ONLY Stop, SubagentStop

## Git Strategy

- Branch: Feature branches from `master`
- Commits: Conventional commits (`feat:`, `fix:`, `docs:`, `chore:`)
- PR: Update CHANGELOG if user-facing changes

## Maintenance Policy

When rules diverge from actual code patterns, propose an update immediately. Ensure `AGENTS.md` stays in sync with these governance rules.

---

# Context Map

## Active Plugins (3)

- **[Context-Aware Workflow](./plugins/context-aware-workflow/AGENTS.md)** — Full-featured plugin with agents, skills, hooks, Plan Mode integration, Ralph Loop, and Gemini CLI async reviews.
- **[Codex CLI](./plugins/codex-cli/AGENTS.md)** — Markdown-only plugin for Codex CLI integration (12 commands).
- **[Gemini CLI](./plugins/gemini-cli/AGENTS.md)** — Markdown-only plugin for Gemini CLI integration (6 commands).

