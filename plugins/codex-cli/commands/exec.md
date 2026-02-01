---
description: Execute Codex with advanced options (approval-policy, reasoning, sandbox)
argument-hint: "<prompt> [options]"
allowed-tools: ["Bash"]
---

# Codex Exec

Execute Codex CLI with advanced configuration options for fine-grained control.

## Instructions

1. Parse the arguments for options:
   - `-p, --approval-policy`: Approval policy
   - `-r, --reasoning`: Reasoning effort level
   - `-s, --sandbox`: Sandbox mode
   - `-m, --model`: Model selection
   - `--cwd`: Working directory
   - `--instructions`: Custom base instructions

2. Build and run the Codex CLI command with provided options:

```bash
codex exec \
  -m <model> \
  -s <sandbox> \
  --approval-policy <policy> \
  --reasoning <level> \
  [--cwd <directory>] \
  [--base-instructions "<instructions>"] \
  "<prompt>"
```

3. Display the result to the user

## Options

### Approval Policy (`-p, --approval-policy`)
| Value | Description |
|-------|-------------|
| `untrusted` | Require approval for all actions |
| `on-request` | Approve on request |
| `on-failure` | Only approve on failure |
| `never` | Autonomous execution (no approval) |

### Reasoning Effort (`-r, --reasoning`)
| Value | Use Case |
|-------|----------|
| `low` | Quick fixes, simple experiments |
| `medium` | General code generation (default) |
| `high` | Complex architecture, thorough review |

### Sandbox (`-s, --sandbox`)
| Value | Description |
|-------|-------------|
| `read-only` | Safe mode, no file writes (default) |
| `workspace-write` | Can write to workspace |
| `danger-full-access` | Full system access (caution) |

### Model (`-m, --model`)
| Value | Description |
|-------|-------------|
| `gpt-5.2` | General purpose |
| `gpt-5.2-codex` | Code optimized |

## Usage Examples

```
# Basic execution with defaults
/codex:exec "Explain this code"

# High reasoning for complex analysis
/codex:exec -r high "Review the architecture of this project"

# Full-auto mode with workspace write
/codex:exec -p never -s workspace-write "Refactor the utils module"

# Custom working directory
/codex:exec --cwd ./backend "List all API endpoints"

# With custom instructions
/codex:exec --instructions "Focus on security" "Review authentication flow"
```

## Notes

- Default sandbox: `read-only`
- Default reasoning: `medium`
- Default approval-policy: `on-request`
- For simpler use cases, prefer `/codex:code`, `/codex:ask`, or `/codex:auto`
