# MCP Tool API Design: Workflow Management

> **Design Date**: 2026-01-03
> **Status**: Design Complete
> **Total Tools**: 30 (기존 10 + 신규 20)

---

## Design Principles

1. **Workflow가 Aggregate Root** - Task 조작은 항상 Workflow 컨텍스트에서
2. **명령과 조회 분리** (CQRS-lite) - 복잡한 조회는 별도 도구로
3. **이벤트 암묵적 기록** - 모든 변경 시 자동 이벤트 로깅
4. **멱등성 보장** - 동일 요청 반복 시 동일 결과

---

## Tool Categories Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    MCP Tool Categories                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  📁 WORKFLOW MANAGEMENT (6 tools)                               │
│  ├── create_workflow      새 워크플로우 생성                    │
│  ├── get_workflow         워크플로우 상세 조회                   │
│  ├── list_workflows       워크플로우 목록 조회                   │
│  ├── update_workflow      워크플로우 메타데이터 수정             │
│  ├── delete_workflow      워크플로우 삭제                        │
│  └── archive_workflow     워크플로우 아카이브                    │
│                                                                 │
│  ✅ TASK MANAGEMENT (6 tools)                                   │
│  ├── add_task             태스크 추가                           │
│  ├── update_task          태스크 수정                           │
│  ├── remove_task          태스크 제거                           │
│  ├── reorder_tasks        태스크 순서 변경                       │
│  ├── set_task_status      태스크 상태 변경 ⭐                   │
│  └── delegate_task        태스크 위임 (에이전트)                 │
│                                                                 │
│  📸 CHECKPOINT MANAGEMENT (3 tools)                             │
│  ├── create_checkpoint    체크포인트 생성                        │
│  ├── list_checkpoints     체크포인트 목록                        │
│  └── restore_checkpoint   체크포인트 복원                        │
│                                                                 │
│  🔗 ARTIFACT LINKING (2 tools)                                  │
│  ├── link_artifact        노트를 워크플로우/태스크에 연결         │
│  └── unlink_artifact      연결 해제                             │
│                                                                 │
│  📊 QUERY & INSIGHTS (3 tools)                                  │
│  ├── get_workflow_status  워크플로우 현황 요약 ⭐               │
│  ├── get_timeline         이벤트 타임라인 조회                   │
│  └── resume_workflow      마지막 상태에서 재개 정보 ⭐          │
│                                                                 │
│  ⭐ = 가장 빈번하게 사용될 핵심 도구                             │
└─────────────────────────────────────────────────────────────────┘
```

---

## Workflow Management Tools

### 1. create_workflow

```typescript
server.registerTool(
  'create_workflow',
  {
    title: 'Create Workflow',
    description: 'Create a new workflow for managing a multi-step task or project',
    inputSchema: {
      name: z.string().describe('Workflow name'),
      description: z.string().optional().describe('Detailed description'),
      workspace: z.string().optional().describe('Workspace/project name'),
      tasks: z.array(z.object({
        title: z.string(),
        description: z.string().optional(),
        priority: z.enum(['low', 'medium', 'high', 'critical']).optional(),
        phase: z.string().optional(),
      })).optional().describe('Initial tasks'),
      fromPlanNote: z.string().optional().describe('Create from existing plan note ID'),
      status: z.enum(['draft', 'active']).optional().default('draft'),
    },
  },
  async (params) => { /* implementation */ }
);
```

**Use Cases:**
- 새 프로젝트/기능 구현 시작
- 기존 plan 노트를 워크플로우로 변환
- 복잡한 작업을 구조화된 형태로 관리

---

### 2. get_workflow

```typescript
server.registerTool(
  'get_workflow',
  {
    title: 'Get Workflow',
    description: 'Get detailed information about a workflow including all tasks',
    inputSchema: {
      id: z.string().describe('Workflow ID'),
      includeTasks: z.boolean().optional().default(true),
      includeEvents: z.boolean().optional().default(false),
      eventLimit: z.number().optional().default(10),
    },
  },
  async (params) => { /* implementation */ }
);
```

---

### 3. list_workflows

```typescript
server.registerTool(
  'list_workflows',
  {
    title: 'List Workflows',
    description: 'List workflows with optional filtering',
    inputSchema: {
      workspace: z.string().optional(),
      status: z.enum(['draft', 'active', 'paused', 'blocked', 'completed', 'archived']).optional(),
      activeOnly: z.boolean().optional().default(false),
      search: z.string().optional(),
      limit: z.number().optional().default(20),
      sortBy: z.enum(['updated', 'created', 'name', 'progress']).optional().default('updated'),
    },
  },
  async (params) => { /* implementation */ }
);
```

---

### 4. update_workflow

```typescript
server.registerTool(
  'update_workflow',
  {
    title: 'Update Workflow',
    description: 'Update workflow metadata (name, description, status)',
    inputSchema: {
      id: z.string().describe('Workflow ID'),
      name: z.string().optional(),
      description: z.string().optional(),
      status: z.enum(['draft', 'active', 'paused', 'blocked', 'completed']).optional(),
      currentPhase: z.string().optional(),
      blockReason: z.string().optional(),
    },
  },
  async (params) => { /* implementation */ }
);
```

---

## Task Management Tools

### 5. add_task

```typescript
server.registerTool(
  'add_task',
  {
    title: 'Add Task',
    description: 'Add a new task to a workflow',
    inputSchema: {
      workflowId: z.string().describe('Workflow ID'),
      title: z.string().describe('Task title'),
      description: z.string().optional(),
      priority: z.enum(['low', 'medium', 'high', 'critical']).optional().default('medium'),
      phase: z.string().optional(),
      dependencies: z.array(z.string()).optional(),
      afterTask: z.string().optional().describe('Insert after this task ID'),
      assignee: z.enum(['human', 'agent']).optional().default('human'),
      agentType: z.string().optional(),
      artifactIds: z.array(z.string()).optional(),
    },
  },
  async (params) => { /* implementation */ }
);
```

---

### 6. set_task_status ⭐ (Core Tool)

```typescript
server.registerTool(
  'set_task_status',
  {
    title: 'Set Task Status',
    description: 'Change the status of a task (start, complete, block, etc.)',
    inputSchema: {
      taskId: z.string().describe('Task ID'),
      status: z.enum(['pending', 'ready', 'in_progress', 'blocked', 'completed', 'skipped']),
      note: z.string().optional().describe('Note about this status change'),
      blockReason: z.string().optional(),
      updateWorkflow: z.boolean().optional().default(true),
    },
  },
  async (params) => { /* implementation */ }
);
```

**Status Flow:**
```
pending → ready → in_progress → completed
                      ↓
                   blocked → unblocked → in_progress
                      ↓
                   skipped
