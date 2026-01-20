---
description: Generate commit message from staged changes using Gemini
argument-hint: ""
allowed-tools: ["Bash"]
---

# Gemini Commit

Generate a commit message from staged changes using Google Gemini CLI.

## Instructions

1. Check for staged changes using `git diff --cached`
2. If no staged changes, inform the user and exit
3. Run Gemini CLI to generate commit message:

```bash
git diff --cached | gemini -p "Write a concise commit message for these changes. Follow conventional commit format (type: description). Types include: feat, fix, docs, style, refactor, test, chore. Keep the first line under 72 characters."
```

4. Display the suggested commit message to the user

## Options

- Mode: Headless (`-p` flag for prompt)
- Input: Git staged diff piped to Gemini
- Format: Conventional commits

## Usage Examples

```
/gemini:commit
```

## Output Format

The generated commit message will follow conventional commit format:

```
type(scope): brief description

- Detailed change 1
- Detailed change 2
```

## Notes

- Stage your changes with `git add` before running this command
- Review the suggested message before committing
- For code review, use `/gemini:review`
- For documentation, use `/gemini:docs`
