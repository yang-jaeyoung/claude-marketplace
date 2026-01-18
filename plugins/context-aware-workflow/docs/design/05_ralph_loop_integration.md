# Option A: /cw:loop 명령어 추가 계획

dingco Ralph Loop (반복 실행 자동화)를 cw 플러그인에 통합하는 설계 문서

## 1. 개요

### 1.1 목적

기존 `/cw:auto`는 단계별로 한 번씩만 실행하고 에러 시 중단됩니다.
`/cw:loop`는 **완료 조건이 충족될 때까지 자동으로 반복 실행**하는 자율 에이전트 모드를 제공합니다.

### 1.2 핵심 차이점

| 구분 | /cw:auto | /cw:loop (신규) |
|------|----------|-----------------|
| 실행 방식 | 각 단계 1회 실행 | 완료까지 반복 실행 |
| 에러 처리 | 중단 후 수동 개입 요청 | 자동 재시도/수정 시도 |
| 종료 조건 | 모든 단계 완료 | completion-promise 감지 |
| 최대 실행 | 단계 수만큼 | max-iterations 제한 |

## 2. 명령어 사양

### 2.1 기본 사용법

```bash
# 기본 사용
/cw:loop "REST API 서버와 웹 클라이언트를 만들고 연동합니다. 완료되면 DONE을 출력합니다."

# 옵션 지정
/cw:loop "프로젝트 구현" --max-iterations 30 --completion-promise "COMPLETE"

# 기존 task_plan 기반 실행
/cw:loop --continue --max-iterations 50
```

### 2.2 파라미터

| 파라미터 | 기본값 | 설명 |
|----------|--------|------|
| `--max-iterations` | 20 | 최대 반복 횟수 (무한 루프 방지) |
| `--completion-promise` | "DONE" | 작업 완료를 나타내는 키워드 |
| `--continue` | false | 기존 task_plan.md 기반으로 계속 실행 |
| `--auto-fix` | true | 에러 발생 시 자동 수정 시도 |
| `--verbose` | false | 상세 진행 상황 출력 |
| `--reflect` | true | 완료 후 Ralph Loop 회고 실행 |

### 2.3 완료 조건 (Exit Criteria)

루프가 종료되는 조건:

```
EXIT_CONDITIONS:
  1. completion-promise 키워드가 출력에 포함됨
  2. max-iterations 도달
  3. 사용자가 수동 중단 (Ctrl+C)
  4. 연속 3회 동일 에러 발생 (무한 실패 방지)
  5. task_plan.md의 모든 단계가 ✅ Complete
```

## 3. 구현 아키텍처

### 3.1 파일 구조

```
plugins/context-aware-workflow/
├── commands/
│   └── loop.md                    # 신규: 명령어 정의
├── _shared/
│   └── schemas/
│       └── loop-state.schema.json # 신규: 루프 상태 스키마
└── hooks/
    └── hooks.json                 # 수정: Stop hook 추가
```

### 3.2 핵심 컴포넌트

#### A. commands/loop.md

```yaml
---
description: Run autonomous loop until task completion (dingco Ralph Loop pattern)
argument-hint: "<task description>"
---
```

#### B. 루프 상태 관리 (.caw/loop_state.json)

```json
{
  "loop_id": "loop_20240115_143022",
  "started_at": "2024-01-15T14:30:22Z",
  "status": "running",
  "config": {
    "max_iterations": 20,
    "completion_promise": "DONE",
    "auto_fix": true
  },
  "iterations": [
    {
      "number": 1,
      "started_at": "...",
      "ended_at": "...",
      "outcome": "partial",
      "steps_completed": ["1.1", "1.2"],
      "errors": [],
      "output_contains_promise": false
    }
  ],
  "current_iteration": 3,
  "consecutive_failures": 0,
  "completion_detected": false
}
```

#### C. Stop Hook (완료 조건 검사)

```json
{
  "Stop": [
    {
      "matcher": "loop_active",
      "hooks": [
        {
          "type": "prompt",
          "prompt": "## Loop Completion Check\n\n1. Read .caw/loop_state.json\n2. Check if output contains completion_promise\n3. If found: Update status to 'completed', output completion message\n4. If not found AND iterations < max: Continue to next iteration\n5. If max reached: Update status to 'max_iterations_reached'"
        }
      ]
    }
  ]
}
```