```

---

### 7. delegate_task

```typescript
server.registerTool(
  'delegate_task',
  {
    title: 'Delegate Task',
    description: 'Delegate a task to a specialized agent for autonomous execution',
    inputSchema: {
      taskId: z.string().describe('Task ID'),
      agentType: z.string().describe('Agent type (e.g., "code-reviewer")'),
      instructions: z.string().optional(),
      autoComplete: z.boolean().optional().default(true),
    },
  },
  async (params) => { /* implementation */ }
);
```

---

## Checkpoint Management Tools

### 8. create_checkpoint

```typescript
server.registerTool(
  'create_checkpoint',
  {
    title: 'Create Checkpoint',
    description: 'Create a checkpoint to save current workflow state',
    inputSchema: {
      workflowId: z.string().describe('Workflow ID'),
      summary: z.string().optional().describe('Summary of current state'),
      trigger: z.enum(['manual', 'milestone', 'session_end']).optional().default('manual'),
    },
  },
  async (params) => { /* implementation */ }
);
```

---

### 9. restore_checkpoint

```typescript
server.registerTool(
  'restore_checkpoint',
  {
    title: 'Restore Checkpoint',
    description: 'Restore workflow state from a checkpoint',
    inputSchema: {
      checkpointId: z.string().describe('Checkpoint ID'),
      preview: z.boolean().optional().default(false).describe('Preview without applying'),
    },
  },
  async (params) => { /* implementation */ }
);
```

---

## Query & Insights Tools

### 10. get_workflow_status ⭐ (Core Tool)

```typescript
server.registerTool(
  'get_workflow_status',
  {
    title: 'Get Workflow Status',
    description: 'Get a human-readable summary of workflow progress',
    inputSchema: {
      workflowId: z.string().optional().describe('Defaults to active workflow'),
      workspace: z.string().optional(),
      format: z.enum(['summary', 'detailed', 'minimal']).optional().default('summary'),
    },
  },
  async (params) => { /* implementation */ }
);
```

**Example Output (summary format):**
```
📋 Authentication Implementation
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Progress: ████████░░░░░░░░ 53%

