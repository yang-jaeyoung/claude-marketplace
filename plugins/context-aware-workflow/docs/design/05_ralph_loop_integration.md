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
  "schema_version": "1.0",
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

**스키마 버전 관리**

```markdown
## 버전 호환성

schema_version 필드로 하위 호환성 관리:
- "1.0": 초기 버전 (MVP)
- "1.1": iteration_result.json 통합 (Phase 2)
- "2.0": 병렬 루프 지원 (Phase 4+)

## 마이그레이션 로직

loop_state.json 로드 시:
1. schema_version 확인
2. 현재 버전보다 낮으면 자동 마이그레이션
3. 현재 버전보다 높으면 경고 + 읽기 전용 모드
```

#### C. Stop Hook (완료 조건 검사)

**구현 방식**: 파일 존재 여부 기반 조건부 활성화

현재 cw 플러그인의 hooks.json은 문자열 매처(tool name 기반)를 사용합니다.
`loop_active`라는 조건부 매처 대신, **commands/loop.md 내부에서 반복 로직을 직접 제어**하는 방식을 채택합니다.

```markdown
## Loop Completion Check (commands/loop.md 내 로직)

각 iteration 종료 시:
1. .caw/loop_state.json 읽기
2. 현재 iteration의 출력에서 completion_promise 검색
3. 감지됨 → status를 'completed'로 업데이트, 루프 종료
4. 미감지 AND iterations < max → 다음 iteration 진행
5. max 도달 → status를 'max_iterations_reached'로 업데이트
```

**대안 A: PreToolUse Hook 활용** (Phase 2)

```json
{
  "PreToolUse": [
    {
      "matcher": "Task",
      "hooks": [
        {
          "type": "prompt",
          "prompt": "IF .caw/loop_state.json exists AND status == 'running':\n  Check exit conditions before proceeding"
        }
      ]
    }
  ]
}
```

**대안 B: 전용 Loop Controller Agent** (Phase 3)

별도의 loop-controller 에이전트가 iteration 관리를 전담:
- Builder 에이전트 호출/감시
- 출력 캡처 및 completion_promise 감지
- 상태 업데이트 및 다음 iteration 결정

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

#### 출력 캡처 메커니즘

Claude Code에서 에이전트 출력을 캡처하는 방법:

**방법 1: 파일 기반 로깅 (권장)**

```markdown
## Builder 에이전트 호출 시

1. Builder 실행 전: .caw/iteration_output.md 초기화
2. Builder 에이전트 시스템 프롬프트에 추가:
   "각 단계 완료 시 결과를 .caw/iteration_output.md에 append하세요"
3. Builder 종료 후: .caw/iteration_output.md 읽어서 completion_promise 검색
```

**방법 2: task_plan.md 상태 기반 (보조)**

```markdown
## 암시적 완료 감지

task_plan.md의 단계 상태를 파싱하여:
- 모든 단계가 ✅ → 암시적 완료
- ⏳ 또는 ❌ 존재 → 미완료
```

**방법 3: 구조화된 결과 파일 (Phase 3)**

```json
// .caw/iteration_result.json
{
  "iteration": 3,
  "steps_executed": ["3.1", "3.2"],
  "outputs": [
    { "step": "3.1", "result": "success", "message": "Tests created" },
    { "step": "3.2", "result": "success", "message": "All tests passing. DONE" }
  ],
  "completion_promise_found": true,
  "found_in": "step 3.2 output"
}
```

#### 파일 역할 구분 (iteration_output.md vs iteration_result.json)

| 파일 | Phase | 용도 | Primary Source |
|------|-------|------|----------------|
| `iteration_output.md` | Phase 2+ | Human-readable 로그, completion promise 감지 | **Phase 2의 truth** |
| `iteration_result.json` | Phase 3+ | 구조화된 분석용 데이터, 에러 추적 강화 | Phase 3 이후 보조 |

**결정 근거**:
- Phase 2 (MVP): `iteration_output.md`만 사용 - Builder가 자연스럽게 작성 가능
- Phase 3+: `iteration_result.json` 추가 - 복잡한 에러 분석, 메트릭 수집에 활용
- `iteration_output.md`는 항상 completion promise 감지의 primary source로 유지

#### 감지 로직

