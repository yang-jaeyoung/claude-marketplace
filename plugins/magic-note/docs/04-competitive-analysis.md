# Competitive Analysis: Workflow Management Patterns

> **Analysis Date**: 2026-01-03
> **Sources**: SuperClaude_Framework, SuperClaude_Plugin, superpowers
> **Purpose**: Magic-Note 워크플로우 진화를 위한 차용 가능한 개념/기능 식별

---

## Executive Summary

3개의 유사 프로젝트 분석을 통해 Magic-Note 워크플로우 관리에 즉시 적용 가능한 **7가지 핵심 패턴**을 식별했습니다.

| 패턴 | 출처 | 적용 우선순위 | 예상 가치 |
|------|------|--------------|----------|
| **Confidence Checker** | SuperClaude_Framework | 🔴 높음 | 잘못된 방향 실행 방지 |
| **Bite-Sized Tasks** | superpowers | 🔴 높음 | 명확한 진행률 추적 |
| **Memory Schema** | SuperClaude_Plugin | 🔴 높음 | 세션 간 연속성 |
| **Reflexion Pattern** | SuperClaude_Framework | 🟡 중간 | 실수에서 학습 |
| **Verification Gate** | superpowers | 🟡 중간 | 품질 보장 |
| **Two-Stage Review** | superpowers | 🟢 향상 | 코드 품질 |
| **Batch Execution** | superpowers | 🟢 향상 | 효율적 실행 |

---

## Pattern 1: Confidence Checker (🔴 HIGH PRIORITY)

### 출처
- **파일**: `SuperClaude_Framework/src/superclaude/pm_agent/confidence.py`
- **개념**: 구현 전 신뢰도 평가로 잘못된 방향 실행 방지

### 핵심 아이디어

```
실행 전 5가지 체크 항목으로 신뢰도 점수(0.0-1.0) 계산:

1. 중복 구현 없음? (25%)      - 기존 코드 확인
2. 아키텍처 준수? (25%)       - 기존 기술 스택 사용
3. 공식 문서 확인? (20%)      - 추측 아닌 근거
4. OSS 참조 있음? (15%)       - 검증된 패턴
5. 근본 원인 식별? (15%)      - 증상 아닌 원인

신뢰도 수준:
- ≥90%: 즉시 진행
- 70-89%: 옵션 제시, 확인 후 진행
- <70%: 중단, 추가 조사 필요
```

### Magic-Note 적용 방안

```typescript
// NEW: workflow.ts에 추가

interface TaskConfidence {
  score: number;           // 0.0 - 1.0
  checks: ConfidenceCheck[];
  recommendation: 'proceed' | 'review' | 'stop';
}

interface ConfidenceCheck {
  name: string;
  passed: boolean;
  weight: number;
  message: string;
}

// Task 생성/시작 전 신뢰도 체크 옵션
async function assessTaskConfidence(task: Task): Promise<TaskConfidence> {
  const checks: ConfidenceCheck[] = [
    { name: 'dependencies_clear', weight: 0.3, passed: task.dependencies.length === 0 || await allDependenciesMet(task), message: '...' },
    { name: 'requirements_clear', weight: 0.25, passed: !!task.description, message: '...' },
    { name: 'artifacts_linked', weight: 0.2, passed: task.artifactIds.length > 0, message: '...' },
    { name: 'blockers_none', weight: 0.15, passed: !task.blockedBy?.length, message: '...' },
    { name: 'context_loaded', weight: 0.1, passed: await hasRelevantContext(task), message: '...' },
  ];

  const score = checks.reduce((sum, c) => sum + (c.passed ? c.weight : 0), 0);

  return {
    score,
    checks,
    recommendation: score >= 0.9 ? 'proceed' : score >= 0.7 ? 'review' : 'stop',
  };
}
```

### 가치

- **ROI**: 25-250x 토큰 절약 (잘못된 방향 조기 중단)
- **신뢰**: "왜 이걸 시작했지?" 질문에 근거 제공
- **품질**: 불완전한 상태로 시작하는 것 방지

---

## Pattern 2: Bite-Sized Task Granularity (🔴 HIGH PRIORITY)

### 출처
- **파일**: `superpowers/skills/writing-plans/SKILL.md`
- **개념**: 각 태스크를 2-5분 단위의 원자적 작업으로 분해

### 핵심 아이디어

