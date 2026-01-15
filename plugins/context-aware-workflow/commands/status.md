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

### Step 2.5: Check Active Mode

Check if `.caw/mode.json` exists to determine active mode:

```json
{
  "active_mode": "DEEP_WORK" | "NORMAL",
  "activated_at": "ISO timestamp",
  "keyword_trigger": "deepwork" | null,
  "completion_required": true | false
}
```

If file doesn't exist, default to NORMAL mode.

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

### Step 3.5: Generate Visual Progress Bar

Create a visual progress bar based on completion percentage:

```
bar_width = 20  # Total characters in progress bar
filled = round(progress_percent / 100 * bar_width)
empty = bar_width - filled

progress_bar = "█" * filled + "░" * empty
```

**Progress Bar Examples**:
- 0%:   `░░░░░░░░░░░░░░░░░░░░`
- 25%:  `█████░░░░░░░░░░░░░░░`
- 50%:  `██████████░░░░░░░░░░`
- 75%:  `███████████████░░░░░`
- 100%: `████████████████████`

### Step 4: Display Status

**Standard Output Format**:

```
📊 Workflow Status
══════════════════════════════════════════

📋 Task: [Task Title from .caw/task_plan.md]
📁 Plan: .caw/task_plan.md
🕐 Created: [date from metadata]
📌 Status: [status from metadata]
🎯 Mode: [DEEP WORK | NORMAL] (if Deep Work active, show: "⚡ Must complete ALL tasks")

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

   [progress_bar] [X]%

   ✅ Completed: [N]
   🔄 In Progress: [N]
   ⏳ Pending: [N]
   ❌ Blocked: [N]

──────────────────────────────────────────
⏳ Remaining Tasks
──────────────────────────────────────────
[List first 5 pending/in-progress steps]
  • [N.X] [Step description]
  • [N.Y] [Step description]
  [+N more if applicable]

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

## Worktree Status (Parallel Execution)

### Step 3.5b: Check for Active Worktrees

Scan for `.worktrees/caw-step-*` directories:

```
if .worktrees/ exists:
    worktrees = glob(".worktrees/caw-step-*")
    for each worktree:
        read worktree/.caw/task_plan.md
        extract step status
```

### Worktree Status Display

If active worktrees exist, add this section after Progress:

```
──────────────────────────────────────────
🌳 Parallel Worktrees
──────────────────────────────────────────
│ Path                      │ Step │ Status        │
│ .worktrees/caw-step-2.2   │ 2.2  │ ✅ Complete   │
│ .worktrees/caw-step-2.3   │ 2.3  │ 🔄 In Progress│

💡 Run /caw:merge to merge completed worktrees
```

### Parallel Opportunity Display

If `Deps` column exists in task_plan.md, show runnable parallel steps:

```
──────────────────────────────────────────
⚡ Parallel Opportunities
──────────────────────────────────────────
Runnable in parallel:
  • 2.2 - Implement token generation
  • 2.3 - Implement token validation

💡 Run /caw:next --parallel to execute both
   Run /caw:worktree create for isolated execution
```

### No Worktrees Case

If no worktrees but parallel opportunities exist:

```
⚡ Tip: Steps 2.2 and 2.3 can run in parallel
   Use /caw:next --parallel or /caw:worktree create
```

## Integration

- **Reads**: `.caw/task_plan.md`, `.worktrees/caw-step-*/.caw/task_plan.md`
- **Suggests**: `/caw:next`, `/caw:merge`, `/caw:worktree` commands
- **Works with**: All CAW commands
- **Uses**: `dependency-analyzer` skill for parallel opportunity detection
