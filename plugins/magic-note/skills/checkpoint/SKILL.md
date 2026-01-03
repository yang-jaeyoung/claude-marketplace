---
name: checkpoint
description: >-
  Save a checkpoint to preserve current workflow state.
  Use before ending a session, at milestones, or before risky changes.
  Triggers on: "/checkpoint", "save checkpoint", "save progress",
  "체크포인트", "진행 저장"
---

# Checkpoint Skill

This skill creates checkpoints to save workflow state for session continuity.

## When to Activate

Activate this skill when:
- User says "/checkpoint" or "/checkpoint [notes]"
- Before ending a coding session
- At major milestones (phase complete, feature done)
- Before attempting risky changes
- When switching to a different task

## How to Create Checkpoint

### 1. Identify Active Workflow

If not specified, get the currently active workflow:
```
list_workflows({ activeOnly: true, limit: 1 })
```

### 2. Create Checkpoint

```
create_checkpoint({
  workflowId: "[id]",
  notes: "[summary of current state]",
  reason: "manual" | "milestone" | "session_end"
})
```

### 3. Confirm Creation

```
📸 Checkpoint Created!
━━━━━━━━━━━━━━━━━━━━━━━
ID: cp_abc123
Workflow: Add User Authentication
Reason: milestone

📝 Notes:
   "Completed JWT implementation, auth middleware works"

📊 State Captured:
   ✅ 3 tasks completed
   🔄 1 task in progress
   ⬜ 4 tasks pending

━━━━━━━━━━━━━━━━━━━━━━━
Use restore_checkpoint to return to this state.
```

## Checkpoint Reasons

| Reason | When to Use |
|--------|-------------|
| `manual` | User explicitly requests checkpoint |
| `milestone` | Major feature or phase completed |
| `session_end` | Before ending a coding session |

## Auto-Checkpoint Triggers

Consider auto-creating checkpoints:
- Every 30 minutes of active work
- When task status changes to `completed`
- Before risky operations (major refactors)
- When switching between workflows

## Example Usage

**User**: /checkpoint

**Response**:
```
📸 Checkpoint created for "Add User Authentication"

Current state saved:
• Progress: 50% (3/6 tasks)
• Current task: Implement JWT token service
• Last activity: Added token validation

Notes: [auto-generated summary]
```

**User**: /checkpoint Finished auth middleware, works with all routes

**Response**:
```
📸 Checkpoint Created!

📝 Notes: "Finished auth middleware, works with all routes"

Your progress has been saved. You can safely:
• End this session
• Switch to another workflow
• Attempt risky changes

Use /resume to continue later.
```

## Best Practices

### 1. Add Meaningful Notes
Good: "JWT validation working, refresh token logic pending"
Bad: "checkpoint" or "saving"

### 2. Create Before Risky Changes
```
/checkpoint Before refactoring token validation
[make risky changes]
# If things go wrong:
restore_checkpoint({ ... })
```

### 3. Create at Natural Breakpoints
- Feature completion
- Phase transitions
- Before meetings/breaks
- Before complex debugging

## Viewing Checkpoints

To see all checkpoints:
```
list_checkpoints({ workflowId: "[id]" })
```

Output:
```
📸 Checkpoints for "Add User Authentication"

1. cp_xyz789 - 30 min ago (milestone)
   "Completed JWT implementation"

2. cp_abc123 - 2 hours ago (manual)
   "Starting auth middleware"

3. cp_def456 - 1 day ago (session_end)
   "End of Friday session"
```

## Restoring from Checkpoint

If you need to go back:
```
restore_checkpoint({
  workflowId: "[id]",
  checkpointId: "cp_abc123"
})
```

This restores:
- Task statuses to checkpoint state
- Step completion states
- Progress calculations

**Note**: Events are NOT deleted (history is preserved)

## Session End Pattern

At the end of a session:

```
1. Mark current task status appropriately
2. Create checkpoint with session summary
3. Note any blockers or next steps

Example:
/checkpoint Session end - JWT working, need to add refresh tokens tomorrow
```
