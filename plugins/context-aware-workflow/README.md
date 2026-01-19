# Context-Aware Workflow (CAW)

Context-aware workflow orchestration plugin for Claude Code. Acts as a **Context-Aware Project Manager** that enforces structured workflows while collaborating interactively with developers.

## Philosophy

- **Hybrid Automation**: Combines natural language interface with rigorous programmatic logic
- **Human-in-the-Loop**: Propose → Review → Execute pattern
- **Context Engineering**: Active/Project/Archived tiered context management
- **Plan Mode Integration**: Seamlessly imports existing Claude Code plans

## Features

### MVP (v0.1.0)

- `/cw:init` - Initialize CAW environment (standalone setup)
- `/cw:start` - Initialize workflow with task description or import Plan Mode plans
- **Bootstrapper Agent** - Environment initialization and project detection
- **Planner Agent** - Analyzes requirements and generates structured `task_plan.md`
- **ContextManager Skill** - Intelligent context file management (pack, prune, search)
- **Workflow Hooks** - Plan detection and coding-without-plan warnings

## Installation

```bash
# Option 1: Use directly
claude --plugin-dir /path/to/context-aware-workflow

# Option 2: Copy to project
cp -r context-aware-workflow /your/project/.claude-plugin/
```

## Usage

### Initialize Environment (Optional)

```bash
# Initialize CAW environment only
/cw:init

# Reset and reinitialize
/cw:init --reset
```

### Start a New Workflow

```bash
# With task description (auto-initializes if needed)
/cw:start "Implement user authentication with JWT"

# Import from Plan Mode
/cw:start --from-plan

# Specify plan file
/cw:start --plan-file .claude/plan.md
```

### Workflow Loop

1. **Bootstrap**: Bootstrapper initializes `.caw/` environment (auto on first run)
2. **Discovery**: Planner Agent asks clarifying questions
3. **Planning**: Generates `task_plan.md` in `.caw/`
4. **Execution**: Code with plan-aware hooks (warnings if no plan exists)
5. **Review**: Manual review of implementation

## Generated Artifacts

| File | Purpose |
|------|---------|
| `.caw/task_plan.md` | Current task plan |
| `.caw/context_manifest.json` | Active/Packed/Ignored file tracking |
| `.caw/mode.json` | Active mode state (DEEP_WORK, NORMAL, etc.) |
| `.caw/session.json` | Current session state |
| `.caw/learnings.md` | Accumulated improvement insights from Ralph Loop |
| `.caw/archives/` | Completed/abandoned plans |

## Configuration

Create `.claude/caw.local.md` for project-specific settings (optional):

```markdown
# CAW Local Settings

## Context Preferences
- Max active files: 10
- Auto-prune after: 5 turns

## Plan Preferences
- Default plan location: .claude/plan.md
- Auto-detect plans: true
```

## Magic Keywords

Activate special modes by including keywords in your prompt:

| Keyword | Mode | Behavior |
|---------|------|----------|
| `deepwork`, `fullwork`, `ultrawork` | DEEP WORK | Complete ALL tasks without stopping |
| `thinkhard`, `ultrathink` | DEEP ANALYSIS | Extended reasoning, validate before acting |
| `quickfix`, `quick`, `fast` | MINIMAL CHANGE | Essential changes only, speed priority |
| `research`, `investigate` | RESEARCH | Comprehensive information gathering first |

**Example:**
```bash
# Start a task that won't stop until fully complete
"deepwork implement the user authentication system"

# Quick fixes only
"quickfix the failing tests"
```

## Work Mode Tracking

CAW tracks workflow mode to adapt agent behavior:

- **Mode State**: Agents check `.caw/mode.json` to adjust their approach
- **DEEP_WORK mode**: Agents prioritize thoroughness over speed
- **MINIMAL_CHANGE mode**: Agents focus on quick, targeted fixes

Use `/cw:status` to see current mode and task progress.

## Ralph Loop - Continuous Improvement

