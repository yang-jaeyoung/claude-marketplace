# Context-Aware Workflow (CAW)

Context-aware workflow orchestration plugin for Claude Code. Acts as a **Context-Aware Project Manager** that enforces structured workflows while collaborating interactively with developers.

## Philosophy

- **Hybrid Automation**: Combines natural language interface with rigorous programmatic logic
- **Human-in-the-Loop**: Propose → Review → Execute pattern
- **Context Engineering**: Active/Project/Archived tiered context management
- **Plan Mode Integration**: Seamlessly imports existing Claude Code plans

## Features

### v1.7.0 (Current)

- **`/cw:loop`** - Autonomous execution loop with 5-level error recovery
- **Gemini CLI Review Integration** - Edit and commit review via Gemini CLI hooks
- Full workflow automation with `/cw:auto`
- Tidy First methodology with `/cw:tidy` command
- Git Worktree parallel execution
- Ralph Loop continuous improvement
- Serena MCP memory synchronization

## Installation

```bash
# Option 1: Use directly
claude --plugin-dir /path/to/context-aware-workflow

# Option 2: Copy to project
cp -r context-aware-workflow /your/project/.claude-plugin/
```

## Quick Start

```bash
# Initialize and start a new workflow
/cw:start "Implement user authentication with JWT"

# Or run autonomously until completion
/cw:loop "Implement user authentication with JWT"

# Or run full workflow automatically
/cw:auto "Add a logout button to the header"
```

## Commands Reference

| Command | Description |
|---------|-------------|
| `/cw:auto` | **Run full workflow automatically** - init → start → next → review → fix → check → reflect |
| `/cw:loop` | **Autonomous execution loop** - repeat until completion with 5-level error recovery (NEW) |
| `/cw:init` | Initialize CAW environment (creates `.caw/` directory) |
| `/cw:start` | Start a new workflow with task description or import Plan Mode plans |
| `/cw:status` | Display current workflow status with visual progress bar |
| `/cw:next` | Execute the next pending step from task plan (supports auto-parallel execution) |
| `/cw:review` | Run code review with configurable depth (--haiku/--sonnet/--opus) |
| `/cw:fix` | Apply fixes from review results (auto-fix or manual) |
| `/cw:tidy` | Analyze and apply structural improvements (Tidy First methodology) |
| `/cw:check` | Validate compliance with project rules and conventions |
| `/cw:context` | Manage context files (add, remove, pack, view) |
| `/cw:brainstorm` | Interactive requirements discovery through Socratic dialogue |
| `/cw:design` | Create UX/UI or architecture design documents |
| `/cw:reflect` | Run Ralph Loop - continuous improvement cycle |
| `/cw:sync` | Synchronize CAW state with Serena memory (cross-session persistence) |
| `/cw:worktree` | Manage Git worktrees for parallel phase execution |
| `/cw:merge` | Merge completed worktree branches back to main |

## Workflow Loop

1. **Bootstrap**: Bootstrapper initializes `.caw/` environment (auto on first run)
2. **Discovery**: Planner Agent asks clarifying questions
3. **Planning**: Generates `task_plan.md` in `.caw/`
4. **Execution**: Code with plan-aware hooks (warnings if no plan exists)
5. **Review**: Manual review of implementation
6. **Reflection**: Ralph Loop for continuous improvement

## Autonomous Loop (`/cw:loop`)

For focused tasks, run until completion with automatic error recovery:

```bash
/cw:loop "Implement JWT authentication"
```

### Exit Conditions

| Condition | Status | Description |
|-----------|--------|-------------|
| Completion Promise | `completed` | Output contains completion keyword |
| All Steps Complete | `completed` | All task_plan.md steps are ✅ |
| Max Iterations | `max_iterations_reached` | Reached --max-iterations limit |
| Consecutive Failures | `failed` | 3+ consecutive failures |

### 5-Level Error Recovery

```
Level 1: Retry      → Re-attempt the same step
Level 2: Fixer      → Invoke Fixer-Haiku for auto-fix
Level 3: Alternative → Planner-Haiku suggests alternative
Level 4: Skip       → Skip non-blocking step
Level 5: Abort      → Save state and exit
```

### Options

```bash
/cw:loop "task" --max-iterations 30    # Custom iteration limit
/cw:loop "task" --no-auto-fix          # Disable auto-fix
/cw:loop "task" --verbose              # Detailed progress output
/cw:loop --continue                    # Resume interrupted loop
```

## Auto Mode (`/cw:auto`)

For end-to-end feature development:

```bash
/cw:auto "Add a logout button to the header"
```

### Workflow Stages

```
[1/7] init     → Initialize .caw/ if needed
[2/7] start    → Generate task plan (minimal questions)
[3/7] next     → Execute all steps
[4/7] review   → Code review
[5/7] fix      → Auto-fix issues
[6/7] check    → Compliance validation
[7/7] reflect  → Ralph Loop learning
```

## /cw:loop vs /cw:auto

| Feature | /cw:loop | /cw:auto |
|---------|----------|----------|
| Focus | Iteration until done | Full workflow stages |
| Exit condition | Flexible (promise/steps/max) | Stage completion |
| Error recovery | 5-level progressive | Stop and report |
| Review/Fix | Optional (via recovery) | Built-in stages |
| Best for | Single focused task | Complete feature |

