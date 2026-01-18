---
description: Display current workflow status, progress, and next actions
---

# /cw:status - Workflow Status

Display current state of the context-aware workflow.

## Usage

```bash
/cw:status             # Standard status
/cw:status --verbose   # Detailed with file lists
/cw:status --worktrees # Show active worktree status
/cw:status --agents    # Show background agent status
/cw:status --all       # Everything (verbose + worktrees + agents)
```

## Behavior

### Step 1: Check Task Plan
Look for `.caw/task_plan.md`. Show help if not found.

### Step 2: Parse & Calculate Progress
```
progress_percent = (completed / total) * 100
progress_bar = "█" * filled + "░" * empty
```

### Step 3: Check Active Mode
Read `.caw/mode.json` for DEEP_WORK or NORMAL mode.

### Step 4: Display Status

**Standard Output:**
```
📊 Workflow Status
══════════════════════════════════════════
📋 Task: [Title]
📌 Status: [status]
🎯 Mode: [DEEP WORK | NORMAL]

──────────────────────────────────────────
Phase [N]: [Phase Name]
├─ [N.1] [Step]    ✅ Complete
├─ [N.2] [Step]    🔄 In Progress  ← current
└─ [N.3] [Step]    ⏳ Pending

══════════════════════════════════════════
📈 Progress: [X]% ([completed]/[total])
   [████████░░░░░░░░░░░░] [X]%
══════════════════════════════════════════
```

## Status Icons

| Icon | Status | Meaning |
|------|--------|---------|
| ✅ | Complete | Finished |
| 🔄 | In Progress | Working |
| ⏳ | Pending | Not started |
| ❌ | Blocked | Cannot proceed |
| ⏭️ | Skipped | Bypassed |

## Current Step Detection
1. First 🔄 (In Progress) step
2. If none, first ⏳ (Pending) step
3. If all complete, show completion message

## Flags

### --verbose
Adds Context Files and Recent Activity sections.

### --worktrees
Shows phase-based and step-based worktrees with:
- Branch, Directory, Status, Progress
- Parallel execution opportunities

### --agents
Shows background agents with:
- Task ID, Step, Status, Duration
- Commands: `TaskOutput <id>` to check output

## Edge Cases

- **All Complete**: Shows success message with suggested actions
- **All Blocked**: Lists blocked steps with resolution hints

## Integration

- **Reads**: `.caw/task_plan.md`, `.worktrees/phase-*/.caw/task_plan.md`, `.caw/agents.json`
- **Uses**: `dependency-analyzer` for parallel opportunities
