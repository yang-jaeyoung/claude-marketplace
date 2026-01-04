---
description: Start a context-aware workflow session. Analyzes task requirements, imports Plan Mode plans, and generates structured task_plan.md.
---

# /caw:start - Workflow Initialization

Initialize a context-aware workflow session for structured task execution.

## Invocation Modes

### Mode 1: New Task with Description
When invoked with a task description:
```
/caw:start "Implement user authentication with JWT"
```

1. **Acknowledge** the task description
2. **Invoke Planner Agent** using Task tool with subagent_type="caw:planner"
3. Planner will:
   - Ask clarifying questions if needed
   - Explore codebase for context
   - Generate `.caw/task_plan.md`

### Mode 2: Import from Plan Mode
When invoked with `--from-plan`:
```
/caw:start --from-plan
```

1. **Detect** existing Plan Mode output:
   - Check `.claude/plan.md` (default)
   - Check `.claude/plans/current.md`
2. If found:
   - Display plan summary
   - Ask user to confirm import
   - Convert to `.caw/task_plan.md` format
3. If not found:
   - Inform user no plan detected
   - Offer to start fresh workflow

### Mode 3: Specific Plan File
When invoked with `--plan-file <path>`:
```
/caw:start --plan-file docs/my-plan.md
```

1. **Read** the specified plan file
2. **Validate** it contains actionable steps
3. **Convert** to `.caw/task_plan.md` format

## Interactive Discovery

When starting a new task (Mode 1), engage in discovery dialogue:

1. **Initial Analysis**:
   - Parse the task description for key entities
   - Identify ambiguous requirements
   - Detect mentioned files or components

2. **Clarifying Questions** (use AskUserQuestion):
   - Scope boundaries: "Should this include X?"
   - Technical choices: "Prefer approach A or B?"
   - Priority: "Core functionality first, or complete feature?"
   - Constraints: "Any existing patterns to follow?"

3. **Context Gathering**:
   - Use Glob to find relevant files
   - Use Grep to search for related code
   - Read key configuration files (package.json, tsconfig.json, etc.)

## Output: .caw/task_plan.md

**IMPORTANT**: You MUST use the Write tool to create `.caw/task_plan.md`. First create the `.caw/` directory if it doesn't exist. Do not just display the plan - actually write it to disk.

Generate and **write** `.caw/task_plan.md` with this structure:

```markdown
# Task Plan: [Task Title]

## Metadata
| Field | Value |
|-------|-------|
| **Created** | [timestamp] |
| **Source** | User request / Plan Mode import |
| **Status** | Planning |

## Context Files

### Active Context
| File | Reason | Status |
|------|--------|--------|
| `src/auth/index.ts` | Main implementation target | 📝 Edit |

### Project Context (Read-Only)
- `GUIDELINES.md`
- `package.json`

## Task Summary
[2-3 sentence summary of what will be accomplished]

## Execution Phases

### Phase 1: [Phase Name]
| # | Step | Status | Notes |
|---|------|--------|-------|
| 1.1 | [Step description] | ⏳ Pending | |

### Phase 2: [Phase Name]
| # | Step | Status | Notes |
|---|------|--------|-------|
| 2.1 | [Step description] | ⏳ Pending | |

## Validation Checklist
- [ ] Existing tests pass
- [ ] New tests added
- [ ] Code follows project conventions

## Open Questions
- [Any unresolved questions for user]
```

## Integration

- **Triggers ContextManager Skill**: Updates `.caw/context_manifest.json`
- **Works with Hooks**: SessionStart hook may pre-detect plans
- **Enables PreToolUse Hook**: After plan exists, hook validates plan adherence

## Tips

- Be thorough in discovery - better planning reduces rework
- Always confirm understanding before generating plan
- Reference specific files and line numbers when possible
- Keep phases small and testable
