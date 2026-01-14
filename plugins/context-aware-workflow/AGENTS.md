# Module Context

**Module:** Context Aware Workflow
**Role:** Advanced agentic capabilities, skills, and hooks for Claude Code.
**Tech Stack:** Python 3.x, Pytest.

# Agent Inventory

## Core Agents with Tiered Variants

### Planner
Plans and structures tasks into executable steps.

| Tier | File | Use Case | Complexity |
|------|------|----------|------------|
| Haiku | `planner-haiku.md` | Simple tasks, single-file, quick fixes | ≤ 0.3 |
| Sonnet | `planner.md` | Standard development, multi-step features | 0.3 - 0.7 |
| Opus | `planner-opus.md` | Architecture design, security-critical planning | > 0.7 |

### Builder
Implements code following TDD approach.

| Tier | File | Use Case | Complexity |
|------|------|----------|------------|
| Haiku | `builder-haiku.md` | Boilerplate, simple CRUD, formatting | ≤ 0.3 |
| Sonnet | `builder-sonnet.md` | Standard implementation, pattern-following | 0.3 - 0.7 |
| Opus | `builder.md` | Complex algorithms, security-critical code | > 0.7 |

### Reviewer
Reviews code for quality, bugs, and best practices.

| Tier | File | Use Case | Complexity |
|------|------|----------|------------|
| Haiku | `reviewer-haiku.md` | Quick style checks, linting issues | ≤ 0.3 |
| Sonnet | `reviewer.md` | Standard code review, quality gates | 0.3 - 0.7 |
| Opus | `reviewer-opus.md` | Security audits, architecture review, OWASP | > 0.7 |

### Fixer
Applies fixes based on review feedback.

| Tier | File | Use Case | Complexity |
|------|------|----------|------------|
| Haiku | `fixer-haiku.md` | Auto-fix: lint, imports, formatting | ≤ 0.3 |
| Sonnet | `fixer-sonnet.md` | Multi-file refactoring, pattern extraction | 0.3 - 0.7 |
| Opus | `fixer.md` | Security fixes, architectural refactoring | > 0.7 |

## Specialized Agents (Single Tier)

| Agent | File | Model | Purpose |
|-------|------|-------|---------|
| Bootstrapper | `bootstrapper.md` | Haiku | Environment initialization, project detection |
| Architect | `architect.md` | Opus | System design, component architecture |
| Designer | `designer.md` | Sonnet | UX/UI design, wireframes, user flows |
| Ideator | `ideator.md` | Sonnet | Requirements discovery, Socratic dialogue |
| ComplianceChecker | `compliance-checker.md` | Sonnet | Guideline validation, convention checking |

# Operational Commands

## Testing
-   `python -m pytest tests/` — Run all unit and integration tests.
-   `python tests/test_plugin_structure.py` — Validate plugin file structure compliance.

# Implementation Patterns

## Agent Definitions
-   files: `agents/*.md`
-   frontmatter: `name`, `model` (haiku/sonnet/opus), `tier`, `tools` list.
-   body: clear system prompt with tier-specific behavior.

## Tiered Agent Naming Convention
-   Base tier (Sonnet): `<agent>.md` (e.g., `planner.md`, `reviewer.md`)
-   Lower tier (Haiku): `<agent>-haiku.md`
-   Higher tier (Opus): `<agent>-opus.md`
-   Exception: Builder uses Opus as base (`builder.md`)

## Skill Definitions
-   files: `skills/*/SKILL.md`
-   frontmatter: `name`, `description`, `allowed-tools`.
-   Use `forked-context: true` for skills that need isolation.

# Local Golden Rules

## Do's
-   **DO** add a test case in `tests/` for every new agent or skill logic.
-   **DO** ensure YAML frontmatter is valid; use a linter if possible.
-   **DO** clear context variables when a workflow finishes to avoid pollution.
-   **DO** create tier variants when agents need different complexity handling.

## Don'ts
-   **DON'T** rely on global state across different agent executions.
-   **DON'T** use complex logic inside Markdown files; delegate to Python scripts if logic is heavy.
-   **DON'T** hardcode model selection; use the Model Routing System.