```markdown
## Detection Logic

AFTER each iteration:

1. Read .caw/iteration_output.md (또는 iteration_result.json)
2. Normalize (lowercase, trim whitespace)
3. Check if contains completion_promise (case-insensitive)
4. Check for variations:
   - Exact match: "DONE"
   - With punctuation: "DONE!", "DONE."
   - In sentence: "Task is DONE"

IF detected:
  - Set completion_detected = true
  - Record detection context (which step, which output)
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

> **설계 원칙**: Phase 1은 최소 기능으로 빠르게 검증 가능하도록 구성.
> Hook 기반 복잡한 로직은 Phase 2 이후로 이동.

### Phase 1: MVP (필수) - 단순 반복 실행

```
□ 1.1 commands/loop.md 생성
    - 명령어 정의 및 파라미터 설명
    - 기본 반복 실행 흐름 (max_iterations 기반 종료만)
    - Builder 에이전트 호출 로직

□ 1.2 _shared/schemas/loop-state.schema.json 생성
    - 루프 상태 JSON 스키마 정의 (schema_version 포함)

□ 1.3 기본 종료 조건
    - max_iterations 도달 시 종료
    - task_plan.md 모든 단계 완료 시 종료 (암시적)
    - 연속 3회 실패 시 종료

목표: 파라미터 없이 `/cw:loop --continue`로 기존 task_plan 반복 실행 가능
```

### Phase 2: 완료 조건 감지 (필수)

```
□ 2.1 출력 캡처 메커니즘
    - .caw/iteration_output.md 파일 기반 로깅
    - Builder 에이전트 프롬프트 수정

□ 2.2 completion_promise 감지
    - iteration_output.md에서 키워드 검색
    - 감지 시 루프 종료 및 상태 업데이트

□ 2.3 State 관리 강화
    - loop_state.json iterations 배열 관리
    - 재시작 지원 (--continue)

목표: `/cw:loop "task" --completion-promise "DONE"` 동작
```

### Phase 3: 에러 처리 (권장)

```
□ 3.1 Auto-fix 통합
    - Fixer 에이전트 호출 (Level 1-2)
    - 재시도 로직

□ 3.2 복구 전략
    - 대안 접근법 제안 (Level 3)
    - 스킵 & 계속 옵션 (Level 4)

□ 3.3 iteration_result.json 구조화
    - 단계별 결과 기록
    - 에러 추적 강화
```

### Phase 4: 통합 및 최적화 (선택)

```
□ 4.1 /cw:reflect 연동
    - 루프 완료 후 자동 회고

□ 4.2 컨텍스트 관리
    - iteration 5회마다 자동 정리
    - Serena 메모리 저장

□ 4.3 테스트 작성
    - 루프 시나리오 테스트
    - 에지 케이스 검증
```

### Phase 5: 고급 기능 (향후)

```
□ 5.1 /cw:auto --review-loop 통합
    - auto.md에서 loop 로직 재사용

□ 5.2 PreToolUse Hook 기반 조건부 활성화
    - 루프 활성 상태에서만 동작하는 hook

□ 5.3 Loop Controller Agent
    - 전용 에이전트로 iteration 관리 분리
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
```

#### 컨텍스트 윈도우 관리 전략

```markdown
## Iteration별 컨텍스트 최적화

각 iteration 시작 시:
1. 이전 iteration의 상세 로그는 loop_state.json에만 유지
2. 현재 iteration에 필요한 최소 정보만 로드:
   - task_plan.md (현재 pending 단계만)
   - loop_state.json (config + current_iteration만)
3. 대화 컨텍스트가 임계치 도달 시 자동 정리 (Phase 3)

## 파일 기반 상태 분리

컨텍스트에 유지:        파일에만 저장:
├─ 현재 iteration 정보   ├─ 이전 iterations 상세
├─ 현재 단계 목록        ├─ 에러 히스토리
└─ completion config     └─ 수정 이력
```

**컨텍스트 자동 정리 (Phase 3 구현)**:
```
## 자동 정리 트리거

구현 시점: Phase 3

트리거 조건:
- iteration 5회마다 자동 실행
- 또는 loop_state.json에 iterations 배열 크기 > 10

정리 동작:
1. loop_state.json의 오래된 iteration 상세를 요약으로 압축
2. iteration_output.md 내용을 summary로 변환 후 초기화
3. 현재 진행 상태와 최근 3 iteration만 유지
```

#### 비용 관리

```markdown
## API 호출 최적화

1. Builder 에이전트는 필요한 파일만 읽도록 제한
2. 반복되는 컨텍스트 로드 최소화
3. --verbose=false 기본값으로 출력 최소화