### 3.3 실행 흐름

```
┌─────────────────────────────────────────────────────────────┐
│                    /cw:loop "task"                          │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│  [1] Initialize                                             │
│  ├─ Create .caw/loop_state.json                            │
│  ├─ Check .caw/context_manifest.json (bootstrap if needed) │
│  └─ Generate initial task_plan.md (if not --continue)      │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
        ┌─────────────────────────────┐
        │  [2] Iteration N            │◄────────────────┐
        │  ├─ Execute pending steps   │                 │
        │  ├─ Handle errors (auto-fix)│                 │
        │  └─ Log iteration result    │                 │
        └─────────────┬───────────────┘                 │
                      │                                  │
                      ▼                                  │
        ┌─────────────────────────────┐                 │
        │  [3] Check Exit Conditions  │                 │
        │  ├─ completion_promise?     │                 │
        │  ├─ max_iterations?         │                 │
        │  ├─ all steps complete?     │                 │
        │  └─ consecutive failures?   │                 │
        └─────────────┬───────────────┘                 │
                      │                                  │
              ┌───────┴───────┐                         │
              │               │                         │
          CONTINUE         EXIT                         │
              │               │                         │
              └───────────────┼─────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────┐
        │  [4] Finalize               │
        │  ├─ Update loop_state       │
        │  ├─ Generate summary        │
        │  └─ Run /cw:reflect (opt)   │
        └─────────────────────────────┘
```

## 4. 상세 설계

### 4.1 Iteration 로직

```markdown
## Single Iteration Execution

FOR each iteration:

1. **Read Current State**
   - Load .caw/task_plan.md
   - Find pending steps (⏳ status)
   - Load .caw/loop_state.json for context

2. **Execute Steps**
   - Invoke Builder agent for each pending step
   - On success: Update step status to ✅
   - On failure:
     - If auto_fix enabled: Attempt Fixer agent
     - Log error to iteration record

3. **Check Progress**
   - Count completed vs total steps
   - Check if any output contains completion_promise
   - Check if new steps were added (dynamic planning)

4. **Record Iteration**
   - Save iteration result to loop_state.json
   - Update consecutive_failure counter
   - Log progress message

5. **Evaluate Exit**
   - Apply exit conditions
   - If continuing: Increment iteration, goto step 1
   - If exiting: Proceed to finalization
```

### 4.2 에러 복구 전략

```markdown
## Auto-Fix Strategy

Level 1: Retry
  - Same step, fresh attempt
  - Clear any cached state

Level 2: Analyze & Fix
  - Read error message
  - Invoke Fixer agent with error context
  - Apply suggested fix
  - Retry step

Level 3: Alternative Approach
  - If step fails 3 times
  - Invoke Planner to suggest alternative
  - Update task_plan.md with new approach
  - Continue with modified plan

Level 4: Skip & Continue
  - Mark step as ⏭️ Skipped with reason
  - Log to iteration errors
  - Continue to next step
  - Note: Only if step is not blocking

Level 5: Abort
  - If 3 consecutive iterations with no progress
  - Save state and exit
  - Report to user for manual intervention
```

### 4.3 Completion Promise 감지

```markdown
## Detection Logic

AFTER each agent execution:

1. Capture all output text
2. Normalize (lowercase, trim whitespace)
3. Check if contains completion_promise (case-insensitive)
4. Check for variations:
   - Exact match: "DONE"
   - With punctuation: "DONE!", "DONE."
   - In sentence: "Task is DONE"

IF detected:
  - Set completion_detected = true
  - Record detection context
  - Proceed to finalization

ALSO check for implicit completion:
  - All steps in task_plan.md are ✅
  - No pending or blocked steps
  - Tests passing (if applicable)
```

## 5. 출력 형식

### 5.1 진행 상황 표시

