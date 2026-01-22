# Module Context

**Module:** Context-Aware Workflow (cw)
**Version:** 1.8.0
**Role:** Advanced agentic workflow orchestration with intelligent model routing.
**Tech Stack:** Python 3.x, Pytest, Markdown/YAML.

## Core Capabilities

- Plan Mode integration with automatic task plan generation
- Tiered agent variants (Haiku/Sonnet/Opus) with complexity-based routing
- Ralph Loop continuous improvement cycles
- QA loops (qaloop/ultraqa) for automated quality assurance
- OMC (oh-my-claudecode) integration with graceful degradation
- Parallel execution via git worktrees

---

# Operational Commands

```bash
# Run all tests
python -m pytest tests/

# Validate plugin structure
python tests/test_plugin_structure.py

# Workflow commands (in Claude Code)
/cw:start      # Initialize workflow
/cw:status     # Check progress
/cw:next       # Execute next step
/cw:review     # Run code review
/cw:reflect    # Run Ralph Loop
/cw:qaloop     # Review-Fix cycles
/cw:ultraqa    # Auto QA with diagnosis
```

---

# Agent Inventory

## Tiered Agents (Complexity-Based Routing)

### Planner
Plans and structures tasks into executable steps.
- **Haiku** (`planner-haiku.md`): Simple tasks, single-file, quick fixes (complexity <= 0.3)
- **Sonnet** (`planner.md`): Standard development, multi-step features (0.3-0.7)
- **Opus** (`planner-opus.md`): Architecture design, security-critical planning (> 0.7)

### Builder
Implements code following TDD approach.
- **Haiku** (`builder-haiku.md`): Boilerplate, simple CRUD, formatting (complexity <= 0.3)
- **Sonnet** (`builder-sonnet.md`): Standard implementation, pattern-following (0.3-0.7)
- **Opus** (`builder.md`): Complex algorithms, security-critical code (> 0.7)

### Reviewer
Reviews code for quality, bugs, and best practices.
- **Haiku** (`reviewer-haiku.md`): Quick style checks, linting issues (complexity <= 0.3)
- **Sonnet** (`reviewer.md`): Standard code review, quality gates (0.3-0.7)
- **Opus** (`reviewer-opus.md`): Security audits, architecture review, OWASP (> 0.7)

### Fixer
Applies fixes based on review feedback.
- **Haiku** (`fixer-haiku.md`): Auto-fix lint, imports, formatting (complexity <= 0.3)
- **Sonnet** (`fixer-sonnet.md`): Multi-file refactoring, pattern extraction (0.3-0.7)
- **Opus** (`fixer.md`): Security fixes, architectural refactoring (> 0.7)

## Specialized Agents (Single Tier)

- **Bootstrapper** (`bootstrapper.md`, Haiku): Environment initialization, project detection
- **Architect** (`architect.md`, Opus): System design, component architecture
- **Designer** (`designer.md`, Sonnet): UX/UI design, wireframes, user flows
- **Ideator** (`ideator.md`, Sonnet): Requirements discovery, Socratic dialogue
- **ComplianceChecker** (`compliance-checker.md`, Sonnet): Guideline validation

---

# OMC Integration

When oh-my-claudecode plugin is available, additional specialized agents become accessible.

## Agent Mapping (OMC -> CAW Fallback)

- `omc:architect` -> `cw:architect`
- `omc:researcher` -> `cw:Planner` + WebSearch
- `omc:scientist` -> `cw:Builder` + Bash
- `omc:explore` -> Task(Explore)
- `omc:executor` -> `cw:Builder`
- `omc:qa-tester` -> `cw:Reviewer` + Bash
- `omc:critic` -> `cw:reviewer-opus`
- `omc:build-fixer` -> `cw:Fixer`
- `omc:security-reviewer` -> `cw:reviewer-opus`
- `omc:code-reviewer` -> `cw:reviewer-opus`

## Graceful Degradation

CAW functions fully without OMC. When OMC agents are unavailable:
1. Agent Resolver checks OMC availability
2. Falls back to equivalent CAW agent
3. Displays warning about reduced capability
4. Continues operation with fallback

See `_shared/agent-resolver.md` for implementation details.

---

# Implementation Patterns

## Agent Definition (agents/*.md)

```yaml
---
name: "AgentName"
description: "What the agent does"
model: sonnet           # haiku, sonnet, or opus
tier: sonnet            # Optional: complexity tier indicator
whenToUse: |
  Usage guidance with examples
tools:
  - Read
  - Write
  - Glob
mcp_servers:
  - serena
---
# Agent system prompt here
```

## Tiered Agent Naming Convention

- Base tier (Sonnet): `<agent>.md` (e.g., `planner.md`, `reviewer.md`)
- Lower tier (Haiku): `<agent>-haiku.md`
- Higher tier (Opus): `<agent>-opus.md`
- Exception: Builder uses Opus as base (`builder.md`)

## Skill Definition (skills/*/SKILL.md)

```yaml
---
name: skill-name
description: What the skill does
allowed-tools: Read, Glob, Grep
context: fork           # Runs in isolated context
---
# Skill behavior instructions
```

---

# Local Golden Rules

## Do's

- **DO** add tests in `tests/` for every new agent or skill.
- **DO** ensure YAML frontmatter is valid before committing.
- **DO** clear context variables when workflows finish.
- **DO** create tier variants when agents need different complexity handling.
- **DO** use Model Routing System for automatic tier selection.

## Don'ts

- **DON'T** rely on global state across agent executions.
- **DON'T** use complex logic in Markdown; delegate to Python scripts.
- **DON'T** hardcode model selection; use the routing system.
- **DON'T** skip graceful degradation when integrating external agents.

---

# Context Map

- **[Shared Resources](./_shared/)** — Model routing, agent resolver, templates.
- **[Documentation](./docs/)** — Architecture, workflows, integration guides.
- **[Tests](./tests/)** — Plugin structure validation, unit tests.