## 예상 비용 (참고)

iteration당 평균:
- Sonnet 호출: 3-5회
- 토큰: ~10K input, ~3K output

20 iterations 기준:
- 총 호출: 60-100회
- 총 토큰: ~200K input, ~60K output
```

#### 대응 방안

```
- 각 iteration 후 상태 저장 (복구 가능)
- 진행률 기반 중간 체크포인트
- --max-iterations로 상한선 설정
- iteration 5회마다 자동 컨텍스트 정리 고려 (Phase 3)
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

## 11. /cw:auto 통합 방안

기존 `/cw:auto`의 review → fix 단계에 loop 패턴을 통합하는 방안입니다.

> **중복 방지 원칙**: `/cw:auto --review-loop`는 `/cw:loop`의 로직을 **재사용**합니다.
> 별도 구현이 아닌 내부 호출 방식으로 코드 중복을 피합니다.

### 11.1 현재 /cw:auto 워크플로우

```
[1/7] init     → 환경 초기화
[2/7] start    → 계획 생성
[3/7] next     → 단계 실행
[4/7] review   → 코드 리뷰 (1회)
[5/7] fix      → 이슈 수정 (1회)
[6/7] check    → 컴플라이언스 체크
[7/7] reflect  → 회고
```

**문제점**: review-fix가 1회만 실행되어 High 이슈가 남을 수 있음

### 11.2 제안: --review-loop 플래그 추가

```bash
# 기존 동작 (1회 review-fix) - 하위 호환성 유지
/cw:auto "task"

# Review-Fix Loop 모드 활성화
/cw:auto "task" --review-loop

# 옵션 지정
/cw:auto "task" --review-loop --max-review-iterations 5 --review-threshold high
```

### 11.3 새 파라미터

| 파라미터 | 기본값 | 설명 |
|----------|--------|------|
| `--review-loop` | false | Review-Fix를 반복 실행 |
| `--max-review-iterations` | 5 | 최대 Review-Fix 반복 횟수 |
| `--review-threshold` | high | 이 심각도 이상 이슈 시 반복 (critical, high, medium) |

### 11.4 수정된 워크플로우

```
[1/6] init
[2/6] start
[3/6] next
[4/6] review-fix-loop  ← 조건부 반복
      │
      ├─► review
      │     ↓
      │   High 이슈?
      │     ├─ YES → fix → 다음 iteration
      │     └─ NO  → 루프 종료
      │
      └─► 안전장치: max-review-iterations 도달 시 종료
[5/6] check
[6/6] reflect
```

### 11.5 종료 조건

```
Review-Fix Loop 종료 조건:
  1. review-threshold 이상 이슈가 0개
  2. max-review-iterations 도달
  3. 연속 2회 동일 이슈 (수정 불가 판단)
```

### 11.6 출력 예시

```
🚀 /cw:auto "Add logout button" --review-loop

[1/6] Initializing...     ✓
[2/6] Planning...         ✓ (2 phases, 5 steps)
[3/6] Executing...        ✓ (5/5 steps complete)
[4/6] Review-Fix Loop...
      ├─ Iteration 1/5: 2 High issues found
      │   🔧 Fixing: JWT secret hardcoded... ✓
      │   🔧 Fixing: SQL injection risk... ✓
      ├─ Iteration 2/5: 1 High issue found
      │   🔧 Fixing: Missing input validation... ✓
      └─ Iteration 3/5: 0 High issues ✓
[5/6] Checking...         ✓ (compliant)
[6/6] Reflecting...       ✓

✅ Workflow Complete

📊 Summary:
  • Steps executed: 5
  • Review-Fix iterations: 3
  • Issues fixed: 3 High, 2 Medium (auto)
  • Remaining: 4 Low (below threshold)
  • Compliance: Pass
```

### 11.7 에러 처리

#### 최대 반복 도달

```
[4/6] Review-Fix Loop...
      ├─ Iteration 1/5: 3 High issues → fixed 2
      ├─ Iteration 2/5: 2 High issues → fixed 1
      ├─ Iteration 3/5: 2 High issues → fixed 1
      ├─ Iteration 4/5: 2 High issues → fixed 0 ⚠️
      └─ Iteration 5/5: 2 High issues → MAX REACHED

⚠️ Review-Fix Loop: Max iterations reached

📋 Remaining High Issues (2):
  1. src/auth/oauth.ts:88 - Complex refactoring needed
  2. src/api/upload.ts:156 - Architecture change required

💡 Options:
  1. Fix manually and run: /cw:review
  2. Continue without fixing: /cw:check
  3. Increase limit: /cw:auto --continue --max-review-iterations 10
```

