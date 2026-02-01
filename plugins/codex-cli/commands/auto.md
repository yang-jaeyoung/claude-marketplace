---
description: Execute Codex in full-auto mode for unattended tasks
argument-hint: "<task>"
allowed-tools: ["Bash"]
---

# Codex Auto

Execute Codex CLI in full-auto mode for autonomous task completion.

## Instructions

1. Get the task description from the arguments
2. Run Codex CLI in full-auto mode:

```bash
codex exec --full-auto -m gpt-5.2-codex -s read-only --reasoning medium --skip-git-repo-check "<task>"
```

3. Display the result to the user

## Options

- Model: `gpt-5.2-codex` (optimized for coding tasks)
- Sandbox: `read-only` (safe mode by default)
- Mode: `--full-auto` (autonomous execution)
- Reasoning: `medium` (balanced speed/quality)
- Approval Policy: `never` (full autonomous mode)

## Usage Examples

```
/codex:auto Fix all linting errors in src/
/codex:auto Add type annotations to utils.py
/codex:auto Refactor the database connection handling
/codex:auto Write unit tests for the API endpoints
```

## Caution

- Full-auto mode runs autonomously without human confirmation
- Default sandbox is `read-only` for safety
- Best used for well-defined, scoped tasks
- Review changes after execution
- For potentially destructive tasks, consider using `/codex:code` with manual approval instead