CAW includes a continuous improvement cycle inspired by systematic learning practices:

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
# Reflect on last completed task
/cw:reflect

# Reflect on specific step
/cw:reflect --task 2.3

# Full workflow retrospective
/cw:reflect --full
```

### Output Example

```markdown
## 🔄 Ralph Loop - Improvement Cycle

**Task**: Implement JWT Authentication
**Outcome**: ✅ Success | **Duration**: ⏱️ Expected

### 💡 LEARN
**Key Insights**:
1. TDD approach reduced debugging time by 50%
2. Security review should happen earlier

### 📋 PLAN
| Priority | Action | Applies To |
|----------|--------|------------|
| 🔴 High | Add security review to Phase 1 | All auth tasks |

### 🔧 HABITUATE
- ✅ Added to .caw/learnings.md
- ✅ Created memory: ralph_learning_2024-01-15
```

### Integration Points

- **Serena Memory**: Stores learnings for future sessions
- **Learnings File**: `.caw/learnings.md` accumulates insights
- **Status Command**: `/cw:status` suggests reflection when appropriate

## Auto Mode - Full Workflow Automation

For simple, well-defined tasks, run the entire workflow with a single command:

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

### Options

```bash
/cw:auto "task" --skip-review    # Skip stages 4-6
/cw:auto "task" --skip-reflect   # Skip stage 7
/cw:auto "task" --verbose        # Detailed progress output
```

### Error Handling

- **On error**: Workflow pauses, state saved to `.caw/session.json`
- **Resume**: Use `/cw:next` to continue from where it stopped
- **Critical issues**: Workflow pauses for manual intervention

### When to Use Auto Mode

| Use Auto Mode | Use Manual Workflow |
|---------------|---------------------|
| Simple, well-defined tasks | Complex multi-module changes |
| "Add X", "Fix Y" tasks | Architecture decisions |
| Prototyping | Production-critical code |
| Learning the workflow | Full control needed |

## Model Routing System

CAW automatically selects the optimal model tier based on task complexity:

### Complexity Scoring (0.0 - 1.0)

| Indicator | Low | Medium | High |
|-----------|-----|--------|------|
| File Count | 1-3 (+0.0) | 4-10 (+0.1) | 10+ (+0.2) |
| Scope Keywords | simple/quick (+0.0) | standard (+0.15) | architecture/security (+0.3) |
| Cross Module | 1 module (+0.0) | 2-3 modules (+0.12) | 4+ modules (+0.25) |
| Dependencies | None (+0.0) | Has deps (+0.15) | - |

### Model Tier Selection

| Complexity | Tier | Use Case |
|------------|------|----------|
| ≤ 0.3 | Haiku | Fast, simple tasks, boilerplate |
| 0.3 - 0.7 | Sonnet | Standard development, TDD |
| > 0.7 | Opus | Architecture, security audits |

### User Overrides

Force a specific model tier with flags:
```bash
/cw:review --haiku     # Quick review
/cw:review --sonnet    # Standard review
/cw:review --security  # Auto-selects Opus

