---
description: Run code review on current repository using Codex CLI
argument-hint: "[optional: specific files or focus area]"
allowed-tools: ["Bash"]
---

# Codex Review

Run code review on the current repository using Codex CLI.

## Instructions

1. Check if arguments specify files or focus area
2. Run Codex CLI review with the following command:

If no arguments provided:
```bash
codex review -m gpt-5.2-codex -s read-only
```

If specific focus area or files provided:
```bash
codex exec -m gpt-5.2-codex -s read-only "Review the code: <user_args>"
```

3. Display the review results to the user

## Options

- Model: `gpt-5.2-codex` (optimized for code analysis)
- Sandbox: `read-only` (safe mode)
- Working directory: Current directory (should be a git repository)

## Usage Examples

```
/codex:review
/codex:review src/main.py
/codex:review Focus on security vulnerabilities
/codex:review Check for performance issues in the API handlers
```

## Notes

- This command works best when run inside a git repository
- Uses the `gpt-5.2-codex` model for code-focused analysis
- For general questions, use `/codex:ask`
- For code-related questions, use `/codex:code`
