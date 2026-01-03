# Type Definitions Reference: Magic-Note Workflow

> **Generated**: 2026-01-03
> **Source**: [types.ts](../src/core/types.ts)
> **Status**: Implementation Ready

---

## Overview

Magic-Note의 타입 시스템은 두 계층으로 구성됩니다:

1. **Core Note Types** - 기존 노트 관리 (backward compatible)
2. **Workflow Types** - 새로운 워크플로우 관리 (7가지 경쟁 패턴 통합)

---

## Type Categories

```
┌─────────────────────────────────────────────────────────────────┐
│                      TYPES HIERARCHY                             │
└─────────────────────────────────────────────────────────────────┘

CORE NOTE LAYER (Backward Compatible)
├── NoteType: 'prompt' | 'plan' | 'choice' | 'insight' | 'mistake'
├── Note, NoteMeta, CreateNoteInput, UpdateNoteInput
├── Template, Project, NoteFilter
└── StoragePaths (extended with workflows/, workspaces/)

WORKFLOW LAYER (New)
├── Status Types
│   ├── WorkflowStatus (8 states)
│   └── TaskStatus (8 states with verification support)
│
├── Quality Gate Types (Competitive Patterns)
│   ├── Confidence Checker: TaskConfidence, ConfidenceDimension
│   ├── Bite-Sized Tasks: TaskStep
│   ├── Verification Gate: VerificationGate, TaskCompletionGate
│   └── Two-Stage Review: TaskReview, ReviewType, ReviewResult
│
├── Core Entities
│   ├── Workflow (Aggregate Root)
│   ├── Task (with all patterns integrated)
│   └── Checkpoint (Memory Schema enhanced)
│
├── Event Sourcing
│   ├── WorkflowEvent
│   └── WorkflowEventType (20 event types)
│
├── Execution Patterns
│   ├── BatchExecutionConfig
│   └── BatchExecution
│
└── Reflexion Pattern
    ├── ErrorSignature
    ├── LearnedSolution
    └── MistakeNoteContent
```

---

## Status Types

### WorkflowStatus

워크플로우 전체 라이프사이클을 나타냅니다.

```typescript
type WorkflowStatus =
  | 'draft'       // 초기 계획 단계
  | 'ready'       // 모든 태스크 정의 완료, 실행 준비
  | 'active'      // 현재 실행 중
  | 'paused'      // 일시 중단
  | 'blocked'     // 외부 의존성 대기
  | 'completed'   // 성공적 완료
  | 'failed'      // 오류로 종료
  | 'cancelled';  // 수동 취소
```

**State Transitions:**
```
draft → ready → active → completed
                  ↓
              paused ⟷ active
                  ↓
              blocked → active
                  ↓
              failed / cancelled
```

### TaskStatus

태스크 실행 상태를 나타내며, Verification Gate 패턴을 지원합니다.

```typescript
type TaskStatus =
  | 'pending'       // 시작 전
  | 'in_progress'   // 작업 중
  | 'verifying'     // 검증 실행 중 (Verification Gate)
  | 'review'        // 리뷰 대기 (Two-Stage Review)
  | 'completed'     // 완료 및 검증됨
  | 'failed'        // 검증 또는 실행 실패
  | 'skipped'       // 의도적으로 건너뜀
  | 'blocked';      // 의존성 대기
```

---

## Quality Gate Types

### 1. Confidence Checker Pattern

태스크 시작 전 신뢰도를 점수화하여 "시작해도 될까?"를 판단합니다.

```typescript
interface ConfidenceDimension {
  dimension: string;      // 예: 'understanding', 'approach', 'risks'
  score: number;          // 0.0 (무신뢰) ~ 1.0 (완전 신뢰)
  evidence: string;       // 점수 근거
  blockers?: string[];    // 높은 점수를 막는 요인
}

interface TaskConfidence {
  overall: number;                    // 가중 평균 (0.0-1.0)
  dimensions: ConfidenceDimension[];
  threshold: number;                  // 최소 요구치 (기본: 0.7)
  passed: boolean;                    // overall >= threshold
  checkedAt: string;                  // ISO 8601
  recommendation?: 'proceed' | 'clarify' | 'research' | 'defer';
}
```

