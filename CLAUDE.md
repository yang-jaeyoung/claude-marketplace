# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

# Project Context

**Project:** Claude Code Plugins Marketplace
**Purpose:** Monorepo hosting multiple Claude Code plugins for extended functionality.
**Owner:** jaebit

## Tech Stack

- Plugin Definition: Markdown with YAML frontmatter
- Hook Scripts: Python 3.x
- Testing: Pytest (context-aware-workflow plugin)
- Package Management: npm (for future MCP servers)

## Operational Commands

```bash
# Install marketplace
claude plugins add github:jaebit/context-aware-workflow

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
| Agents | `agents/*.md` | name, description, model, tools, mcp_servers, whenToUse, color, tier, skills |
| Skills | `skills/*/SKILL.md` | name, description, allowed-tools, context:fork |
| Hooks | `hooks/hooks.json` | PreToolUse, PostToolUse, Stop, Setup, SessionStart, etc |

## Agents Schema

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Agent identifier (lowercase or PascalCase) |
| `description` | string | Brief description of agent purpose |
| `model` | enum | `sonnet`, `opus`, or `haiku` |
| `tools` | array | List of allowed tools |

### Optional Fields

| Field | Type | Description |
|-------|------|-------------|
| `mcp_servers` | array | MCP servers to enable (serena, sequential, context7, perplexity) |
| `whenToUse` | string | Multi-line guidance for when to invoke this agent |
| `color` | string | Display color hint for UI (green, blue, orange, purple, etc.) |
| `tier` | string | Explicit tier label for tiered variants (haiku, sonnet, opus) |
| `skills` | string | Comma-separated list of integrated skills |

## Agents Tiering

### Naming Convention

- **Base:** `<name>.md` — Default tier, typically Sonnet (but may use Opus for complex-by-default agents)
- **Fast:** `<name>-haiku.md` — Lightweight, speed-optimized
- **Complex:** `<name>-opus.md` — Deep analysis, comprehensive

### Model Selection by Complexity

| Complexity | Tier | Model | Use Case |
|------------|------|-------|----------|
| ≤ 0.3 | Haiku | haiku | Boilerplate, simple CRUD, formatting |
| 0.3 - 0.7 | Sonnet | sonnet | Standard features, typical tasks |
| > 0.7 | Opus | opus | Architecture, security, large refactoring |

### Escalation Pattern

Agents should include escalation guidance when task complexity exceeds their tier:
- Haiku → "⚠️ Task more complex. Sonnet recommended."
- Sonnet → "⚠️ Higher complexity. Opus recommended."
- Opus → "ℹ️ Task simpler than expected. Sonnet tier would be efficient."

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
- **[Codex CLI](./plugins/codex-cli/CLAUDE.md)** — Markdown-only plugin for Codex CLI integration (14 commands).
- **[Gemini CLI](./plugins/gemini-cli/AGENTS.md)** — Markdown-only plugin for Gemini CLI integration (6 commands).

