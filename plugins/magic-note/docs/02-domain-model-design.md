# Domain Model Design: Magic-Note Workflow Evolution

> **Design Date**: 2026-01-03
> **Last Updated**: 2026-01-03 (Competitive Patterns Integrated)
> **Status**: Implementation Ready
> **Approach**: Hybrid (Separation Model + Event Sourcing)
> **Implementation**: [types.ts](../src/core/types.ts)

---

## Design Principles

1. **Workflow가 Aggregate Root** - Task 조작은 항상 Workflow 컨텍스트에서
2. **Note는 First-class Citizen 유지** - 기존 호환성 + Artifact로 참조 가능
3. **Event Sourcing (Lightweight)** - JSONL append로 모든 변경 추적
4. **점진적 마이그레이션** - 기존 데이터 100% 보호
5. **Quality Gates** - Confidence → Verification → Review 3단계 검증

---

## Integrated Competitive Patterns

경쟁 분석([04-competitive-analysis.md](./04-competitive-analysis.md))에서 발견한 7가지 패턴이 도메인 모델에 통합되었습니다:

| 패턴 | 출처 | 통합 위치 | 설명 |
|------|------|----------|------|
| **Confidence Checker** | SuperClaude_Framework | `TaskConfidence` | 태스크 시작 전 0.0-1.0 신뢰도 검증 |
| **Bite-Sized Tasks** | superpowers | `TaskStep` | 2-5분 단위 atomic step 분해 |
| **Memory Schema** | SuperClaude_Plugin | `MemoryEntry`, `Checkpoint.sessionContext` | Plan→Phase→Task→Todo 계층 메모리 |
| **Reflexion Pattern** | SuperClaude_Framework | `NoteType: 'mistake'`, `MistakeNoteContent` | 오류 학습 및 패턴 매칭 |
| **Verification Gate** | superpowers | `TaskCompletionGate`, `VerificationGate` | "증거 후 주장" 검증 게이트 |
| **Two-Stage Review** | superpowers | `TaskReview` | Spec Compliance → Code Quality 순서 |
| **Batch Execution** | superpowers | `BatchExecutionConfig`, `BatchExecution` | 3개 단위 배치 + 체크포인트 |

---

## Model Options Evaluated

### Option A: Evolutionary Model (점진적 진화)

```
기존 Note를 확장하여 Workflow 개념을 포함

┌─────────────────────────────────────────────────────────┐
│                      Note (확장)                         │
├─────────────────────────────────────────────────────────┤
│  id: string                                             │
│  type: 'prompt' | 'plan' | 'choice' | 'insight'         │
│        | 'workflow' | 'task'  ← NEW                     │
│  title: string                                          │
│  content: string                                        │
│  tags: string[]                                         │
│  project: string                                        │
│  ─────────────────────────────────────────────────────  │
│  // NEW: Workflow Extensions                            │
│  parentId?: string        // task → workflow 관계       │
│  status?: 'draft'|'active'|'completed'|'blocked'        │
│  dependencies?: string[]  // task 간 의존성             │
│  order?: number           // 순서                       │
│  assignee?: 'human'|'agent'                             │
└─────────────────────────────────────────────────────────┘

장점: 기존 데이터/API 호환, 점진적 마이그레이션
단점: Note 엔티티 비대화, 책임 혼재
```

### Option B: Separation Model (명확한 분리) ✅ Selected