```
🔄 /cw:loop "REST API와 웹 연동"

══════════════════════════════════════════════════════════════
📍 Iteration 1/20
══════════════════════════════════════════════════════════════
[1.1] Creating Express server...        ✓
[1.2] Setting up API endpoints...       ✓
[1.3] Adding CORS middleware...         ✓

Progress: 3/8 steps (37.5%)
Completion promise "DONE" not detected
Continuing to next iteration...

══════════════════════════════════════════════════════════════
📍 Iteration 2/20
══════════════════════════════════════════════════════════════
[2.1] Creating web client...            ✓
[2.2] Implementing fetch calls...       ✓
[2.3] Connecting to API...              ⚠️ Error: CORS issue

🔧 Auto-fix attempt 1/3...
   → Analyzing error...
   → Applying fix: Update CORS origin
   → Retrying step 2.3...                ✓

Progress: 6/8 steps (75%)
Completion promise "DONE" not detected
Continuing to next iteration...

══════════════════════════════════════════════════════════════
📍 Iteration 3/20
══════════════════════════════════════════════════════════════
[3.1] Writing E2E tests...              ✓
[3.2] Running full test suite...        ✓

🎯 Output: "All tests passing. DONE"

✅ Completion promise "DONE" detected!
══════════════════════════════════════════════════════════════

📊 Loop Summary
──────────────────────────────────────────────────────────────
• Iterations: 3/20
• Steps completed: 8/8 (100%)
• Errors encountered: 1 (auto-fixed)
• Duration: 4m 32s

Running /cw:reflect for continuous improvement...
```

### 5.2 에러 종료 출력

```
🔄 /cw:loop "complex task"

══════════════════════════════════════════════════════════════
⚠️ Loop Stopped: Max Iterations Reached
══════════════════════════════════════════════════════════════

📊 Final Status
──────────────────────────────────────────────────────────────
• Iterations: 20/20 (limit reached)
• Steps completed: 15/23 (65%)
• Remaining steps:
  - [4.2] Integration testing     ⏳
  - [4.3] Performance tuning      ⏳
  - [5.1] Documentation           ⏳
  ...

📋 State saved to: .caw/loop_state.json

💡 To continue:
   /cw:loop --continue --max-iterations 30

💡 To review current state:
   /cw:status
```

## 6. 구현 순서

### Phase 1: 기본 구조 (필수)

```
□ 1.1 commands/loop.md 생성
    - 명령어 정의 및 파라미터 설명
    - 기본 실행 흐름 지시

□ 1.2 _shared/schemas/loop-state.schema.json 생성
    - 루프 상태 JSON 스키마 정의

□ 1.3 hooks/hooks.json 수정
    - Stop hook 추가 (completion 검사)
```

### Phase 2: 핵심 로직 (필수)

```
□ 2.1 Iteration 실행 로직
    - task_plan.md 읽기/업데이트
    - Builder 에이전트 호출
    - 결과 기록

□ 2.2 Exit 조건 검사
    - completion_promise 감지
    - max_iterations 체크
    - 연속 실패 카운트

□ 2.3 State 관리
    - loop_state.json 생성/업데이트
    - 재시작 지원 (--continue)
```

### Phase 3: 에러 처리 (권장)

```
□ 3.1 Auto-fix 통합
    - Fixer 에이전트 호출
    - 재시도 로직

□ 3.2 복구 전략
    - 대안 접근법 제안
    - 스킵 & 계속 옵션
```

### Phase 4: 통합 (선택)

```
□ 4.1 /cw:reflect 연동
    - 루프 완료 후 자동 회고

□ 4.2 Serena 메모리 저장
    - 루프 결과 크로스세션 저장

□ 4.3 테스트 작성
    - 루프 시나리오 테스트
```

## 7. 기존 기능과의 관계

### 7.1 /cw:auto 와의 차이

```
/cw:auto:
├─ 7단계 순차 실행
├─ 에러 시 중단
├─ 수동 개입 필요
└─ 한 번에 완료 목표

/cw:loop:
├─ N회 반복 실행
├─ 에러 시 자동 복구 시도
├─ 자율 진행
└─ 완료까지 반복 목표
```

### 7.2 /cw:reflect 와의 관계

```
/cw:loop 완료 후:
└─ 자동으로 /cw:reflect 호출 (--reflect 옵션)
    └─ Ralph Loop 회고 사이클 실행
        ├─ Reflect: 루프 실행 리뷰
        ├─ Analyze: 반복 패턴 분석
        ├─ Learn: 자동화 개선점 학습
        ├─ Plan: 다음 루프 최적화
        └─ Habituate: 학습 내용 저장
```

