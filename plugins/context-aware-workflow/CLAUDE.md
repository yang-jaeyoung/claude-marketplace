# Module Context

**Module:** Context-Aware Workflow (cw)
**Version:** 2.0.0
**Role:** Advanced agentic workflow orchestration with intelligent model routing.
**Tech Stack:** Python 3.x, Pytest, Markdown/YAML.

## Core Capabilities

- Plan Mode integration with automatic task plan generation
- Tiered agent variants (Haiku/Sonnet/Opus) with complexity-based routing
- Ralph Loop continuous improvement cycles
- QA loops (qaloop/ultraqa) for automated quality assurance
- Parallel execution via git worktrees
- HUD (Heads-Up Display) for real-time workflow metrics
- Eco mode for cost-optimized execution (30-50% savings)
- Background task heuristics for automatic async decisions
- Analytics system for token/cost analysis
- Delegation categories for improved agent routing
- Rate limit handling with automatic resume
- Swarm mode for parallel multi-agent execution
- Pipeline mode for explicit sequential stages

---

# Operational Commands

```bash
# Run all tests
python -m pytest tests/

# Validate plugin structure
python tests/test_plugin_structure.py

# Workflow commands (in Claude Code)
# Core workflow
/cw:start      # Initialize workflow
/cw:status     # Check progress
/cw:next       # Execute next step
/cw:init       # Project initialization

# Execution modes
/cw:auto       # Autonomous workflow execution
/cw:loop       # Continuous iteration loop
/cw:swarm      # Parallel agent execution
/cw:pipeline   # Sequential stage execution

# Quality assurance
/cw:review     # Run code review
/cw:qaloop     # Review-Fix cycles
/cw:ultraqa    # Auto QA with diagnosis
/cw:check      # Run compliance checks
/cw:fix        # Apply fixes

# Planning & design
/cw:brainstorm # Ideation session
/cw:design     # UI/UX design workflow
/cw:research   # Research task

# Improvement & analysis
/cw:reflect    # Run Ralph Loop
/cw:evolve     # Self-improvement cycle
/cw:analytics  # Token/cost analysis

# Context & collaboration
/cw:context    # Manage context variables
/cw:sync       # Sync with external tools
/cw:merge      # Merge worktree results
/cw:worktree   # Git worktree management
/cw:tidy       # Cleanup resources

# Magic keywords
# eco/ecomode   - Cost-optimized execution
# deepwork      - Complete all tasks mode
# quickfix      - Minimal changes only
# async         - Force background execution
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

- **Analyst** (`analyst.md`, Sonnet): Requirements extraction, task specification for auto workflow
- **Bootstrapper** (`bootstrapper.md`, Haiku): Environment initialization, project detection
- **Architect** (`architect.md`, Opus): System design, component architecture
- **Designer** (`designer.md`, Sonnet): UX/UI design, wireframes, user flows
- **Ideator** (`ideator.md`, Sonnet): Requirements discovery, Socratic dialogue
- **ComplianceChecker** (`compliance-checker.md`, Sonnet): Guideline validation

---

# Skills Inventory

## Workflow Management
- **context-manager**: Workflow context variable management
- **progress-tracker**: Task progress tracking and reporting
- **session-persister**: Session state persistence across restarts
- **plan-detector**: Automatic plan detection from user input

## Quality & Review
- **quality-gate**: Quality checkpoint validation
- **review-assistant**: Code review assistance and feedback
- **commit-discipline**: Commit message and discipline enforcement
- **quick-fix**: Rapid fix suggestions

## Learning & Insights
- **insight-collector**: Collect insights from workflow execution
- **pattern-learner**: Learn patterns from codebase
- **knowledge-base**: Store and retrieve project knowledge
- **decision-logger**: Log architectural decisions

## Analysis & Monitoring
- **hud**: Real-time workflow metrics (HUD)
- **dashboard**: Workflow dashboard display
- **dependency-analyzer**: Dependency analysis

## Utilities
- **context-helper**: Context management helpers
- **reflect**: Self-reflection and improvement
- **evolve**: Self-evolution capabilities
- **research**: Research task execution
- **serena-sync**: Serena MCP synchronization

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

---

# Key Features

## HUD (Heads-Up Display)
Real-time workflow metrics during execution.
- Enable: `CAW_HUD=enabled`
- Location: `skills/hud/SKILL.md`

## Eco Mode
Cost-optimized execution (30-50% savings).
- Activation: Use `eco` or `ecomode` keyword
- Effects: Forces Haiku, skips optional phases

## Background Heuristics
Automatic async/foreground decision based on task patterns.
- Location: `_shared/background-heuristics.md`
- Patterns: lint, format, gemini → async; security, critical → foreground

## Analytics
Token/cost analysis and optimization insights.
- Command: `/cw:analytics`
- Schema: `schemas/metrics.schema.json`

## Swarm Mode
Parallel multi-agent execution.
- Command: `/cw:swarm "task1" "task2"`
- Location: `commands/swarm.md`

## Pipeline Mode
Explicit sequential stages with checkpoints.
- Command: `/cw:pipeline --stages "plan,build,review"`
- Location: `commands/pipeline.md`

## Delegation Categories
Category-based agent routing (research, implementation, review, design, maintenance).
- Location: `_shared/agent-resolver.md`

## Rate Limit Handling
Automatic wait-and-resume for rate limit errors.
- Location: `hooks/scripts/rate_limit_handler.py`

---

# Context Map

- **[Agents](./agents/)** — 18 agents (4 tiered × 3 tiers + 6 specialized).
- **[Commands](./commands/)** — 24 slash commands for workflow control.
- **[Skills](./skills/)** — 20 composable skills for workflow capabilities.
- **[Hooks](./hooks/)** — Lifecycle hooks (SessionStart, Stop, PreToolUse, PostToolUse, SessionEnd).
- **[Schemas](./schemas/)** — JSON schemas (metrics, mode, model-routing, last_review).
- **[Shared Resources](./_shared/)** — Model routing, agent registry, templates, skill composition, background heuristics.
- **[Tests](./tests/)** — Plugin structure validation, unit tests.