🔄 In Progress:
   • Implement refresh token logic

❌ Blocked:
   • Token revocation (needs design decision)

⏳ Ready (Next):
   • Create login endpoint
   • Create logout endpoint

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Status: active | Updated: 2 hours ago
```

---

### 11. resume_workflow ⭐ (Core Tool)

```typescript
server.registerTool(
  'resume_workflow',
  {
    title: 'Resume Workflow',
    description: 'Get context to resume work - shows where you left off',
    inputSchema: {
      workflowId: z.string().optional(),
      workspace: z.string().optional(),
      loadContext: z.boolean().optional().default(true),
    },
  },
  async (params) => { /* implementation */ }
);
```

**Example Output:**
```
👋 Resume: Authentication Implementation
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📸 Last checkpoint: 2 days ago
   JWT 구현 완료, 리프레시 토큰 진행 중

📊 Progress: ████████░░░░░░░░ 53%

✅ Last completed: Implement JWT validation
   (2 days ago)

🔄 Continue working on:
   → Implement refresh token logic
     Complete the refresh token generation and validation...

⏳ Next up:
   1. Create login endpoint
   2. Create logout endpoint
   3. Add auth middleware

📝 Recent activity:
   • task.completed: JWT validation
   • checkpoint.created: manual
   • task.started: refresh token

📎 Linked artifacts:
   • Auth Design Doc (plan)
   • Security Requirements (reference)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Quick actions:
  • set_task_status to update progress
  • create_checkpoint to save state
  • get_timeline for full history
```

---

### 12. get_timeline

```typescript
server.registerTool(
  'get_timeline',
  {
    title: 'Get Timeline',
    description: 'Get the event timeline for a workflow',
    inputSchema: {
      workflowId: z.string().describe('Workflow ID'),
      limit: z.number().optional().default(20),
      eventTypes: z.array(z.string()).optional(),
      since: z.string().optional().describe('ISO date'),
    },
  },
  async (params) => { /* implementation */ }
);
```

**Example Output:**
```
📜 Timeline: wf_abc123
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📅 2026-01-03
  14:30 ✅ task.completed: JWT validation
  14:25 📸 checkpoint.created: manual
  13:00 🔄 task.started: JWT validation

📅 2026-01-02
  16:45 ✅ task.completed: User model setup
  10:00 🚀 workflow.started
  09:30 📋 workflow.created
```

---

## Artifact Linking Tools

### 13. link_artifact

```typescript
server.registerTool(
  'link_artifact',
  {
    title: 'Link Artifact',
    description: 'Link a note as an artifact to a workflow or task',
    inputSchema: {
      noteId: z.string().describe('Note ID to link'),
      workflowId: z.string().optional(),
      taskId: z.string().optional(),
      role: z.enum(['definition', 'reference', 'output', 'decision', 'learning']).optional(),
    },
  },
  async (params) => { /* implementation */ }
);
```

---

## Complete Tool Summary

```
┌─────────────────────────────────────────────────────────────────┐
│           Magic-Note MCP Tools (v2.0)                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  📝 NOTE MANAGEMENT (기존 10개 - 변경 없음)                      │
│  list_notes, get_note, add_note, update_note, delete_note       │
│  upsert_insight, list_templates, use_template                   │
│  list_projects, list_tags                                       │
│                                                                 │
│  📁 WORKFLOW MANAGEMENT (6개 - 신규)                            │
│  create_workflow    | 워크플로우 생성                           │
│  get_workflow       | 워크플로우 조회                           │
│  list_workflows     | 워크플로우 목록                           │
│  update_workflow    | 워크플로우 수정                           │
│  delete_workflow    | 워크플로우 삭제                           │
│  archive_workflow   | 워크플로우 아카이브                       │
│                                                                 │
│  ✅ TASK MANAGEMENT (6개 - 신규)                                │
│  add_task           | 태스크 추가                               │
│  update_task        | 태스크 수정                               │
│  remove_task        | 태스크 제거                               │
│  reorder_tasks      | 태스크 순서 변경                          │
│  set_task_status    | 태스크 상태 변경 ⭐                       │
│  delegate_task      | 태스크 위임                               │
│                                                                 │
│  📸 CHECKPOINT MANAGEMENT (3개 - 신규)                          │
│  create_checkpoint  | 체크포인트 생성                           │
│  list_checkpoints   | 체크포인트 목록                           │
│  restore_checkpoint | 체크포인트 복원                           │
│                                                                 │
│  🔗 ARTIFACT LINKING (2개 - 신규)                               │
│  link_artifact      | 아티팩트 연결                             │
│  unlink_artifact    | 아티팩트 연결 해제                        │
│                                                                 │
│  📊 QUERY & INSIGHTS (3개 - 신규)                               │
│  get_workflow_status| 현황 요약 ⭐                              │
│  resume_workflow    | 재개 정보 ⭐                              │
│  get_timeline       | 이벤트 타임라인                           │
│                                                                 │
│  TOTAL: 30 tools (기존 10 + 신규 20)                            │
└─────────────────────────────────────────────────────────────────┘
```

---

## Helper Functions Required

```typescript
// Progress bar builder
function buildProgressBar(percent: number): string {
  const filled = Math.round(percent / 6.25);
  const empty = 16 - filled;
  return '█'.repeat(filled) + '░'.repeat(empty);
}