```
Workflow와 Note를 별개의 Aggregate로 분리

┌─────────────────────┐      ┌─────────────────────┐
│     Workflow        │      │       Note          │
├─────────────────────┤      ├─────────────────────┤
│ id: string          │      │ id: string          │
│ name: string        │      │ type: NoteType      │
│ status: WfStatus    │      │ title: string       │
│ workspace: string   │      │ content: string     │
│ createdAt: Date     │      │ tags: string[]      │
│ updatedAt: Date     │      │ project: string     │
└─────────────────────┘      └─────────────────────┘
         │                            ▲
         │ 1:N                        │
         ▼                            │
┌─────────────────────┐               │
│       Task          │               │
├─────────────────────┤      references (N:M)
│ id: string          │───────────────┘
│ workflowId: string  │
│ title: string       │
│ status: TaskStatus  │
│ dependencies: []    │
│ artifacts: []       │  // Note IDs
│ order: number       │
└─────────────────────┘

장점: 명확한 책임 분리, 확장성
단점: 복잡도 증가, API 변경 필요
```

### Option C: Event-Sourced Model (이벤트 중심)

```
모든 것을 Event Stream으로 통합

┌─────────────────────────────────────────────────────────┐
│                    Event Store                          │
├─────────────────────────────────────────────────────────┤
│  WorkflowCreated { id, name, workspace }                │
│  TaskAdded { workflowId, taskId, title }                │
│  TaskStatusChanged { taskId, from, to, reason }         │
│  NoteAttached { taskId, noteId, role }                  │
│  CheckpointCreated { workflowId, snapshot }             │
│  InsightCaptured { workflowId, content }                │
│  DecisionRecorded { workflowId, decision, rationale }   │
└─────────────────────────────────────────────────────────┘
                        │
                        ▼ Projection
┌─────────────────────────────────────────────────────────┐
│              Current State (Read Model)                 │
├─────────────────────────────────────────────────────────┤
│  workflows/                                             │
│  ├── {workflowId}/                                      │
│  │   ├── state.json      // 현재 상태                   │
│  │   ├── tasks.json      // 태스크 목록                 │
│  │   └── timeline.json   // 이벤트 타임라인             │
│  notes/                  // 기존 노트 (독립 유지)       │
│  events/                 // 이벤트 로그                 │
└─────────────────────────────────────────────────────────┘

장점: 완벽한 히스토리, 시간 여행, 복구 용이
단점: 구현 복잡도, 학습 곡선
```

### Final Decision: Hybrid (Option B + Option C Event Log)

- **Option B**를 기반 구조로 선택 (명확한 책임 분리)
- **Option C**의 이벤트 로깅을 추가 (히스토리 추적)

---

## Core Type Definitions

