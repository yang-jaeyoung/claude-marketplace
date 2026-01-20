---
description: Ask Gemini a question using headless mode
argument-hint: "<question>"
allowed-tools: ["Bash"]
---

# Gemini Ask

Execute general queries using Google Gemini CLI in headless mode.

## Instructions

1. Get the user's question from the arguments
2. Run Gemini CLI with the following command:

```bash
gemini -p "<user_question>"
```

3. Display the result to the user

## Options

- Mode: Headless (`-p` flag for prompt)
- Working directory: Current directory

## Usage Examples

```
/gemini:ask What is machine learning?
/gemini:ask Explain the difference between REST and GraphQL
/gemini:ask How does garbage collection work in Python?
```

## Notes

- For code review, use `/gemini:review`
- For commit message generation, use `/gemini:commit`
- For documentation generation, use `/gemini:docs`
