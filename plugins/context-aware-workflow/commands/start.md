---
description: Start a context-aware workflow session. Initializes environment if needed, analyzes task requirements, imports Plan Mode plans, and generates structured task_plan.md.
argument-hint: "<task> [--from-plan] [--plan-file <path>]"
---

# /cw:start - Workflow Initialization

Initialize a context-aware workflow session for structured task execution.

## Usage

```bash
/cw:start "Implement user authentication with JWT"
/cw:start --from-plan                    # Import from Plan Mode
/cw:start --plan-file docs/my-plan.md    # Specific plan file
```

## Pre-flight Check

```
Check: .caw/context_manifest.json exists?
├─ NO  → Invoke Bootstrapper via Task(subagent_type="cw:bootstrapper")
│        Wait for completion, verify manifest created
└─ YES → Proceed to planning
```

## Invocation Modes

| Mode | Trigger | Behavior |
|------|---------|----------|
| **New Task** | `"task description"` | Invoke Planner for interactive discovery |
| **From Plan Mode** | `--from-plan` | Detect and convert existing Plan Mode output |
| **Specific File** | `--plan-file <path>` | Read and convert specified plan file |

## Plan Mode Detection

1. Resolve plansDirectory from settings (local → project → global → default)
2. Check `{plansDirectory}/*.md` and `.claude/plan.md` (legacy)
3. If found: display summary, ask to confirm import

## Interactive Discovery (New Task)

1. **Initial Analysis**: Parse task, identify ambiguities
2. **Clarifying Questions** (AskUserQuestion): Scope, technical choices, priority, constraints
3. **Context Gathering**: Glob for files, Grep for code, read configs

## Output: .caw/task_plan.md

**CRITICAL**: Use Write tool to create file. Must include Phase Deps and step Deps columns.

```markdown
# Task Plan: [Title]

## Metadata
| Field | Value |
|-------|-------|
| **Created** | [timestamp] |
| **Source** | User request / Plan Mode import |

## Execution Phases

### Phase 1: [Name]
**Phase Deps**: -

| # | Step | Status | Agent | Deps | Notes |
|---|------|--------|-------|------|-------|
| 1.1 | [Step] | ⏳ | Builder | - | |
| 1.2 | [Step] | ⏳ | Builder | - | ⚡ Parallel OK |

### Phase 2: [Name]
**Phase Deps**: phase 1

| # | Step | Status | Agent | Deps | Notes |
|---|------|--------|-------|------|-------|
| 2.1 | [Step] | ⏳ | Builder | - | |
| 2.2 | [Step] | ⏳ | Builder | 2.1 | |
```

## Parallel Execution Requirements

### Phase Deps (Required)
- `**Phase Deps**: -` - No dependencies
- `**Phase Deps**: phase 1` - Depends on Phase 1
- `**Phase Deps**: phase 2, phase 3` - Depends on multiple

### Deps Column (Required)
- `-` - No dependencies within phase
- `2.1` - Depends on step 2.1
- `1.*` - Depends on all Phase 1 steps

### Parallel Notes
- `⚡ Parallel OK` - Can run with other marked steps
- `🔒 Sequential` - Must run alone

## Plan Mode Conversion

| Plan Mode | CAW |
|-----------|-----|
| `# Title` | Task Plan title |
| `- [ ] item` | Step |
| File mentions | Context Files |
| Code blocks | Implementation hints |

## Integration

- **Triggers ContextManager**: Updates manifest
- **Works with Hooks**: SessionStart may pre-detect plans
- **Enables PreToolUse Hook**: Validates plan adherence

## Tips

- Thorough discovery reduces rework
- Confirm understanding before generating plan
- Reference specific files and line numbers
- Keep phases small and testable
- Design phases for parallel execution