```typescript
// ═══════════════════════════════════════════════════════
// WORKFLOW AGGREGATE
// ═══════════════════════════════════════════════════════

interface Workflow {
  id: string;
  name: string;
  description?: string;
  workspace: string;           // 프로젝트/컨텍스트
  status: WorkflowStatus;

  // Metadata
  createdAt: string;
  updatedAt: string;

  // Relations (IDs only - lazy loading)
  taskIds: string[];
  artifactIds: string[];       // Note references

  // State
  currentPhase?: string;
  activeTaskId?: string;

  // Statistics (denormalized for quick access)
  stats: {
    totalTasks: number;
    completedTasks: number;
    blockedTasks: number;
  };
}

type WorkflowStatus =
  | 'draft'      // 계획 중
  | 'active'     // 진행 중
  | 'paused'     // 일시 중단
  | 'blocked'    // 블로커로 중단
  | 'completed'  // 완료
  | 'archived';  // 보관

// ═══════════════════════════════════════════════════════
// TASK ENTITY
// ═══════════════════════════════════════════════════════

interface Task {
  id: string;
  workflowId: string;

  // Content
  title: string;
  description?: string;

  // Status
  status: TaskStatus;
  priority: 'low' | 'medium' | 'high' | 'critical';

  // Relationships
  dependencies: string[];      // 선행 task IDs
  blockedBy?: string[];        // 블로커 (외부 요인)
  artifactIds: string[];       // 관련 Note IDs

  // Ordering
  phase?: string;              // "Phase 1: Setup"
  order: number;

  // Assignment
  assignee?: 'human' | 'agent';
  agentType?: string;          // 'code-reviewer', 'plan-reviewer' 등

  // Timestamps
  createdAt: string;
  startedAt?: string;
  completedAt?: string;

  // Notes
  notes?: string;              // 인라인 메모
}

type TaskStatus =
  | 'pending'      // ⬜ 대기
  | 'ready'        // ⏳ 시작 가능 (의존성 충족)
  | 'in_progress'  // 🔄 진행 중
  | 'blocked'      // ❌ 블로커
  | 'completed'    // ✅ 완료
  | 'skipped';     // ⏭️ 건너뜀

// ═══════════════════════════════════════════════════════
// NOTE (기존 유지 + 확장)
// ═══════════════════════════════════════════════════════

interface Note extends NoteMeta {
  content: string;

  // NEW: Workflow Integration (optional - backward compatible)
  linkedWorkflows?: string[];  // 연결된 workflow IDs
  linkedTasks?: string[];      // 연결된 task IDs
  role?: ArtifactRole;         // workflow 내 역할
}

type NoteType = 'prompt' | 'plan' | 'choice' | 'insight';

type ArtifactRole =
  | 'definition'    // workflow 정의 문서
  | 'reference'     // 참조 자료
  | 'output'        // 산출물
  | 'decision'      // 의사결정 기록
  | 'learning';     // 학습 내용

// ═══════════════════════════════════════════════════════
// EVENT LOG (Event Sourcing)
// ═══════════════════════════════════════════════════════

interface WorkflowEvent {
  id: string;
  timestamp: string;
  workflowId: string;
  type: WorkflowEventType;
  payload: Record<string, unknown>;

  // Context
  sessionId?: string;
  triggeredBy: 'user' | 'agent' | 'system' | 'hook';
}

type WorkflowEventType =
  // Workflow Lifecycle
  | 'workflow.created'
  | 'workflow.started'
  | 'workflow.paused'
  | 'workflow.resumed'
  | 'workflow.completed'
  | 'workflow.archived'

  // Task Operations
  | 'task.added'
  | 'task.updated'
  | 'task.started'
  | 'task.completed'
  | 'task.blocked'
  | 'task.unblocked'
  | 'task.skipped'
  | 'task.delegated'

  // Artifacts
  | 'artifact.attached'
  | 'artifact.detached'

  // Checkpoints
  | 'checkpoint.created'
  | 'checkpoint.restored'

  // Insights
  | 'insight.captured'
  | 'decision.recorded';

// ═══════════════════════════════════════════════════════
// CHECKPOINT (상태 스냅샷)
// ═══════════════════════════════════════════════════════

interface Checkpoint {
  id: string;
  workflowId: string;
  timestamp: string;

  // Trigger
  trigger: 'auto' | 'manual' | 'milestone' | 'session_end';

  // State Snapshot
  snapshot: {
    workflowStatus: WorkflowStatus;
    taskStatuses: Record<string, TaskStatus>;
    activeTaskId?: string;
    currentPhase?: string;
  };

  // Context
  summary?: string;            // "JWT 구현 완료, 리프레시 토큰 진행 중"
  lastActivity?: string;       // 마지막 작업 설명

  // Session Info
  sessionId?: string;
}
```

---

## Entity Relationships Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        WORKSPACE                                 │
│  (프로젝트 컨텍스트 - 예: "my-app", "auth-service")              │
└─────────────────────────────────────────────────────────────────┘
         │
         │ contains (1:N)
         ▼
┌─────────────────────────────────────────────────────────────────┐
│                        WORKFLOW                                  │
│  "Authentication Implementation"                                 │
│  status: active, progress: 53%                                   │
└─────────────────────────────────────────────────────────────────┘
         │                              │
         │ has (1:N)                    │ references (N:M)
         ▼                              ▼
