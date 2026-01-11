# Module Context

**Module:** Codex CLI
**Role:** Simple command-line interface extensions defined purely in Markdown.
**Tech Stack:** Markdown, YAML Frontmatter.

# Operational Commands

-   No build step required.
-   Verify by reloading Claude Code plugins: `claude plugins reload` (if available) or restart.

# Implementation Patterns

## Command Definition
-   File: `commands/<command-name>.md`
-   Frontmatter:
    ```yaml
    ---
    description: "Short summary"
    argument-hint: "<optional-arg>"
    ---
    ```

# Local Golden Rules

## Do's
-   **DO** keep descriptions concise (they appear in help menus).
-   **DO** provide usage examples in the markdown body.

## Don'ts
-   **DON'T** include executable code blocks that require external dependencies not present in the base environment.
-   **DON'T** create complex multi-step logic here; use a full Agent plugin for that.