#### 수정 불가 이슈 감지

```
[4/6] Review-Fix Loop...
      ├─ Iteration 1/5: 2 High issues → fixed 1
      ├─ Iteration 2/5: 1 High issue → fixed 0
      └─ Iteration 3/5: 1 High issue → same issue detected ⚠️

⚠️ Review-Fix Loop: Unfixable issue detected

📋 Unfixable Issue:
  src/legacy/parser.ts:234
  "Deprecated API usage requires manual migration"

💡 This issue cannot be auto-fixed. Options:
  1. Fix manually and resume: /cw:auto --continue
  2. Skip and continue: /cw:check
  3. Add to tech debt: /cw:defer
```

### 11.8 session.json 확장

```json
{
  "auto_mode": {
    "active": true,
    "current_stage": 4,
    "options": {
      "review_loop": true,
      "max_review_iterations": 5,
      "review_threshold": "high"
    }
  },
  "review_loop_state": {
    "current_iteration": 3,
    "iterations": [
      {
        "number": 1,
        "issues_found": { "high": 2, "medium": 3 },
        "issues_fixed": { "high": 2, "medium": 1 },
        "unfixable": []
      },
      {
        "number": 2,
        "issues_found": { "high": 1, "medium": 2 },
        "issues_fixed": { "high": 1, "medium": 0 },
        "unfixable": []
      },
      {
        "number": 3,
        "issues_found": { "high": 0, "medium": 2 },
        "issues_fixed": {},
        "passed": true
      }
    ],
    "total_fixed": { "high": 3, "medium": 1 },
    "completion_reason": "threshold_met"
  }
}
```

### 11.9 구현 우선순위

```
Phase 1 (MVP):
  □ --review-loop 플래그 파싱
  □ 기본 반복 로직 (max-review-iterations)
  □ High 이슈 기준 종료 조건

Phase 2 (Enhanced):
  □ --review-threshold 파라미터
  □ 수정 불가 이슈 감지
  □ session.json 상태 저장

Phase 3 (Polish):
  □ 상세 출력 포맷
  □ --continue 재개 지원
  □ 테스트 작성
```

### 11.10 /cw:loop 와의 관계

| 명령어 | 용도 | Review-Fix | 구현 |
|--------|------|------------|------|
| `/cw:auto` | 전체 워크플로우 | 1회 (기본) | 기존 |
| `/cw:auto --review-loop` | 전체 워크플로우 | N회 (loop) | **loop.md 재사용** |
| `/cw:loop` | 범용 반복 실행 | 커스텀 가능 | 신규 (핵심) |

**아키텍처**:
```
/cw:auto --review-loop
    │
    ├─ [1-3] init → start → next (기존 로직)
    │
    └─ [4] review-fix-loop
           │
           └─► 내부적으로 /cw:loop 로직 호출
               - completion_promise: "REVIEW_PASSED"
               - task: "리뷰 후 High 이상 이슈 수정"
               - max_iterations: --max-review-iterations 값
```

**차이점**:
- `/cw:auto --review-loop`: 전체 워크플로우 내에서 review-fix만 반복 (loop.md 로직 재사용)
- `/cw:loop`: 독립적인 범용 반복 실행 (review-fix 외 다양한 패턴)

**구현 우선순위**:
1. `/cw:loop` 먼저 구현 (Phase 1-2)
2. `/cw:auto --review-loop`는 loop 로직 재사용으로 구현 (Phase 5)

**사용 시나리오**:
```bash
# 전체 작업 자동화 + 품질 보장
/cw:auto "feature 구현" --review-loop

# review-fix만 별도 실행
/cw:loop "리뷰 후 High 이상 수정. 완료시 DONE" --max-iterations 10

# 기존 코드 품질 개선 (전체 워크플로우 없이)
/cw:loop "전체 코드베이스 리뷰 및 수정" --completion-promise "ALL_CLEAN"
```

---

## 부록: 참고 자료

- [dingco Ralph Loop](https://github.com/dingcodingco/dingco-ralph-wiggum)
- [기존 /cw:auto 구현](../commands/auto.md)
- [기존 /cw:reflect 구현](../skills/reflect/SKILL.md)