┌─────────────────────┐        ┌─────────────────────┐
│       TASK          │        │       NOTE          │
│ "Implement JWT"     │◄──────►│ "Auth Design Doc"   │
│ status: completed   │ linked │ type: plan          │
│ dependencies: [T1]  │        │ role: definition    │
└─────────────────────┘        └─────────────────────┘
         │
         │ logged by (1:N)
         ▼
┌─────────────────────────────────────────────────────────────────┐
│                      EVENT LOG                                   │
│  [task.started] → [task.completed] → [checkpoint.created]        │
└─────────────────────────────────────────────────────────────────┘
         │
         │ produces (N:1)
         ▼
┌─────────────────────────────────────────────────────────────────┐
│                      CHECKPOINT                                  │
│  "Session 2024-01-15: JWT 구현 완료"                             │
│  snapshot: { tasks: {...}, activeTask: "T3" }                    │
└─────────────────────────────────────────────────────────────────┘
```

---

## Storage Structure

```
~/.magic-note/
├── config.yaml
├── index.json                    # 빠른 조회용 인덱스
│
├── notes/                        # 기존 노트 (변경 없음)
│   ├── {note_id}.md
│   └── ...
│
├── workflows/                    # NEW: 워크플로우
│   ├── index.json               # 워크플로우 목록
│   └── {workflow_id}/
│       ├── workflow.json        # 워크플로우 메타데이터
│       ├── tasks.json           # 태스크 목록
│       ├── events.jsonl         # 이벤트 로그 (append-only)
│       └── checkpoints/
│           └── {checkpoint_id}.json
│
├── workspaces/                   # NEW: 워크스페이스 (프로젝트 그룹)
│   └── {workspace_name}/
│       ├── meta.json
│       └── workflow_refs.json   # 연결된 워크플로우 ID 목록
│
└── templates/                    # 기존 템플릿
    └── ...
```

---

## Migration Strategy

### Phase 1: Additive (v1.1)

- `workflows/` 디렉토리 추가
- 기존 `notes/` 100% 유지
- Note에 optional 필드만 추가 (linkedWorkflows)
- 새 MCP 도구 추가: create_workflow, add_task, etc.

### Phase 2: Integration (v1.2)

- 기존 'plan' 노트를 workflow로 자동 변환 옵션
- plan-reviewer가 workflow aware하게 업그레이드
- Event logging 시작

### Phase 3: Full Workflow (v2.0)

- Workflow-first 인터페이스
- Note는 artifact로 통합 관리
- 완전한 Event Sourcing

---

## Extended Type Definitions (types.ts)

> **Note**: 전체 타입 정의는 [types.ts](../src/core/types.ts)에서 확인할 수 있습니다.

### Core Types (Backward Compatible)

```typescript
// NoteType - 'mistake' 추가 (Reflexion Pattern)
export type NoteType = 'prompt' | 'plan' | 'choice' | 'insight' | 'mistake';

// Workflow 상태 라이프사이클
export type WorkflowStatus =
  | 'draft' | 'ready' | 'active' | 'paused'
  | 'blocked' | 'completed' | 'failed' | 'cancelled';

// Task 상태 - Verification Gate 지원
export type TaskStatus =
  | 'pending' | 'in_progress' | 'verifying' | 'review'
  | 'completed' | 'failed' | 'skipped' | 'blocked';
```

### Confidence Checker Pattern

```typescript
interface ConfidenceDimension {
  dimension: string;      // 'understanding', 'approach', 'risks'
  score: number;          // 0.0 - 1.0
  evidence: string;
  blockers?: string[];
}

interface TaskConfidence {
  overall: number;                    // 가중 평균
  dimensions: ConfidenceDimension[];
  threshold: number;                  // 기본값: 0.7
  passed: boolean;                    // overall >= threshold
  checkedAt: string;
  recommendation?: 'proceed' | 'clarify' | 'research' | 'defer';
}
```

### Bite-Sized Tasks Pattern

```typescript
interface TaskStep {
  id: string;
  description: string;
  estimatedMinutes: number;           // 2-5분 이상적
  verificationCommand?: string;
  completed: boolean;
  completedAt?: string;
  evidence?: string;
}
```

### Verification Gate Pattern

```typescript
interface VerificationGate {
  command: string;
  expectedOutput?: string;
  exitCode?: number;
  timeout?: number;
}