```markdown
BAD (너무 크고 모호함):
- "인증 시스템 구현"

GOOD (원자적, 검증 가능):
- Step 1: 실패하는 테스트 작성 (2분)
- Step 2: 테스트 실행하여 실패 확인 (1분)
- Step 3: 최소한의 구현 작성 (3분)
- Step 4: 테스트 실행하여 통과 확인 (1분)
- Step 5: 커밋 (1분)
```

### Magic-Note 적용 방안

```typescript
// Task 타입에 granularity 메타데이터 추가

interface Task {
  // ... existing fields

  // NEW: Granularity metadata
  estimatedMinutes?: number;      // 2-5분 권장
  verificationCommand?: string;   // 검증 명령어
  expectedOutput?: string;        // 예상 출력

  // NEW: Sub-steps for complex tasks
  steps?: TaskStep[];
}

interface TaskStep {
  order: number;
  action: string;              // "Write failing test"
  command?: string;            // "pytest tests/auth.py -v"
  expectedResult?: string;     // "FAIL with 'function not defined'"
  completed: boolean;
}
```

### 가치

- **진행률**: 정확한 % 계산 가능 (모호한 "진행 중" 아님)
- **재개**: 정확히 어디서 멈췄는지 알 수 있음
- **동기부여**: 작은 성공의 연속으로 모멘텀 유지

---

## Pattern 3: Memory Schema (🔴 HIGH PRIORITY)

### 출처
- **파일**: `SuperClaude_Plugin/modes/MODE_Task_Management.md`
- **개념**: 계층적 메모리로 세션 간 연속성 보장

### 핵심 아이디어

```
계층 구조:
📋 Plan → write_memory("plan", goal_statement)
  → 🎯 Phase → write_memory("phase_X", milestone)
    → 📦 Task → write_memory("task_X.Y", deliverable)
      → ✓ Todo → write_memory("todo_X.Y.Z", status)

세션 라이프사이클:

[Session Start]
1. list_memories() → 기존 상태 표시
2. read_memory("current_plan") → 컨텍스트 재개
3. think_about_collected_information() → 위치 파악

[During Execution]
1. write_memory("task_2.1", "completed: ...")
2. Checkpoint every 30 minutes
3. TodoWrite와 병렬 업데이트

[Session End]
1. think_about_whether_you_are_done() → 완료 평가
2. write_memory("session_summary", outcomes)
3. 임시 메모리 정리
```

### Magic-Note 적용 방안

이미 우리 도메인 모델에 유사한 구조가 있음:
- `Workflow` = Plan
- `Task` with `phase` = Phase + Task
- `Checkpoint` = Memory snapshot

**추가로 차용할 것:**

```typescript
// Memory Schema 패턴을 Checkpoint에 통합

interface Checkpoint {
  // ... existing fields

  // NEW: Memory-style metadata
  memoryKeys: {
    currentPlan: string;           // "Implement JWT authentication"
    currentPhase: string;          // "Phase 2: Implementation"
    lastTask: string;              // "task_2.3: Refresh token logic"
    blockers: string[];            // ["Token revocation strategy unclear"]
    decisions: string[];           // ["Use Redis for token blacklist"]
  };

  // NEW: Session context
  sessionContext: {
    startTime: string;
    endTime?: string;
    activeMinutes: number;
    toolsUsed: string[];
  };
}
```

### 가치

- **연속성**: "어디까지 했지?"에 완벽한 답변
- **결정 추적**: 왜 그렇게 결정했는지 기록
- **블로커 관리**: 중단 이유와 해결 방법 추적

---

## Pattern 4: Reflexion Pattern (🟡 MEDIUM PRIORITY)

### 출처
- **파일**: `SuperClaude_Framework/src/superclaude/pm_agent/reflexion.py`
- **개념**: 과거 오류에서 학습하여 재발 방지

### 핵심 아이디어

```
에러 발생 시:
1. 과거 유사 에러 검색 (해시 기반)
2. IF 유사 에러 발견 → 알려진 해결책 즉시 적용 (0 토큰)
3. ELSE → 근본 원인 조사 → 해결책 문서화

저장 구조:
- solutions_learned.jsonl (append-only 로그)
- mistakes/[feature]-[date].md (상세 분석)

Mistake Document 구조:
- ❌ What Happened
- 🔍 Root Cause
- 🤔 Why Missed
- ✅ Fix Applied
- 🛡️ Prevention Checklist
- 💡 Lesson Learned
```

