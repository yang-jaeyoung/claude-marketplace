---
description: Execute code-related queries using Codex CLI with gpt-5.2-codex model
argument-hint: "<code_question>"
allowed-tools: ["Bash"]
---

# Codex Code

Execute code-related queries using Codex CLI with the specialized coding model.

## Instructions

1. Get the user's code-related question from the arguments
2. Run Codex CLI with the following command:

```bash
codex exec -m gpt-5.2-codex -s read-only --reasoning medium --skip-git-repo-check "<user_question>"
```

3. Display the result to the user

## Options

- Model: `gpt-5.2-codex` (optimized for coding tasks)
- Sandbox: `read-only` (safe mode)
- Reasoning: `medium` (balanced speed/quality)
- Working directory: Current directory

## Usage Examples

```
/codex:code How do I implement a binary search in Python?
/codex:code Explain this regex pattern: ^[a-zA-Z0-9]+$
/codex:code What's the best way to handle async errors in JavaScript?
/codex:code Write a function to validate email addresses
```

## Notes

- This command uses the `gpt-5.2-codex` model optimized for code generation and understanding
- For general questions, use `/codex:ask` instead
- For code review, use `/codex:review`