interface TaskCompletionGate {
  verificationRequired: boolean;
  verifications: VerificationGate[];
  lastVerifiedAt?: string;
  lastVerificationResult?: {
    passed: boolean;
    output: string;
    exitCode: number;
    duration: number;
  };
}
```

### Two-Stage Review Pattern

```typescript
type ReviewType = 'spec_compliance' | 'code_quality';
type ReviewResult = 'approved' | 'needs_changes' | 'rejected';

interface TaskReview {
  type: ReviewType;
  result: ReviewResult;
  reviewer?: string;
  feedback?: string;
  issues?: string[];
  reviewedAt: string;
  iteration: number;
}
```

### Enhanced Task (All Patterns Integrated)

```typescript
interface Task {
  id: string;
  workflowId: string;
  title: string;
  description: string;
  priority: TaskPriority;
  status: TaskStatus;
  order: number;
  dependsOn?: string[];

  // Confidence Checker Pattern
  confidence?: TaskConfidence;

  // Bite-Sized Tasks Pattern
  steps?: TaskStep[];
  estimatedMinutes?: number;
  actualMinutes?: number;

  // Verification Gate Pattern
  completionGate?: TaskCompletionGate;

  // Two-Stage Review Pattern
  reviews?: TaskReview[];
  reviewRequired?: boolean;

  // Artifact references
  noteIds?: string[];
  files?: string[];

  // Timing
  startedAt?: string;
  completedAt?: string;
  tags?: string[];
  metadata?: Record<string, unknown>;
}
```

### Memory Schema Pattern (Enhanced Checkpoint)

```typescript
interface MemoryEntry {
  key: string;                        // 'plan_auth', 'phase_1', 'task_1.1'
  value: string;
  category: 'plan' | 'phase' | 'task' | 'todo' | 'checkpoint' | 'decision' | 'blocker';
  createdAt: string;
  updatedAt: string;
}

interface Checkpoint {
  id: string;
  workflowId: string;
  currentTaskId?: string;
  taskStatuses: Record<string, TaskStatus>;
  completedSteps: string[];

  // Memory Schema integration
  memoryEntries: MemoryEntry[];
  sessionContext?: {
    goal: string;
    currentPhase: string;
    blockers: string[];
    decisions: string[];
    nextActions: string[];
  };

  notes?: string;
  pendingActions?: string[];
  createdAt: string;
  reason?: 'manual' | 'auto' | 'session_end' | 'phase_complete';
}
```

### Batch Execution Pattern

```typescript
interface BatchExecutionConfig {
  batchSize: number;                  // 기본: 3
  checkpointAfterBatch: boolean;
  parallelExecution: boolean;
  stopOnFailure: boolean;
}

interface BatchExecution {
  batchNumber: number;
  taskIds: string[];
  startedAt: string;
  completedAt?: string;
  status: 'running' | 'completed' | 'failed' | 'partial';
  results: Record<string, TaskStatus>;
}
```

### Reflexion Pattern

```typescript
interface ErrorSignature {
  errorType: string;
  errorMessage: string;
  context?: string;
}