### Magic-Note 적용 방안

```typescript
// NEW: insight 노트 타입을 확장하여 "mistake" 유형 추가

type NoteType = 'prompt' | 'plan' | 'choice' | 'insight' | 'mistake';

// NEW: Mistake 노트 자동 생성
interface MistakeNote extends Note {
  type: 'mistake';
  content: string;  // Markdown with structured sections

  // Structured metadata for search
  errorSignature: string;      // For similarity matching
  rootCause?: string;
  solution?: string;
  prevention?: string[];
  linkedWorkflow?: string;
  linkedTask?: string;
}

// 블로커 해결 시 자동으로 mistake 노트 생성 제안
async function onBlockerResolved(task: Task, resolution: string) {
  if (task.blockedBy?.length) {
    return suggestMistakeNote({
      title: `Resolved: ${task.blockedBy[0]}`,
      whatHappened: task.blockedBy[0],
      solution: resolution,
      linkedTask: task.id,
    });
  }
}
```

### 가치

- **학습**: 같은 실수 반복 방지
- **효율**: 알려진 문제는 즉시 해결 (0 토큰)
- **지식 축적**: 팀/개인 노하우 체계적 기록

---

## Pattern 5: Verification Gate (🟡 MEDIUM PRIORITY)

### 출처
- **파일**: `superpowers/skills/verification-before-completion/SKILL.md`
- **개념**: "Evidence before claims, always"

### 핵심 아이디어

```
The Iron Law:
"NO COMPLETION CLAIMS WITHOUT FRESH VERIFICATION EVIDENCE"

The Gate Function:
1. IDENTIFY: 이 주장을 증명하는 명령어는?
2. RUN: 명령어 실행 (fresh, complete)
3. READ: 전체 출력, exit code, 실패 수 확인
4. VERIFY: 출력이 주장을 확인하는가?
5. ONLY THEN: 주장 가능

Common Failures:
- "Tests pass" ← Test output 필요, "should pass" 불가
- "Build succeeds" ← Build exit code 필요, "looks good" 불가
- "Bug fixed" ← 원래 증상 테스트 필요, "code changed" 불가
```

### Magic-Note 적용 방안

```typescript
// Task 완료 시 검증 게이트

interface TaskCompletionGate {
  verificationRequired: boolean;
  verificationCommand?: string;
  expectedOutput?: string;
  actualOutput?: string;
  verified: boolean;
  verifiedAt?: string;
}

// set_task_status에서 'completed'로 변경 시
async function setTaskStatus(taskId: string, status: TaskStatus, options?: {
  verificationOutput?: string;
  skipVerification?: boolean;  // 명시적으로 건너뛰기
}) {
  if (status === 'completed' && !options?.skipVerification) {
    const task = await getTaskById(taskId);

    if (task.verificationCommand && !options?.verificationOutput) {
      return {
        error: 'VERIFICATION_REQUIRED',
        message: `Task requires verification. Run: ${task.verificationCommand}`,
        hint: 'Provide verificationOutput or set skipVerification: true',
      };
    }

    // 검증 출력 기록
    if (options?.verificationOutput) {
      await emitEvent({
        type: 'task.verified',
        payload: {
          taskId,
          command: task.verificationCommand,
          output: options.verificationOutput
        },
      });
    }
  }

  // ... continue with status update
}
```

### 가치

- **신뢰**: "완료"가 진짜 완료를 의미
- **품질**: 검증 없는 완료 방지
- **감사**: 무엇이 검증되었는지 기록

---

## Pattern 6: Two-Stage Review (🟢 ENHANCEMENT)

### 출처
- **파일**: `superpowers/skills/subagent-driven-development/SKILL.md`
- **개념**: Spec Compliance → Code Quality 순서로 2단계 리뷰

### 핵심 아이디어

```
Review Order (순서 중요):
1. Spec Compliance Review FIRST
   - 요구사항 모두 충족?
   - 불필요한 추가 기능 없음?
   - 누락된 것 없음?

2. Code Quality Review SECOND (spec 통과 후에만)
   - 코드 품질, 가독성
   - 테스트 커버리지
   - 성능, 보안

Why This Order:
- 요구사항 미충족 코드를 품질 리뷰하는 것은 낭비
- Spec 통과 = 올바른 것 만들기
- Quality 통과 = 올바르게 만들기
```

