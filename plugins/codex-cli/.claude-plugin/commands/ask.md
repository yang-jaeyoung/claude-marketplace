---
description: Execute general queries using Codex CLI with gpt-5.2 model
argument-hint: "<question>"
allowed-tools: ["Bash"]
---

# Codex Ask

Execute general (non-code) queries using Codex CLI.

## Instructions

1. Get the user's question from the arguments
2. Run Codex CLI with the following command:

```bash
codex exec -m gpt-5.2 -s read-only --skip-git-repo-check "<user_question>"
```

3. Display the result to the user

## Options

- Model: `gpt-5.2` (general purpose)
- Sandbox: `read-only` (safe mode)
- Working directory: Current directory

## Usage Examples

```
/codex:ask What is the capital of France?
/codex:ask Explain quantum computing in simple terms
/codex:ask How does HTTP work?
```

## Notes

- For code-related questions, use `/codex:code` instead (uses gpt-5.2-codex model)
- For code review, use `/codex:review`
