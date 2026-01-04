---
name: workflow
description: >-
  Create and manage multi-step workflows for complex coding tasks.
  Use when starting a new feature, refactoring project, or any multi-step work.
  Triggers on: "/workflow", "create workflow", "start workflow", "new workflow",
  "워크플로우 생성", "작업 시작"
---

# Workflow Management Skill

This skill helps create and manage multi-step coding workflows with task tracking, checkpoints, and progress monitoring.

## Plan Mode Handling

**IMPORTANT**: If Claude Code is currently in **plan mode** (EnterPlanMode was used), MCP tools cannot be called directly. In this case:

1. **During Plan Mode**: Generate the workflow structure in your plan, but DO NOT attempt to call `create_workflow` MCP tool.

2. **After Plan Approval**: When the user approves the plan and exits plan mode (ExitPlanMode), THEN call `create_workflow` to create the actual workflow.

3. **Workflow Offer Format in Plan Mode**:
   ```
   📋 이 계획을 워크플로우로 변환할 수 있습니다.

   Plan 승인 후 자동으로 워크플로우가 생성됩니다:
   - [N]개 태스크
   - 체크포인트로 진행 상황 추적 가능

   또는 나중에 `/magic-note:workflow` 명령으로 수동 생성 가능합니다.
   ```

4. **Post-Plan Workflow Creation**: After ExitPlanMode, immediately create the workflow using the plan content as the source.

## When to Activate

Activate this skill when:
- User says "/workflow" or "/workflow [title]"
- Starting a new feature implementation
- Beginning a multi-step refactoring task
- Planning a complex debugging session
- Managing a project with multiple phases
- **After plan approval** when a structured plan was generated in plan mode

## How to Create a Workflow

### 1. Gather Information

If user provides a title, use it directly. Otherwise, ask:
- What is the goal of this workflow?
- What are the main tasks/steps?

### 2. Create Workflow Using MCP Tool

Use the `create_workflow` MCP tool:

```
create_workflow({
  title: "[workflow title]",
  description: "[optional description]",
  project: "[current project name]",
  tasks: [
    { title: "Task 1", description: "Details", priority: "high" },
    { title: "Task 2", description: "Details", priority: "medium" },
    ...
  ],
  tags: ["feature", "sprint-1", ...]
})
```

### 3. Confirm Creation

After creating, display:

```
📋 Workflow Created: [title]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ID: [workflow_id]
Tasks: [count] tasks

⏳ Tasks:
1. [Task 1 title]
2. [Task 2 title]
...

Quick actions:
• set_task_status - Start working on a task
• create_checkpoint - Save progress
• get_workflow_status - Check progress
```

## Task Management

### Starting a Task
```
set_task_status({
  workflowId: "[id]",
  taskId: "[task_id]",
  status: "in_progress"
})
```

### Completing a Task
```
set_task_status({
  workflowId: "[id]",
  taskId: "[task_id]",
  status: "completed",
  note: "What was accomplished"
})
```

### Adding New Tasks
```
add_task({
  workflowId: "[id]",
  title: "New task",
  description: "Details",
  priority: "medium"
})
```

## Checkpoint Management

Create checkpoints at important milestones:
```
create_checkpoint({
  workflowId: "[id]",
  notes: "Completed authentication, moving to API routes",
  reason: "milestone"
})
```

## Example Usage

**User**: /workflow Add user authentication

**Response**:
1. Create workflow with title "Add User Authentication"
2. Generate common tasks:
   - Design user model schema
   - Implement password hashing
   - Create JWT token service
   - Add login/register endpoints
   - Create auth middleware
   - Add protected routes
   - Write tests
3. Display created workflow with task list

## Output Format

Always use this format for workflow status:

```
📋 [Workflow Title]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Progress: ████████░░░░░░░░ 50%

🔄 In Progress:
   • [Current task]

⏳ Next:
   • [Next task 1]
   • [Next task 2]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Status: active | Updated: 5 min ago
```