/cw:fix --deep         # Sonnet-level fixes
/cw:fix --opus         # Force Opus for complex refactoring
```

### Agent-Specific Routing

| Agent | Default | Available Tiers | Upgrade Triggers |
|-------|---------|-----------------|------------------|
| Planner | Sonnet | Haiku, Sonnet, Opus | architecture, security, migration |
| Builder | Sonnet | Haiku, Sonnet, Opus | complex_algorithm, performance_critical |
| Reviewer | Sonnet | Haiku, Sonnet, Opus | --security, --audit, vulnerability |
| Fixer | Haiku | Haiku, Sonnet, Opus | --deep, multi-file changes |

### Tiered Agent Variants

Each agent has tier-specific implementations:

**Planner**:
- `planner-haiku.md` - Fast planning, max 5 steps, single-file focus
- `planner.md` (Sonnet) - Balanced planning with context analysis
- `planner-opus.md` - Deep architectural planning with risk assessment

**Builder**:
- `builder-haiku.md` - Quick implementation, minimal context
- `builder-sonnet.md` - TDD approach, pattern-following
- `builder.md` (Opus) - Full implementation with comprehensive verification

**Reviewer**:
- `reviewer-haiku.md` - Quick style checks, linting
- `reviewer.md` (Sonnet) - Standard code review with quality gates
- `reviewer-opus.md` - Security audits, architecture review, OWASP analysis

**Fixer**:
- `fixer-haiku.md` - Auto-fix: lint, imports, formatting
- `fixer-sonnet.md` - Multi-file refactoring, pattern extraction
- `fixer.md` (Opus) - Security fixes, architectural refactoring

## Commands Reference

| Command | Description |
|---------|-------------|
| `/cw:auto` | **Run full workflow automatically** - init → start → next → review → fix → check → reflect |
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

## Schema Reference

Schemas are located in `schemas/` and `_shared/schemas/`:

| Schema | Location | Purpose |
|--------|----------|---------|
| `mode.schema.json` | `schemas/` | Mode state tracking (DEEP_WORK, NORMAL, etc.) |
| `model-routing.schema.json` | `schemas/` | Model tier selection and complexity scoring |
| `last_review.schema.json` | `schemas/` | Reviewer output format for Fixer integration |
| `ralph-loop.schema.json` | `_shared/schemas/` | Continuous improvement cycle data structure |
| `task-plan.schema.md` | `_shared/schemas/` | Task plan document format specification |
| `review.schema.md` | `_shared/schemas/` | Review output format specification |
| `manifest.schema.md` | `_shared/schemas/` | Context manifest file format |

## Roadmap

### Completed (v1.6.0)
- [x] `/cw:auto` command for full workflow automation
- [x] Auto-mode behavior modifications for agents
- [x] Error handling with state persistence and resumability
- [x] Skip flags (--skip-review, --skip-reflect)
- [x] **Tidy First methodology** with `/cw:tidy` command and `commit-discipline` skill
- [x] `/cw:sync` for Serena MCP memory synchronization
- [x] `/cw:worktree` and `/cw:merge` for Git worktree parallel execution
- [x] PreToolUse hook for automatic Tidy First commit validation

### Completed (v1.5.0)
- [x] Ralph Loop continuous improvement cycle (RALPH: Reflect-Analyze-Learn-Plan-Habituate)
- [x] `/cw:reflect` skill for post-task improvement analysis
- [x] Learnings persistence (`.caw/learnings.md`, Serena memories)
- [x] Ralph Loop schema for structured improvement data

### Completed (v1.4.0)
- [x] Model Routing System with complexity-based tier selection
- [x] Tiered Agent variants (Haiku, Sonnet, Opus for each agent)
- [x] User override flags (--haiku, --sonnet, --opus, --security, --deep)
- [x] Intelligent upgrade triggers per agent type
- [x] Model routing schema and documentation

### Completed (v1.3.0)
- [x] Magic Keyword detection for workflow modes
- [x] Visual progress bar in `/cw:status`
- [x] Mode state persistence (`.caw/mode.json`)

### Completed (v1.2.1)
- [x] Quick Fix skill for auto-fixable issues
- [x] Reviewer JSON output (`last_review.json`)
- [x] JSON schema for Reviewer → Fixer data flow

### Completed (v1.2.0)
- [x] Fixer Agent for intelligent code fixes
- [x] `/cw:fix` - Review result auto/manual fixing

### Completed (v1.1.0)
- [x] Bootstrapper Agent for environment initialization
- [x] `/cw:init` - Environment setup command

### Completed (v1.0.0)
- [x] Builder Agent for TDD execution
- [x] Reviewer Agent for code quality review
- [x] `/cw:status` - Workflow state display
- [x] `/cw:review` - Plan/code review trigger
- [x] ComplianceChecker Agent for guideline compliance

### Planned
- [ ] VS Code extension integration
- [ ] GitHub Actions integration
- [ ] Multi-project support

## License

MIT