### 7.3 명명 정리

| 명령어 | 의미 | 출처 |
|--------|------|------|
| `/cw:loop` | 반복 실행 자동화 | dingco Ralph Loop |
| `/cw:reflect` | 회고 사이클 (RALPH) | cw 기존 구현 |
| `/cw:auto` | 단일 실행 자동화 | cw 기존 구현 |

## 8. 리스크 및 고려사항

### 8.1 무한 루프 방지

```
안전장치:
1. max_iterations 필수 (기본값 20)
2. 연속 3회 동일 에러 시 중단
3. 진행 없는 반복 3회 시 중단
4. 사용자 중단 (Ctrl+C) 지원
```

### 8.2 리소스 관리

```
고려사항:
- 긴 실행 시간으로 인한 컨텍스트 소진
- API 호출 비용 증가
- 파일 시스템 상태 관리

대응:
- 각 iteration 후 상태 저장 (복구 가능)
- 진행률 기반 중간 체크포인트
- --max-iterations로 상한선 설정
```

### 8.3 기존 기능 호환성

```
보장 사항:
- 기존 /cw:auto 동작 변경 없음
- 기존 /cw:reflect 동작 변경 없음
- 동일한 task_plan.md 형식 사용
- 동일한 에이전트 재사용
```

## 9. 향후 확장 가능성

### 9.1 병렬 루프

```bash
# 여러 태스크 동시 실행
/cw:loop "API 개발" --worktree api &
/cw:loop "UI 개발" --worktree ui &
```

### 9.2 조건부 분기

```bash
# 조건에 따른 분기 실행
/cw:loop "테스트 통과까지" --until "all tests pass"
/cw:loop "커버리지 80% 달성" --until "coverage >= 80%"
```

### 9.3 스케줄링

```bash
# 특정 시간/조건에 실행
/cw:loop "정기 리팩토링" --schedule "weekly"
```

## 10. 활용 사례

### 10.1 Review-Fix 루프

코드 리뷰에서 High 이상 심각도 이슈가 없을 때까지 자동으로 리뷰와 수정을 반복합니다.

#### 사용법

```bash
/cw:loop "코드 리뷰 후 High 이상 이슈 수정. 이슈 없으면 REVIEW_PASSED 출력" \
  --completion-promise "REVIEW_PASSED" \
  --max-iterations 10
```

#### 내부 동작 흐름

```
┌─────────────────────────────────────────────────────────────┐
│                    Iteration N                               │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
        ┌─────────────────────────────┐
        │  [1] /cw:review 실행        │
        │  → .caw/review_result.json  │
        └─────────────┬───────────────┘
                      │
                      ▼
        ┌─────────────────────────────┐
        │  [2] 결과 분석              │
        │  ├─ Critical 이슈?          │
        │  └─ High 이슈?              │
        └─────────────┬───────────────┘
                      │
              ┌───────┴───────┐
              │               │
        있음 (≥1)         없음 (0)
              │               │
              ▼               ▼
   ┌──────────────────┐  ┌──────────────────┐
   │ [3a] /cw:fix     │  │ [3b] 출력:       │
   │ → 이슈 수정      │  │ "REVIEW_PASSED"  │
   │ → 다음 iteration │  │ → 루프 종료      │
   └──────────────────┘  └──────────────────┘
```

#### 리뷰 결과 스키마 확장

```json
// .caw/review_result.json
{
  "review_id": "review_20240115_150000",
  "timestamp": "2024-01-15T15:00:00Z",
  "issues": {
    "critical": 0,
    "high": 2,
    "medium": 5,
    "low": 12,
    "info": 8
  },
  "details": [
    {
      "severity": "high",
      "category": "security",
      "file": "src/auth/jwt.ts",
      "line": 42,
      "message": "JWT secret is hardcoded",
      "suggestion": "Use environment variable"
    }
  ],
  "pass_threshold": {
    "critical": 0,
    "high": 0
  },
  "passed": false
}
```

#### 출력 예시