### Magic-Note 적용 방안

```typescript
// Task 완료 시 선택적 리뷰 단계

interface TaskReview {
  specCompliance?: {
    reviewer: 'human' | 'agent';
    status: 'pending' | 'passed' | 'failed';
    issues?: string[];
    reviewedAt?: string;
  };
  codeQuality?: {
    reviewer: 'human' | 'agent';
    status: 'pending' | 'passed' | 'failed';
    issues?: string[];
    reviewedAt?: string;
  };
}

// 리뷰가 필요한 태스크에 대해
interface Task {
  // ... existing
  reviewRequired?: boolean;
  review?: TaskReview;
}
```

### 가치

- **효율**: 잘못된 것을 다듬는 낭비 방지
- **품질**: 이중 검증으로 품질 보장
- **명확성**: "무엇을" vs "어떻게"의 분리

---

## Pattern 7: Batch Execution with Checkpoints (🟢 ENHANCEMENT)

### 출처
- **파일**: `superpowers/skills/executing-plans/SKILL.md`
- **개념**: 3개 태스크 배치 실행 → 리포트 → 피드백 → 다음 배치

### 핵심 아이디어

```
Process:
1. Load and Review Plan (비판적 검토)
2. Execute Batch (기본: 3개 태스크)
3. Report (구현된 것, 검증 결과)
4. Wait for Feedback
5. Continue or Adjust

When to Stop:
- 배치 중간에 블로커 발생
- 계획에 심각한 갭 발견
- 지시사항 이해 불가
- 검증 반복 실패
```

### Magic-Note 적용 방안

```typescript
// Workflow 실행 설정

interface WorkflowExecutionConfig {
  batchSize: number;           // 기본: 3
  checkpointAfterBatch: boolean;
  requireReviewBetweenBatches: boolean;
  stopOnBlocker: boolean;
}

// 배치 실행 상태
interface BatchExecution {
  workflowId: string;
  batchNumber: number;
  taskIds: string[];
  status: 'pending' | 'in_progress' | 'awaiting_review' | 'completed';
  report?: {
    completed: string[];
    failed: string[];
    blockers: string[];
  };
  feedback?: string;
}
```

### 가치

- **제어**: 자동화와 인간 감독의 균형
- **복구**: 문제 발생 시 3개 태스크만 영향
- **피드백**: 정기적 검토 기회

---

## Implementation Priority

### Phase 1: 즉시 적용 (Core 모듈 구현 시)

1. **Memory Schema** → Checkpoint 구조에 통합
2. **Bite-Sized Tasks** → Task 타입에 steps, estimatedMinutes 추가
3. **Confidence Checker** → 선택적 태스크 시작 전 검증

### Phase 2: 향상 기능 (MCP 도구 구현 후)

4. **Verification Gate** → set_task_status에 검증 요구
5. **Reflexion Pattern** → mistake 노트 타입 및 자동 생성

### Phase 3: 고급 기능 (안정화 후)

6. **Two-Stage Review** → 선택적 리뷰 워크플로우
7. **Batch Execution** → 배치 실행 모드

---

## Key Insights

`★ Insight ─────────────────────────────────────`
**세 프로젝트의 공통 철학**:
1. **"증거 먼저, 주장은 나중"** - 검증 없는 완료는 거짓말
2. **"작게 쪼개면 진행이 보인다"** - 2-5분 단위 원자적 태스크
3. **"실수는 자산이다"** - 체계적 기록으로 반복 방지
4. **"컨텍스트가 전부다"** - 세션 간 연속성이 생산성의 핵심

**Magic-Note의 차별점**:
- 이들은 "실행"에 집중, Magic-Note는 "지식 보존"에 집중
- Workflow + Note + Insight의 통합이 고유한 가치
- Event Sourcing으로 "왜 그랬지?"에 답변 가능
`─────────────────────────────────────────────────`

---

## Related Documents

- [01-workflow-evolution-spec.md](./01-workflow-evolution-spec.md) - 전문가 패널 토론
- [02-domain-model-design.md](./02-domain-model-design.md) - 도메인 모델 설계
- [03-mcp-tool-api-design.md](./03-mcp-tool-api-design.md) - MCP Tool API 설계
