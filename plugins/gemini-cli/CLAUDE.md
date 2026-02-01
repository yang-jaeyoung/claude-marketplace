# Module Context

**Module:** Gemini CLI
**Version:** 1.0.0
**Role:** Google Gemini CLI integration for code review, commits, and documentation.
**Tech Stack:** Markdown commands, Gemini CLI (external dependency).

## Prerequisites

- Gemini CLI installed (`brew install google-gemini/tap/gemini-cli`)
- Authenticated via `gemini auth login`

---

# Operational Commands

```bash
# External CLI setup
brew install google-gemini/tap/gemini-cli
gemini auth login
gemini --version

# Plugin commands (in Claude Code)
/gemini:ask <question>       # Ask Gemini a question
/gemini:review [file]        # Code review (staged changes or file)
/gemini:commit               # Generate commit message
/gemini:docs <file>          # Generate documentation
/gemini:release [tag]        # Generate release notes
/gemini:search <query>       # Web search with Search Grounding
```

---

# Command Inventory

## /gemini:ask
Ask Gemini any question using headless mode.
- **Input:** Free-form question
- **Output:** Gemini response

## /gemini:review
Code review on staged changes or specific file.
- **Input:** Optional file path (defaults to staged changes)
- **Focus:** Bugs, security vulnerabilities, code quality

## /gemini:commit
Generate conventional commit message from staged changes.
- **Prerequisite:** `git add` staged changes first
- **Output:** Conventional commit format (feat/fix/docs/etc.)

## /gemini:docs
Generate comprehensive documentation for a file.
- **Input:** File path
- **Output:** Overview, function descriptions, parameters, examples

## /gemini:release
Generate release notes from git commit history.
- **Input:** Optional start tag (auto-detects if omitted)
- **Output:** Summary, features, bug fixes, improvements, breaking changes

## /gemini:search
Web search using Google Search Grounding.
- **Input:** Search query
- **Output:** Search results summary, key information, source URLs
- **Limit:** 1,500 queries/day (free tier)

---

# Implementation Patterns

## Directory Structure

```
gemini-cli/
  .claude-plugin/plugin.json
  README.md
  commands/
    ask.md           # /gemini:ask
    review.md        # /gemini:review
    commit.md        # /gemini:commit
    docs.md          # /gemini:docs
    release.md       # /gemini:release
    search.md        # /gemini:search
```

## Command Definition Pattern

```yaml
---
description: Command description
argument-hint: "<arg>"
---
# Command instructions using Gemini CLI
```

## Gemini CLI Usage

All commands invoke external `gemini` CLI with the `-p` (prompt) flag for non-interactive execution:

```bash
# Direct question
gemini -p "question"

# Code review with context
git diff --staged | gemini -p "Review this code..."

# Commit message generation
git diff --staged | gemini -p "Generate commit message..."
```

---

# Local Golden Rules

## Do's

- **DO** verify Gemini CLI is installed before running commands.
- **DO** ensure `git add` is run before `/gemini:commit`.
- **DO** use `-p` flag for non-interactive prompt execution.
- **DO** handle Gemini CLI errors gracefully with troubleshooting hints.

## Don'ts

- **DON'T** assume Gemini CLI is available without checking.
- **DON'T** run `/gemini:commit` without staged changes.
- **DON'T** expose API keys or tokens in command output.
- **DON'T** use interactive Gemini CLI modes (always use `-p` flag).