```
🔄 /cw:loop "Review-Fix until clean"

══════════════════════════════════════════════════════════════
📍 Iteration 1/10
══════════════════════════════════════════════════════════════
🔍 Running /cw:review...

📊 Review Results:
   Critical: 0 | High: 2 | Medium: 5 | Low: 12

⚠️ High severity issues found:
   [1] src/auth/jwt.ts:42 - JWT secret is hardcoded
   [2] src/api/user.ts:88 - SQL injection vulnerability

🔧 Running /cw:fix...
   → Fixing issue 1/2: JWT secret...     ✓
   → Fixing issue 2/2: SQL injection...  ✓

Continuing to next iteration...

══════════════════════════════════════════════════════════════
📍 Iteration 2/10
══════════════════════════════════════════════════════════════
🔍 Running /cw:review...

📊 Review Results:
   Critical: 0 | High: 0 | Medium: 4 | Low: 12

✅ No Critical or High severity issues!

🎯 Output: "REVIEW_PASSED"

══════════════════════════════════════════════════════════════
✅ Completion promise "REVIEW_PASSED" detected!
══════════════════════════════════════════════════════════════

📊 Loop Summary
──────────────────────────────────────────────────────────────
• Iterations: 2/10
• Issues fixed: 2 High
• Remaining: 4 Medium, 12 Low (below threshold)
• Duration: 1m 45s

💡 To fix remaining issues:
   /cw:loop "Medium 이슈까지 수정. 완료시 ALL_CLEAN" \
     --completion-promise "ALL_CLEAN"
```

#### 확장: 조건 기반 종료 (Phase 2)

Phase 2에서 `--until` 파라미터를 추가하면 더 유연한 조건 지정 가능:

```bash
# 표현식 기반 종료 조건
/cw:loop review-fix \
  --until "review.issues.high == 0 && review.issues.critical == 0" \
  --max-iterations 10

# 특정 임계값 기반
/cw:loop review-fix \
  --severity-threshold medium \
  --max-iterations 15
```

#### loop_state.json 확장

```json
{
  "loop_id": "loop_20240115_150000",
  "mode": "review-fix",
  "config": {
    "completion_promise": "REVIEW_PASSED",
    "max_iterations": 10,
    "exit_condition": {
      "type": "review_threshold",
      "max_severity": "medium",
      "data_source": ".caw/review_result.json"
    }
  },
  "iterations": [
    {
      "number": 1,
      "review_result": {
        "critical": 0,
        "high": 2,
        "medium": 5
      },
      "issues_fixed": ["jwt_secret", "sql_injection"],
      "passed": false
    },
    {
      "number": 2,
      "review_result": {
        "critical": 0,
        "high": 0,
        "medium": 4
      },
      "issues_fixed": [],
      "passed": true
    }
  ],
  "completion_detected": true
}
```

### 10.2 Test-Fix 루프

모든 테스트가 통과할 때까지 반복:

```bash
/cw:loop "테스트 실행 후 실패 수정. 전체 통과시 ALL_TESTS_PASS" \
  --completion-promise "ALL_TESTS_PASS" \
  --max-iterations 15
```

### 10.3 Build-Fix 루프

빌드 에러가 없을 때까지 반복:

```bash
/cw:loop "빌드 실행 후 에러 수정. 성공시 BUILD_SUCCESS" \
  --completion-promise "BUILD_SUCCESS" \
  --max-iterations 10
```

### 10.4 복합 품질 루프

여러 품질 게이트를 순차 통과:

```bash
/cw:loop "빌드, 테스트, 린트, 리뷰 모두 통과까지. 완료시 QUALITY_GATE_PASSED" \
  --completion-promise "QUALITY_GATE_PASSED" \
  --max-iterations 20
```

내부 동작:
```
FOR each iteration:
  1. npm run build     → 실패시 수정
  2. npm test          → 실패시 수정
  3. npm run lint      → 실패시 수정
  4. /cw:review        → High 이상시 수정
  5. 모두 통과 → "QUALITY_GATE_PASSED"
```

---

## 부록: 참고 자료

- [dingco Ralph Loop](https://github.com/dingcodingco/dingco-ralph-wiggum)
- [기존 /cw:auto 구현](../commands/auto.md)
- [기존 /cw:reflect 구현](../skills/reflect/SKILL.md)
