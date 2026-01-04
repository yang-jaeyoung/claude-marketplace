---
description: Display current workflow status, progress, and next actions
---

# /caw:status - Workflow Status

Display the current state of the context-aware workflow, including progress, current phase, and suggested next actions.

## Usage

```bash
/caw:status           # Standard status output
/caw:status --verbose # Detailed status with file lists
/caw:status -v        # Same as --verbose
```

## Behavior

### Step 1: Check for Task Plan

1. Look for `.caw/task_plan.md`
2. If not found, display helpful message:

```
📋 No active workflow

.caw/task_plan.md not found.

💡 Start a new workflow:
   /caw:start "your task description"
   /caw:start --from-plan
```

### Step 2: Parse Task Plan

Read and parse `.caw/task_plan.md` to extract:
- Task title from header
- Metadata (created date, status)
- All phases and steps with their statuses
- Context files

### Step 3: Calculate Progress

Count steps by status:
```
total = count(all steps)
completed = count(steps with ✅)
in_progress = count(steps with 🔄)
pending = count(steps with ⏳)
blocked = count(steps with ❌)

progress_percent = (completed / total) * 100
```

### Step 4: Display Status

**Standard Output Format**:

```
📊 Workflow Status
══════════════════════════════════════════

📋 Task: [Task Title from .caw/task_plan.md]
📁 Plan: .caw/task_plan.md
🕐 Created: [date from metadata]
📌 Status: [status from metadata]

──────────────────────────────────────────
Phase [N]: [Phase Name]
──────────────────────────────────────────
├─ [N.1] [Step description]    ✅ Complete
├─ [N.2] [Step description]    🔄 In Progress  ← current
├─ [N.3] [Step description]    ⏳ Pending
└─ [N.4] [Step description]    ⏳ Pending

──────────────────────────────────────────
Phase [N+1]: [Phase Name]
──────────────────────────────────────────
├─ [N+1.1] [Step description]  ⏳ Pending
└─ [N+1.2] [Step description]  ⏳ Pending

══════════════════════════════════════════
📈 Progress: [X]% ([completed]/[total] steps)

   ✅ Completed: [N]
   🔄 In Progress: [N]
   ⏳ Pending: [N]
   ❌ Blocked: [N]

💡 Next: /caw:next to continue with step [N.X]
══════════════════════════════════════════
```

**Verbose Output** (`--verbose` or `-v`):

Adds these sections:

```
──────────────────────────────────────────
📂 Context Files
──────────────────────────────────────────

Active Context (will be modified):
  • src/auth/jwt.ts - Main JWT implementation
  • src/middleware/auth.ts - Auth middleware

Project Context (read-only):
  • package.json - Dependencies
  • GUIDELINES.md - Project conventions

──────────────────────────────────────────
📝 Recent Activity
──────────────────────────────────────────
  • Step 2.1 completed - src/auth/jwt.ts created
  • Step 2.2 in progress - implementing middleware
```

## Status Icons Reference

| Icon | Status | Meaning |
|------|--------|---------|
| ✅ | Complete | Step finished and verified |
| 🔄 | In Progress | Currently being worked on |
| ⏳ | Pending | Not started yet |
| ❌ | Blocked | Cannot proceed |
| ⏭️ | Skipped | Intentionally skipped |

## Current Step Detection

The "current" step is determined by:
1. First step with 🔄 (In Progress) status
2. If no in-progress, first step with ⏳ (Pending) status
3. If all complete, show completion message

## Edge Cases

### All Steps Complete
```
📊 Workflow Status
══════════════════════════════════════════

🎉 All steps complete!

📋 Task: [Task Title]
📈 Progress: 100% (10/10 steps)

💡 Suggested next actions:
   • Review the implementation
   • Run full test suite
   • Create a new workflow for next task
```

### All Steps Blocked
```
📊 Workflow Status
══════════════════════════════════════════

⚠️ Workflow blocked

📋 Task: [Task Title]
📈 Progress: 30% (3/10 steps)
❌ Blocked: 2 steps

Blocked steps:
  • 2.3: Missing database configuration
  • 2.4: Depends on 2.3

💡 Resolve blockers to continue
```

## Integration

- **Reads**: `.caw/task_plan.md`
- **Suggests**: `/caw:next` command
- **Works with**: All CAW commands
