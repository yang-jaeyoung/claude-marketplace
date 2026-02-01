# Module Context

**Module:** Codex CLI
**Version:** 1.0.0
**Role:** Command-line interface extensions for Codex AI integration.
**Tech Stack:** Markdown commands, YAML frontmatter.

## Prerequisites

- Codex CLI installed and authenticated
- No build step required for this plugin

---

# Operational Commands

```bash
# Plugin reload (if available)
claude plugins reload

# Or restart Claude Code
```

---

# Command Inventory

## Core Commands

- **ask** (`commands/ask.md`): General queries using gpt-5.2 (reasoning: medium)
- **code** (`commands/code.md`): Code-related queries using gpt-5.2-codex (reasoning: medium)
- **review** (`commands/review.md`): Code review using gpt-5.2-codex (reasoning: high)
- **exec** (`commands/exec.md`): Advanced execution with full options control

## Session and Automation

- **resume** (`commands/resume.md`): Resume previous session
- **auto** (`commands/auto.md`): Full-auto mode execution
- **vision** (`commands/vision.md`): Image context queries
- **search** (`commands/search.md`): Web search queries

## Cloud Integration (Experimental)

- **cloud** (`commands/cloud.md`): Create cloud task
- **apply** (`commands/apply.md`): Apply cloud task results

## MCP Integration (Experimental)

- **mcp-server** (`commands/mcp-server.md`): Start Codex as MCP server
- **mcp-list** (`commands/mcp-list.md`): List MCP servers
- **mcp-add** (`commands/mcp-add.md`): Add MCP server

## Utility

- **status** (`commands/status.md`): Check auth status

---

# Implementation Patterns

## Directory Structure

```
codex-cli/
  .claude-plugin/plugin.json
  README.md
  CLAUDE.md
  commands/
    ask.md
    code.md
    review.md
    exec.md
    resume.md
    auto.md
    vision.md
    search.md
    cloud.md
    apply.md
    mcp-server.md
    mcp-list.md
    mcp-add.md
    status.md
```

## Command Definition Pattern

```yaml
---
description: "Short summary"
argument-hint: "<optional-arg>"
allowed-tools: ["Bash"]
---
# Command instructions
```

## Model Selection

- `gpt-5.2`: General purpose, vision, search queries
- `gpt-5.2-codex`: Code-related tasks, auto mode

## Reasoning Effort

- `low`: Quick fixes, simple experiments
- `medium`: General code generation (default)
- `high`: Complex architecture, thorough review

## Approval Policy

- `untrusted`: Require approval for all actions
- `on-request`: Approve on request (default)
- `on-failure`: Only approve on failure
- `never`: Autonomous execution

## Safety Defaults

- Default sandbox: `read-only`
- `--skip-git-repo-check`: For standalone queries
- Cloud/MCP features are experimental

---

# Local Golden Rules

## Do's

- **DO** keep descriptions concise (they appear in help menus).
- **DO** provide usage examples in the markdown body.
- **DO** use `read-only` sandbox by default for safety.
- **DO** mark experimental features clearly.

## Don'ts

- **DON'T** include code blocks requiring external dependencies.
- **DON'T** create complex multi-step logic; use Agent plugins instead.
- **DON'T** use write sandbox without explicit user request.
