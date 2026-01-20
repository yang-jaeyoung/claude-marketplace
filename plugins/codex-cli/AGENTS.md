# Module Context

**Module:** Codex CLI
**Role:** Simple command-line interface extensions defined purely in Markdown.
**Tech Stack:** Markdown, YAML Frontmatter.

# Operational Commands

-   No build step required.
-   Verify by reloading Claude Code plugins: `claude plugins reload` (if available) or restart.

# Commands Overview

## Core Commands
| Command | File | Purpose |
|---------|------|---------|
| `ask` | `commands/ask.md` | General queries (gpt-5.2) |
| `code` | `commands/code.md` | Code-related queries (gpt-5.2-codex) |
| `review` | `commands/review.md` | Code review (gpt-5.2-codex) |

## Session & Automation
| Command | File | Purpose |
|---------|------|---------|
| `resume` | `commands/resume.md` | Resume previous session |
| `auto` | `commands/auto.md` | Full-auto mode execution |
| `vision` | `commands/vision.md` | Image context queries |
| `search` | `commands/search.md` | Web search queries |

## Cloud Integration (Experimental)
| Command | File | Purpose |
|---------|------|---------|
| `cloud` | `commands/cloud.md` | Create cloud task |
| `apply` | `commands/apply.md` | Apply cloud task results |

## MCP Integration (Experimental)
| Command | File | Purpose |
|---------|------|---------|
| `mcp-list` | `commands/mcp-list.md` | List MCP servers |
| `mcp-add` | `commands/mcp-add.md` | Add MCP server |

## Utility
| Command | File | Purpose |
|---------|------|---------|
| `status` | `commands/status.md` | Check auth status |

# Implementation Patterns

## Command Definition
-   File: `commands/<command-name>.md`
-   Frontmatter:
    ```yaml
    ---
    description: "Short summary"
    argument-hint: "<optional-arg>"
    allowed-tools: ["Bash"]
    ---
    ```

## Model Selection
- `gpt-5.2`: General purpose, vision, search queries
- `gpt-5.2-codex`: Code-related tasks, auto mode

## Safety
- Default sandbox: `read-only`
- `--skip-git-repo-check`: For standalone queries
- Cloud/MCP: Experimental features

# Local Golden Rules

## Do's
-   **DO** keep descriptions concise (they appear in help menus).
-   **DO** provide usage examples in the markdown body.
-   **DO** use `read-only` sandbox by default for safety.
-   **DO** mark experimental features clearly.

## Don'ts
-   **DON'T** include executable code blocks that require external dependencies not present in the base environment.
-   **DON'T** create complex multi-step logic here; use a full Agent plugin for that.
-   **DON'T** use write sandbox without explicit user request.
