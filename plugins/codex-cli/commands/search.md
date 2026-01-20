---
description: Execute query with web search capability
argument-hint: "<question>"
allowed-tools: ["Bash"]
---

# Codex Search

Execute a query with web search capability for up-to-date information.

## Instructions

1. Get the user's question from the arguments
2. Run Codex CLI with search enabled:

```bash
codex exec --search -m gpt-5.2 -s read-only --skip-git-repo-check "<question>"
```

3. Display the result to the user

## Options

- Model: `gpt-5.2` (general purpose)
- Sandbox: `read-only` (safe mode)
- Search: `--search` (enables web search)

## Usage Examples

```
/codex:search Latest React 19 features
/codex:search Current Python 3.12 release notes
/codex:search Recent changes in TypeScript 5.4
/codex:search What are the new features in Node.js 22?
```

## Notes

- Enables real-time web search for current information
- Useful for questions about recent updates, news, or documentation
- Results include citations from web sources
- For questions not requiring current info, use `/codex:ask` instead
