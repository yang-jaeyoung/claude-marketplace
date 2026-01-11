# Module Context

**Module:** Context Aware Workflow
**Role:** Advanced agentic capabilities, skills, and hooks for Claude Code.
**Tech Stack:** Python 3.x, Pytest.

# Operational Commands

## Testing
-   `python -m pytest tests/` — Run all unit and integration tests.
-   `python tests/test_plugin_structure.py` — Validate plugin file structure compliance.

# Implementation Patterns

## Agent Definitions
-   files: `agents/*.md`
-   frontmatter: `name`, `model` (sonnet/opus), `tools` list.
-   body: clear system prompt.

## Skill Definitions
-   files: `skills/*/SKILL.md`
-   frontmatter: `name`, `description`, `allowed-tools`.
-   Use `forked-context: true` for skills that need isolation.

# Local Golden Rules

## Do's
-   **DO** add a test case in `tests/` for every new agent or skill logic.
-   **DO** ensure YAML frontmatter is valid; use a linter if possible.
-   **DO** clear context variables when a workflow finishes to avoid pollution.

## Don'ts
-   **DON'T** rely on global state across different agent executions.
-   **DON'T** use complex logic inside Markdown files; delegate to Python scripts if logic is heavy.
