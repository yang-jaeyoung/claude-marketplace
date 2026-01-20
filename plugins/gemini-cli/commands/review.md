---
description: Run code review using Gemini CLI
argument-hint: "[file or focus area]"
allowed-tools: ["Bash"]
---

# Gemini Review

Run code review using Google Gemini CLI in headless mode.

## Instructions

1. Check if arguments specify files or focus area
2. Run Gemini CLI review with the appropriate command:

If no arguments provided (review staged changes):
```bash
git diff --cached | gemini -p "Review this code for bugs, security issues, and code quality. Provide specific feedback with line references where applicable."
```

If no staged changes, review unstaged changes:
```bash
git diff | gemini -p "Review this code for bugs, security issues, and code quality. Provide specific feedback with line references where applicable."
```

If specific file provided:
```bash
cat <file> | gemini -p "Review this code for bugs, security issues, and code quality. Provide specific feedback with line references where applicable."
```

3. Display the review results to the user

## Options

- Mode: Headless (`-p` flag for prompt)
- Input: Git diff or file contents piped to Gemini
- Focus: Bugs, security issues, and code quality

## Usage Examples

```
/gemini:review
/gemini:review src/auth.py
/gemini:review api/routes.js
```

## Notes

- This command works best when run inside a git repository
- If no file is specified, it reviews git staged changes (or unstaged if none staged)
- For general questions, use `/gemini:ask`
- For commit messages, use `/gemini:commit`