**Usage Example:**
```typescript
const confidence: TaskConfidence = {
  overall: 0.85,
  dimensions: [
    { dimension: 'understanding', score: 0.9, evidence: 'Requirements clear' },
    { dimension: 'approach', score: 0.8, evidence: 'Similar pattern exists' },
    { dimension: 'risks', score: 0.85, evidence: 'Edge cases identified' }
  ],
  threshold: 0.7,
  passed: true,
  checkedAt: '2026-01-03T10:00:00Z',
  recommendation: 'proceed'
};
```

### 2. Bite-Sized Tasks Pattern

태스크를 2-5분 단위의 atomic step으로 분해합니다.

```typescript
interface TaskStep {
  id: string;
  description: string;
  estimatedMinutes: number;           // 이상적: 2-5분
  verificationCommand?: string;       // 완료 검증 명령
  completed: boolean;
  completedAt?: string;               // ISO 8601
  evidence?: string;                  // 완료 증거
}
```

**Usage Example:**
```typescript
const steps: TaskStep[] = [
  {
    id: 'step-1',
    description: 'Create user model interface',
    estimatedMinutes: 3,
    verificationCommand: 'grep "interface User" src/models/user.ts',
    completed: false
  },
  {
    id: 'step-2',
    description: 'Implement validation logic',
    estimatedMinutes: 5,
    verificationCommand: 'npm test -- --grep "User validation"',
    completed: false
  }
];
```

### 3. Verification Gate Pattern

"증거 후 주장" - 완료를 선언하기 전에 검증을 실행합니다.

```typescript
interface VerificationGate {
  command: string;                    // 실행할 명령
  expectedOutput?: string;            // 성공 출력 패턴
  exitCode?: number;                  // 예상 종료 코드 (기본: 0)
  timeout?: number;                   // 타임아웃 (초)
}

interface TaskCompletionGate {
  verificationRequired: boolean;
  verifications: VerificationGate[];
  lastVerifiedAt?: string;            // ISO 8601
  lastVerificationResult?: {
    passed: boolean;
    output: string;
    exitCode: number;
    duration: number;                 // 밀리초
  };
}
```

**Usage Example:**
```typescript
const completionGate: TaskCompletionGate = {
  verificationRequired: true,
  verifications: [
    {
      command: 'npm test',
      expectedOutput: 'All tests passed',
      exitCode: 0,
      timeout: 60
    },
    {
      command: 'npm run lint',
      exitCode: 0,
      timeout: 30
    }
  ]
};
```

### 4. Two-Stage Review Pattern

Spec Compliance → Code Quality 순서로 리뷰를 진행합니다.

```typescript
type ReviewType = 'spec_compliance' | 'code_quality';
type ReviewResult = 'approved' | 'needs_changes' | 'rejected';

interface TaskReview {
  type: ReviewType;
  result: ReviewResult;
  reviewer?: string;                  // 에이전트 또는 사람 식별자
  feedback?: string;
  issues?: string[];
  reviewedAt: string;                 // ISO 8601
  iteration: number;                  // 리뷰 라운드 (1, 2, 3...)
}
```

**Usage Example:**
```typescript
const reviews: TaskReview[] = [
  {
    type: 'spec_compliance',
    result: 'needs_changes',
    reviewer: 'spec-reviewer-agent',
    issues: ['Missing error handling for edge case'],
    reviewedAt: '2026-01-03T10:30:00Z',
    iteration: 1
  },
  {
    type: 'spec_compliance',
    result: 'approved',
    reviewer: 'spec-reviewer-agent',
    feedback: 'All requirements met',
    reviewedAt: '2026-01-03T11:00:00Z',
    iteration: 2
  },
  {
    type: 'code_quality',
    result: 'approved',
    reviewer: 'code-quality-agent',
    feedback: 'Clean code, good test coverage',
    reviewedAt: '2026-01-03T11:15:00Z',
    iteration: 1
  }
];
```