## Generated Artifacts

| File | Purpose |
|------|---------|
| `.caw/task_plan.md` | Current task plan |
| `.caw/context_manifest.json` | Active/Packed/Ignored file tracking |
| `.caw/mode.json` | Active mode state (DEEP_WORK, NORMAL, etc.) |
| `.caw/session.json` | Current session state |
| `.caw/loop_state.json` | Autonomous loop state (NEW) |
| `.caw/learnings.md` | Accumulated improvement insights from Ralph Loop |
| `.caw/archives/` | Completed/abandoned plans |

## Model Routing System

CAW automatically selects the optimal model tier based on task complexity:

| Complexity | Tier | Use Case |
|------------|------|----------|
| ≤ 0.3 | Haiku | Fast, simple tasks, boilerplate |
| 0.3 - 0.7 | Sonnet | Standard development, TDD |
| > 0.7 | Opus | Architecture, security audits |

### User Overrides

```bash
/cw:review --haiku     # Quick review
/cw:review --sonnet    # Standard review
/cw:review --security  # Auto-selects Opus
```

## Hooks

### PreToolUse Hooks

**Edit/Write tools**:
1. Plan Adherence Check - Verify plan compliance
2. Gemini Edit Review - Review edits via Gemini CLI (NEW)

**Bash tool (git commit)**:
1. Tidy First Commit Validation - Block mixed structural/behavioral changes
2. Gemini Commit Review - Review commit via Gemini CLI (NEW)

## Ralph Loop - Continuous Improvement

### The RALPH Cycle

| Phase | Action | Output |
|-------|--------|--------|
| **R**eflect | Review what happened during the task | Task summary, outcome assessment |
| **A**nalyze | Identify patterns and root causes | What worked, what didn't, patterns |
| **L**earn | Extract actionable lessons | Key insights, skills improved, gaps |
| **P**lan | Create improvement actions | Prioritized action items |
| **H**abituate | Apply to future work | Updated defaults, checklists, memories |

### Usage

```bash
/cw:reflect              # Reflect on last completed task
/cw:reflect --task 2.3   # Reflect on specific step
/cw:reflect --full       # Full workflow retrospective
```

## Magic Keywords

Activate special modes by including keywords in your prompt:

| Keyword | Mode | Behavior |
|---------|------|----------|
| `deepwork`, `fullwork`, `ultrawork` | DEEP WORK | Complete ALL tasks without stopping |
| `thinkhard`, `ultrathink` | DEEP ANALYSIS | Extended reasoning, validate before acting |
| `quickfix`, `quick`, `fast` | MINIMAL CHANGE | Essential changes only, speed priority |
| `research`, `investigate` | RESEARCH | Comprehensive information gathering first |

## Tidy First Methodology

Kent Beck's **Tidy First** methodology for code quality:

> "Never mix structural changes with behavioral changes in the same commit.
> When both are needed, always do structural changes first."

### Step Types

| Icon | Type | Description | Commit Prefix |
|------|------|-------------|---------------|
| 🧹 | Tidy | Structural change (no behavior change) | `[tidy]` |
| 🔨 | Build | Behavioral change (new feature, bug fix) | `[feat]`, `[fix]` |

### Usage

```bash
/cw:tidy                  # Analyze current step target
/cw:tidy --scope src/     # Analyze specific directory
/cw:tidy --apply          # Apply changes
/cw:tidy --add-step       # Add Tidy step to plan
```

## Schema Reference

| Schema | Location | Purpose |
|--------|----------|---------|
| `mode.schema.json` | `schemas/` | Mode state tracking |
| `model-routing.schema.json` | `schemas/` | Model tier selection |
| `last_review.schema.json` | `schemas/` | Reviewer output format |
| `ralph-loop.schema.json` | `_shared/schemas/` | Continuous improvement cycle |
| `task-plan.schema.md` | `_shared/schemas/` | Task plan document format |

## Roadmap

### Completed (v1.7.0)
- [x] `/cw:loop` - Autonomous execution loop with 5-level error recovery
- [x] Gemini CLI integration for edit and commit review hooks
- [x] Loop state persistence and resumability

### Completed (v1.6.0)
- [x] Tidy First methodology with `/cw:tidy` command
- [x] `/cw:sync` for Serena MCP memory synchronization
- [x] `/cw:worktree` and `/cw:merge` for Git worktree parallel execution
- [x] PreToolUse hook for automatic Tidy First commit validation

### Completed (v1.5.0)
- [x] Ralph Loop continuous improvement cycle
- [x] `/cw:reflect` skill for post-task improvement analysis
- [x] Learnings persistence (`.caw/learnings.md`, Serena memories)

### Completed (v1.4.0)
- [x] Model Routing System with complexity-based tier selection
- [x] Tiered Agent variants (Haiku, Sonnet, Opus)
- [x] `/cw:auto` command for full workflow automation

### Planned
- [ ] VS Code extension integration
- [ ] GitHub Actions integration
- [ ] Multi-project support

## License

MIT