interface MistakeNoteContent {
  errorSignature: ErrorSignature;
  whatHappened: string;
  rootCause: string;
  whyMissed?: string;
  fixApplied: string;
  preventionChecklist?: string[];
  lessonLearned: string;
  taskId?: string;
  workflowId?: string;
}
```

---

## Design Decision Summary

| 결정 항목 | 선택 | 근거 |
|----------|------|------|
| **기본 구조** | Option B (Separation) + Event Log | 명확한 책임 분리 + 히스토리 추적 |
| **Note 관계** | First-class → Artifact 참조 | 기존 호환성 유지하면서 통합 |
| **Storage** | File-based (workflows/ 추가) | MCP 서버 단순성 유지 |
| **Event Sourcing** | Lightweight (JSONL append) | 복잡도와 가치의 균형 |
| **마이그레이션** | 3-Phase Additive | 기존 데이터 100% 보호 |
| **Quality Gates** | Confidence → Verification → Review | 경쟁 분석에서 검증된 패턴 |
| **Task Granularity** | 2-5분 Bite-Sized Steps | superpowers 검증 결과 |
| **Error Learning** | Reflexion Pattern + 'mistake' NoteType | 오류 재발 방지 |

---

## Key Insights

- **Workflow-Task-Note** 3계층 구조가 "계획-실행-기록" 사이클을 자연스럽게 표현
- **Event Log**는 "시간 여행" 가능하게 하여 "왜 이렇게 됐지?" 질문에 완벽히 대응
- **Checkpoint + Memory Schema**는 세션 간 연속성의 핵심 - 복잡한 상태를 단일 스냅샷으로 압축
- **Confidence Checker**는 "시작하기 전에 확인" - 실패 비용을 줄이는 선제적 검증
- **Verification Gate**는 "증거 후 주장" - 완료 주장 전 실제 검증 필수
- **Bite-Sized Tasks**는 "2-5분 단위" - 진행률 추적과 세션 중단 대응력 향상
- **Reflexion Pattern**은 "실수로부터 학습" - 동일 오류 재발 방지

---

## Quality Gate Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    TASK EXECUTION FLOW                          │
└─────────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────┐
│  1. CONFIDENCE      │  ← TaskConfidence (0.0-1.0)
│     CHECK           │  ← threshold: 0.7
│  "시작해도 될까?"    │  ← recommendation: proceed/clarify/research/defer
└─────────────────────┘
         │ passed = true
         ▼
┌─────────────────────┐
│  2. STEP BY STEP    │  ← TaskStep[] (2-5분 단위)
│     EXECUTION       │  ← verificationCommand per step
│  "작은 단위로 진행"  │  ← evidence 수집
└─────────────────────┘
         │
         ▼
┌─────────────────────┐
│  3. VERIFICATION    │  ← TaskCompletionGate
│     GATE            │  ← VerificationGate[]
│  "증거 후 주장"      │  ← 명령 실행 → 결과 기록
└─────────────────────┘
         │ passed = true
         ▼
┌─────────────────────┐
│  4A. SPEC REVIEW    │  ← TaskReview (type: spec_compliance)
│  "스펙 준수 확인"    │  ← iteration: 1, 2, 3...
└─────────────────────┘
         │ approved
         ▼
┌─────────────────────┐
│  4B. QUALITY REVIEW │  ← TaskReview (type: code_quality)
│  "품질 확인"         │  ← iteration: 1, 2, 3...
└─────────────────────┘
         │ approved
         ▼
┌─────────────────────┐
│  5. COMPLETION      │  ← status: 'completed'
│                     │  ← completedAt: timestamp
└─────────────────────┘
         │
         ▼ (If failed at any stage)
┌─────────────────────┐
│  REFLEXION          │  ← NoteType: 'mistake'
│  "실수 기록 & 학습"  │  ← MistakeNoteContent
│                     │  ← ErrorSignature for future matching
└─────────────────────┘
```

---

## Related Documents

- [01-workflow-evolution-spec.md](./01-workflow-evolution-spec.md) - 전문가 패널 토론
- [03-mcp-tool-api-design.md](./03-mcp-tool-api-design.md) - MCP Tool API 설계
- [04-competitive-analysis.md](./04-competitive-analysis.md) - 경쟁 분석 및 차용 패턴
- [types.ts](../src/core/types.ts) - 구현된 타입 정의