---

## Core Entities

### Task

모든 Quality Gate 패턴이 통합된 태스크 엔티티입니다.

```typescript
interface Task {
  id: string;
  workflowId: string;

  // 기본 정보
  title: string;
  description: string;
  priority: TaskPriority;
  status: TaskStatus;

  // 순서 및 의존성
  order: number;
  dependsOn?: string[];               // 의존하는 태스크 IDs

  // Confidence Checker Pattern
  confidence?: TaskConfidence;

  // Bite-Sized Tasks Pattern
  steps?: TaskStep[];
  estimatedMinutes?: number;          // 총 예상 시간
  actualMinutes?: number;             // 실제 소요 시간

  // Verification Gate Pattern
  completionGate?: TaskCompletionGate;

  // Two-Stage Review Pattern
  reviews?: TaskReview[];
  reviewRequired?: boolean;

  // 아티팩트 참조
  noteIds?: string[];                 // 관련 노트
  files?: string[];                   // 관련 파일 경로

  // 타이밍
  startedAt?: string;
  completedAt?: string;

  // 메타데이터
  tags?: string[];
  metadata?: Record<string, unknown>;
}
```

### Workflow

태스크 관리의 Aggregate Root입니다.

```typescript
interface Workflow {
  id: string;

  // 기본 정보
  title: string;
  description?: string;
  status: WorkflowStatus;

  // 계층
  project: string;
  parentWorkflowId?: string;          // 하위 워크플로우용

  // 태스크
  tasks: Task[];

  // 실행 설정
  executionConfig?: BatchExecutionConfig;
  currentBatch?: BatchExecution;

  // 체크포인트
  checkpoints: Checkpoint[];
  autoCheckpointInterval?: number;    // 자동 체크포인트 간격 (분)

  // 노트 참조
  planNoteId?: string;                // 원본 계획 노트
  relatedNoteIds?: string[];

  // 진행률 추적
  progress: {
    total: number;
    completed: number;
    failed: number;
    percentage: number;
  };

  // 타이밍
  createdAt: string;
  updatedAt: string;
  startedAt?: string;
  completedAt?: string;
  estimatedCompletion?: string;

  // 메타데이터
  tags?: string[];
  metadata?: Record<string, unknown>;
}
```

### Checkpoint (Memory Schema Enhanced)

