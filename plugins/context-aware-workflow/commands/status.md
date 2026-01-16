---
description: Display current workflow status, progress, and next actions
---

# /caw:status - Workflow Status

Display the current state of the context-aware workflow, including progress, current phase, and suggested next actions.

## Usage

```bash
/caw:status             # Standard status output
/caw:status --verbose   # Detailed status with file lists
/caw:status -v          # Same as --verbose
/caw:status --worktrees # Show active worktree status
/caw:status --agents    # Show background agent status
/caw:status --all       # Show everything (verbose + worktrees + agents)
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

## Worktree Status (`--worktrees`)

### Detection Logic

Scan for both phase-based and step-based worktrees:

```
if .worktrees/ exists:
    # Phase worktrees (primary)
    phase_worktrees = glob(".worktrees/phase-*")

    # Step worktrees (legacy)
    step_worktrees = glob(".worktrees/caw-step-*")

    for each worktree:
        read worktree/.caw/task_plan.md
        calculate phase/step completion
```

### Worktree Status Display (`/caw:status --worktrees`)

```
📊 Workflow Status
══════════════════════════════════════════

📋 Task: User Authentication System
📈 Progress: 45% (9/20 steps)

──────────────────────────────────────────
🌳 Active Worktrees
──────────────────────────────────────────

## Phase Worktrees
| Phase | Branch      | Directory          | Status      | Progress |
|-------|-------------|--------------------| ------------|----------|
| 2     | caw/phase-2 | .worktrees/phase-2 | 🔄 In Progress | 3/5   |
| 3     | caw/phase-3 | .worktrees/phase-3 | ✅ Complete    | 4/4   |
| 4     | caw/phase-4 | .worktrees/phase-4 | ⏳ Pending     | 0/3   |

## Step Worktrees (Legacy)
| Step | Branch        | Directory             | Status      |
|------|---------------|-----------------------|-------------|
| (none) |

──────────────────────────────────────────
⚡ Parallel Opportunities
──────────────────────────────────────────
Phases 2, 3, 4 share same Phase Deps (phase 1)
→ Can run in parallel worktrees

Runnable steps in main:
  • 1.2 - Add type definitions
  • 1.3 - Setup test fixtures

💡 Commands:
  /caw:merge                     # Merge completed (phase-3)
  /caw:next --worktree phase 5   # Create new worktree
  /caw:worktree clean            # Clean completed worktrees
══════════════════════════════════════════
```

### Worktree Completion Detection

```python
def get_worktree_status(worktree_path):
    task_plan = read(f"{worktree_path}/.caw/task_plan.md")
    phase_num = extract_phase_number(worktree_path)

    total_steps = count_steps_in_phase(task_plan, phase_num)
    completed_steps = count_completed_steps(task_plan, phase_num)

    if completed_steps == total_steps:
        return "✅ Complete"
    elif completed_steps > 0:
        return "🔄 In Progress"
    else:
        return "⏳ Pending"
```

## Background Agent Status (`--agents`)

### Detection Logic

Track background agents launched via `run_in_background=true`:

```
# Agent tracking file: .caw/agents.json
{
  "active_agents": [
    {
      "task_id": "abc123",
      "step": "2.2",
      "started": "2026-01-16T10:30:00Z",
      "status": "running"
    }
  ]
}
```

### Agent Status Display (`/caw:status --agents`)

```
📊 Workflow Status
══════════════════════════════════════════

📋 Task: User Authentication System
📈 Progress: 45% (9/20 steps)

──────────────────────────────────────────
⚡ Background Agents
──────────────────────────────────────────

| Task ID | Step | Description              | Status  | Duration |
|---------|------|--------------------------|---------|----------|
| abc123  | 2.2  | Token generation         | 🔄 Running | 2m 30s |
| def456  | 2.3  | Token validation         | 🔄 Running | 2m 15s |
| ghi789  | 2.4  | Auth middleware          | ✅ Done    | 5m 10s |

💡 Commands:
  TaskOutput abc123        # Get specific agent output
  TaskOutput def456 --wait # Wait for completion

──────────────────────────────────────────
📊 Agent Summary
──────────────────────────────────────────
  🔄 Running: 2
  ✅ Completed: 1
  ❌ Failed: 0

Estimated completion: ~2 minutes
══════════════════════════════════════════
```

### Agent State Management

```python
# When launching background agent
agent_entry = {
    "task_id": task_result.task_id,
    "step": step_number,
    "started": datetime.now().isoformat(),
    "status": "running"
}
append_to_agents_json(agent_entry)

# When agent completes (via polling or callback)
update_agent_status(task_id, "done" | "failed")
update_task_plan_status(step_number, "✅" | "❌")
```

## Combined Status (`--all`)

Shows everything: verbose + worktrees + agents

```bash
/caw:status --all
```

Equivalent to:
```bash
/caw:status --verbose --worktrees --agents
```

## Parallel Opportunity Display

If `Phase Deps` exists in task_plan.md, show Phase-level parallel opportunities:

```
──────────────────────────────────────────
⚡ Parallel Execution Opportunities
──────────────────────────────────────────

## Phase Parallel
Phases with same Phase Deps can run in parallel worktrees:

  Phase Deps: phase 1
    → Phase 2 ⏳
    → Phase 3 ⏳
    → Phase 4 ⏳

  💡 /caw:worktree create phase 2,3,4

## Step Parallel (within current phase)
Steps with same Deps can run in parallel:

  Phase 2, Deps: -
    → 2.2 Token generation ⏳
    → 2.3 Token validation ⏳

  💡 /caw:next --parallel phase 2
──────────────────────────────────────────
```

## Integration

- **Reads**: `.caw/task_plan.md`, `.worktrees/phase-*/.caw/task_plan.md`, `.caw/agents.json`
- **Suggests**: `/caw:next`, `/caw:merge`, `/caw:worktree`, `TaskOutput` commands
- **Works with**: All CAW commands
- **Uses**: `dependency-analyzer` skill for parallel opportunity detection