// Relative time formatter
function formatRelativeTime(isoDate: string): string {
  const diff = Date.now() - new Date(isoDate).getTime();
  const minutes = Math.floor(diff / 60000);
  const hours = Math.floor(diff / 3600000);
  const days = Math.floor(diff / 86400000);

  if (days > 0) return `${days} day${days > 1 ? 's' : ''} ago`;
  if (hours > 0) return `${hours} hour${hours > 1 ? 's' : ''} ago`;
  if (minutes > 0) return `${minutes} minute${minutes > 1 ? 's' : ''} ago`;
  return 'just now';
}

// Event emoji mapper
function getEventEmoji(eventType: string): string {
  const map: Record<string, string> = {
    'workflow.created': '📋',
    'workflow.started': '🚀',
    'workflow.completed': '🎉',
    'task.added': '➕',
    'task.started': '🔄',
    'task.completed': '✅',
    'task.blocked': '❌',
    'checkpoint.created': '📸',
  };
  return map[eventType] || '•';
}

// Status emoji mapper
function getStatusEmoji(status: TaskStatus): string {
  const map: Record<TaskStatus, string> = {
    'pending': '⬜',
    'ready': '⏳',
    'in_progress': '🔄',
    'blocked': '❌',
    'completed': '✅',
    'skipped': '⏭️',
  };
  return map[status];
}

// Event summary formatter
function formatEventSummary(event: WorkflowEvent): string {
  const { type, payload } = event;
  switch (type) {
    case 'task.completed':
      return `Completed: ${payload.title || payload.taskId}`;
    case 'task.started':
      return `Started: ${payload.title || payload.taskId}`;
    case 'checkpoint.created':
      return `Checkpoint: ${payload.trigger}`;
    default:
      return type.split('.').join(': ');
  }
}
```

---

## Integration with Hooks

### SessionStart Hook Enhancement

```typescript
// hooks/hooks.json 에 추가
{
  "event": "SessionStart",
  "action": "auto-resume",
  "script": "Resume active workflow for current workspace"
}

// 실행 로직
async function onSessionStart(workspace: string) {
  const activeWorkflow = await findActiveWorkflow(workspace);
  if (activeWorkflow) {
    const resumeInfo = await getResumeInfo(activeWorkflow.id);
    console.log(formatResumeMessage(resumeInfo));
  }
}
```

### SessionEnd Hook Enhancement

```typescript
// 자동 체크포인트 생성
async function onSessionEnd(workspace: string) {
  const activeWorkflow = await findActiveWorkflow(workspace);
  if (activeWorkflow) {
    await createCheckpoint({
      workflowId: activeWorkflow.id,
      trigger: 'session_end',
      summary: await generateSessionSummary(),
    });
  }
}
```

---

## Key Insights

- **`resume_workflow`**가 "어디까지 했지?" 문제의 직접적인 해결책
- **`set_task_status`**가 가장 빈번한 작업 - 간결하고 빠르게 설계
- **Event Sourcing은 암묵적** - 모든 도구가 자동으로 이벤트 기록

---

## Related Documents

- [01-workflow-evolution-spec.md](./01-workflow-evolution-spec.md) - 전문가 패널 토론
- [02-domain-model-design.md](./02-domain-model-design.md) - 도메인 모델 설계
