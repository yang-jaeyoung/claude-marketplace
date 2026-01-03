---
name: resume
description: >-
  Resume work on an existing workflow from where you left off.
  Shows last checkpoint, current progress, and what to work on next.
  Triggers on: "/resume", "resume workflow", "continue workflow",
  "where did I leave off", "이어서 작업", "작업 재개"
---

# Resume Workflow Skill

This skill helps resume work on an existing workflow by showing context about where you left off.

## When to Activate

Activate this skill when:
- User says "/resume" or "/resume [workflow_id]"
- User asks "where did I leave off?"
- User wants to continue previous work
- Starting a new session on an existing task

## How to Resume

### 1. Find the Workflow

If no workflow ID provided:
```
list_workflows({ activeOnly: true, limit: 5 })
```

Show active workflows and ask which to resume:
```
📋 Active Workflows:
1. [title] - 50% complete (updated 2h ago)
2. [title] - 30% complete (updated 1d ago)

Which workflow would you like to resume?
```

### 2. Get Resume Context

Once workflow is identified:
```
resume_workflow({ workflowId: "[id]" })
```

This returns:
- Last checkpoint with notes
- Current progress percentage
- Last completed task
- Current in-progress task
- Next tasks to do
- Recent activity log

### 3. Display Resume Context

Format the output clearly:

```
👋 Resume: [Workflow Title]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📸 Last checkpoint: 2 hours ago
   "Completed user model, starting JWT"

📊 Progress: ████████░░░░░░░░ 50%

✅ Last completed: Create user model
   (2 hours ago)

🔄 Continue working on:
   → Implement JWT token service
     Generate and validate JWT tokens...

⏳ Next up:
   1. Add login/register endpoints
   2. Create auth middleware
   3. Add protected routes

📝 Recent activity:
   ✅ task completed
   🔄 task started
   📸 checkpoint created

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Quick actions:
  • set_task_status to update progress
  • create_checkpoint to save state
  • get_timeline for full history
```

### 4. Offer Next Steps

After showing context, offer to:
- Continue with the in-progress task
- Mark current task as complete
- Create a checkpoint before continuing

## Session Continuity Pattern

When user resumes:

1. **Check for in-progress task**: If exists, offer to continue
2. **Check for blockers**: Alert if any tasks are blocked
3. **Show relevant context**: Files, decisions, notes from previous session
4. **Suggest next action**: Based on workflow state

## Example Usage

**User**: /resume

**Response (if single active workflow)**:
Shows full resume context for that workflow

**Response (if multiple active workflows)**:
```
📋 You have 3 active workflows:

1. Add User Authentication
   Progress: ████████░░░░░░░░ 50%
   Last activity: 2 hours ago

2. Refactor Database Layer
   Progress: ██░░░░░░░░░░░░░░ 15%
   Last activity: 1 day ago

3. Add API Documentation
   Progress: ██████████████░░ 85%
   Last activity: 30 min ago

Which workflow would you like to resume? (Enter number or ID)
```

## Restore from Checkpoint

If user wants to go back to a previous state:
```
list_checkpoints({ workflowId: "[id]" })
restore_checkpoint({ workflowId: "[id]", checkpointId: "[cp_id]" })
```

This restores task statuses to the checkpoint state.

## Best Practices

1. **Always create checkpoint before ending session**
2. **Add notes to checkpoints** describing current state
3. **Mark tasks as blocked** if waiting on something
4. **Link relevant notes** to tasks for context
