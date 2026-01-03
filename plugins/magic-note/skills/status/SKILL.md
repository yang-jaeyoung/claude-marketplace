---
name: status
description: >-
  Get a quick status summary of workflow progress.
  Shows current task, blockers, and next actions at a glance.
  Triggers on: "/status", "workflow status", "show progress",
  "what's the status", "진행 상황", "현재 상태"
---

# Workflow Status Skill

This skill provides a quick status summary of workflow progress.

## When to Activate

Activate this skill when:
- User says "/status" or "/status [workflow_id]"
- User asks about progress or current state
- User wants a quick overview of the workflow

## How to Show Status

### 1. Get Workflow Status

```
get_workflow_status({
  workflowId: "[id]",
  format: "summary"  // or "detailed" or "minimal"
})
```

### 2. Format Options

**Minimal Format** (one line):
```
Add User Authentication: 50% (active)
```

**Summary Format** (default):
```
📋 Add User Authentication
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Progress: ████████░░░░░░░░ 50%

🔄 In Progress:
   • Implement JWT token service

❌ Blocked:
   • Database migration (waiting for DBA)

⏳ Next:
   • Add login/register endpoints
   • Create auth middleware

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Status: active | Updated: 5 min ago
```

**Detailed Format** (all tasks):
```
📋 Add User Authentication
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Progress: ████████░░░░░░░░ 50%

📝 All Tasks:
   ✅ Design user model schema
   ✅ Implement password hashing
   🔄 Implement JWT token service
   ⬜ Add login/register endpoints
   ⬜ Create auth middleware
   🚫 Database migration (blocked)
   ⬜ Write tests

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Status: active | Updated: 5 min ago
```

## Status Emojis

| Status | Emoji | Meaning |
|--------|-------|---------|
| pending | ⬜ | Not started |
| in_progress | 🔄 | Currently working |
| verifying | 🔍 | Testing/verification |
| review | 📝 | In review |
| completed | ✅ | Done |
| failed | ❌ | Failed |
| skipped | ⏭️ | Skipped |
| blocked | 🚫 | Blocked |

## Quick Actions

After showing status, suggest relevant actions based on state:

**If task in progress**:
```
💡 Tip: Use set_task_status to mark "Implement JWT" as completed
```

**If tasks blocked**:
```
⚠️ You have 1 blocked task. Resolve blockers to continue.
```

**If almost complete**:
```
🎉 Almost there! Just 2 tasks remaining.
```

## Example Usage

**User**: /status

**If single active workflow**:
Shows summary status of that workflow

**If multiple workflows**:
```
📊 Workflow Status Summary

1. Add User Authentication
   ████████░░░░░░░░ 50% | 🔄 JWT service

2. Refactor Database
   ██░░░░░░░░░░░░░░ 15% | ⬜ Not started

3. API Documentation
   ██████████████░░ 85% | 🔄 Final review

Total: 3 active workflows
```

**User**: /status wf_abc123

Shows detailed status for specific workflow

## Progress Calculation

Progress percentage is calculated as:
```
percentage = (completed_tasks / total_tasks) * 100
```

The progress bar uses 16 characters:
- Each █ represents 6.25% progress
- ░ represents incomplete portion

## Integration with Other Skills

- Use with `/resume` to get context before continuing
- Use with `/workflow` to check newly created workflow
- Pairs with `create_checkpoint` at milestones