세션 연속성을 위한 상태 스냅샷입니다. Memory Schema 패턴이 통합되어 있습니다.

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

  // 상태 스냅샷
  currentTaskId?: string;
  taskStatuses: Record<string, TaskStatus>;
  completedSteps: string[];           // 완료된 Step IDs

  // Memory Schema 통합
  memoryEntries: MemoryEntry[];
  sessionContext?: {
    goal: string;                     // 현재 목표
    currentPhase: string;             // 현재 단계
    blockers: string[];               // 블로커 목록
    decisions: string[];              // 의사결정 기록
    nextActions: string[];            // 다음 액션
  };

  // 컨텍스트 보존
  notes?: string;                     // 사람이 읽을 수 있는 요약
  pendingActions?: string[];

  // 타이밍
  createdAt: string;
  reason?: 'manual' | 'auto' | 'session_end' | 'phase_complete';
}
```

---

## Batch Execution Pattern

태스크를 배치 단위로 실행하고 체크포인트를 생성합니다.

```typescript
interface BatchExecutionConfig {
  batchSize: number;                  // 배치당 태스크 수 (기본: 3)
  checkpointAfterBatch: boolean;      // 배치 후 자동 체크포인트
  parallelExecution: boolean;         // 병렬 실행 가능 여부
  stopOnFailure: boolean;             // 첫 실패 시 중단
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

---

## Reflexion Pattern

과거 실수로부터 학습하여 재발을 방지합니다.

```typescript
interface ErrorSignature {
  errorType: string;
  errorMessage: string;
  context?: string;                   // 태스크/테스트 이름
}

interface LearnedSolution {
  signature: ErrorSignature;
  rootCause: string;
  solution: string;
  prevention?: string;
  learnedAt: string;
  reusedCount: number;
}

// NoteType: 'mistake'로 저장
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

## Event Sourcing

모든 변경을 이벤트로 기록하여 히스토리를 추적합니다.

```typescript
type WorkflowEventType =
  // 워크플로우 라이프사이클
  | 'workflow_created'
  | 'workflow_started'
  | 'workflow_paused'
  | 'workflow_resumed'
  | 'workflow_completed'
  | 'workflow_failed'
  | 'workflow_cancelled'
  // 태스크 작업
  | 'task_created'
  | 'task_started'
  | 'task_completed'
  | 'task_failed'
  | 'task_skipped'
  // Quality Gates
  | 'step_completed'
  | 'confidence_checked'
  | 'verification_run'
  | 'review_submitted'
  // 체크포인트 및 메모리
  | 'checkpoint_created'
  | 'memory_updated'
  // 노트 연결
  | 'note_linked'
  | 'note_unlinked';

interface WorkflowEvent {
  id: string;
  workflowId: string;
  taskId?: string;
  stepId?: string;

  type: WorkflowEventType;
  payload: Record<string, unknown>;

  timestamp: string;                  // ISO 8601
  actor?: string;                     // 트리거 주체
}
```

---

## Input/Output Types

### Creation Inputs

```typescript
interface CreateWorkflowInput {
  title: string;
  description?: string;
  project?: string;
  planNoteId?: string;
  tasks?: Omit<Task, 'id' | 'workflowId'>[];
  executionConfig?: BatchExecutionConfig;
  tags?: string[];
}

interface CreateTaskInput {
  title: string;
  description: string;
  priority?: TaskPriority;
  order?: number;
  dependsOn?: string[];
  steps?: Omit<TaskStep, 'id' | 'completed'>[];
  estimatedMinutes?: number;
  reviewRequired?: boolean;
  completionGate?: TaskCompletionGate;
  noteIds?: string[];
  files?: string[];
  tags?: string[];
}
```

### Filters

```typescript
interface WorkflowFilter {
  status?: WorkflowStatus | WorkflowStatus[];
  project?: string;
  tags?: string[];
  search?: string;
  hasIncomplete?: boolean;
  createdAfter?: string;
  createdBefore?: string;
}

interface TaskFilter {
  status?: TaskStatus | TaskStatus[];
  priority?: TaskPriority | TaskPriority[];
  hasBlockers?: boolean;
  needsReview?: boolean;
  search?: string;
}
```

---

## Status Summary

워크플로우 현재 상태를 요약합니다.

```typescript
interface WorkflowStatusSummary {
  workflow: {
    id: string;
    title: string;
    status: WorkflowStatus;
    progress: Workflow['progress'];
  };
  currentTask?: {
    id: string;
    title: string;
    status: TaskStatus;
    currentStep?: TaskStep;
  };
  recentEvents: WorkflowEvent[];
  lastCheckpoint?: Checkpoint;
  blockers: string[];
  nextActions: string[];
}
```

---

## Related Documents

- [02-domain-model-design.md](./02-domain-model-design.md) - 도메인 모델 설계
- [03-mcp-tool-api-design.md](./03-mcp-tool-api-design.md) - MCP Tool API 설계
- [04-competitive-analysis.md](./04-competitive-analysis.md) - 경쟁 분석
- [types.ts](../src/core/types.ts) - 구현 소스
