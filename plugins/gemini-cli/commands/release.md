---
description: Generate release notes from git commits using Gemini
argument-hint: "<from-tag>"
allowed-tools: ["Bash"]
---

# Gemini Release

Generate release notes from git commits using Google Gemini CLI.

## Instructions

1. Get the tag from arguments
2. If no tag specified, try to use the most recent tag:

```bash
git describe --tags --abbrev=0
```

3. Get commits since the specified tag:

```bash
git log --oneline <tag>..HEAD | gemini -p "Generate professional release notes from these commits. Group changes by category (Features, Bug Fixes, Improvements, Breaking Changes). Use markdown format with bullet points. Include a brief summary at the top."
```

4. If no tag exists, use last 20 commits:

```bash
git log --oneline -20 | gemini -p "Generate professional release notes from these commits. Group changes by category (Features, Bug Fixes, Improvements, Breaking Changes). Use markdown format with bullet points. Include a brief summary at the top."
```

5. Display the release notes to the user

## Options

- Mode: Headless (`-p` flag for prompt)
- Input: Git commit log piped to Gemini
- Output: Markdown formatted release notes

## Usage Examples

```
/gemini:release v1.0.0
/gemini:release v2.3.1
/gemini:release
```

## Output Format

The generated release notes will include:

- **Summary**: Brief overview of the release
- **Features**: New functionality added
- **Bug Fixes**: Issues resolved
- **Improvements**: Enhancements to existing features
- **Breaking Changes**: Changes that may affect existing users

## Notes

- Provide a git tag as the starting point for the release notes
- If no tag is specified, uses the most recent tag or last 20 commits
- This command requires a git repository with commit history
- For code review, use `/gemini:review`
- For commit messages, use `/gemini:commit`
