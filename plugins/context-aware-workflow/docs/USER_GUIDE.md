# Context-Aware Workflow (CAW) 사용자 가이드

> **버전**: 2.0.0
> **목적**: 구조화된 작업 계획과 컨텍스트 관리를 통한 효율적인 개발 워크플로우
> **업데이트**: **Swarm 병렬 실행**, **Pipeline 명시적 파이프라인**, **Analytics 비용 분석**, **Evolve 인스팅트 진화**, **Dashboard/HUD 시각화**, GUIDELINES.md/AGENTS.md 자동 생성, QA Loop, UltraQA, Research Mode, Autonomous Loop, Tidy First 방법론

---

## 📋 목차

1. [빠른 시작](#-빠른-시작)
2. [핵심 개념](#-핵심-개념)
3. [초기화 고급 기능](#-초기화-고급-기능)
4. [QA Loop & UltraQA](#-qa-loop--ultraqa)
5. [Research Mode](#-research-mode)
6. [Autonomous Loop](#-autonomous-loop)
7. [Swarm 병렬 실행](#-swarm-병렬-실행) **(NEW v2.0.0)**
8. [Pipeline 명시적 파이프라인](#-pipeline-명시적-파이프라인) **(NEW v2.0.0)**
9. [Analytics 비용 분석](#-analytics-비용-분석) **(NEW v2.0.0)**
10. [Tidy First 방법론](#-tidy-first-방법론)
11. [명령어 상세](#-명령어-상세)
12. [에이전트](#-에이전트)
13. [스킬](#-스킬)
14. [워크플로우 예시](#-워크플로우-예시)
15. [훅 동작](#-훅-동작)
16. [베스트 프랙티스](#-베스트-프랙티스)
17. [문제 해결](#-문제-해결)

---

## 🚀 빠른 시작

### 설치

```bash
# 방법 1: 세션별 로드 (테스트용)
claude --plugin-dir /path/to/context-aware-workflow

# 방법 2: 영구 설치
claude plugin add /path/to/context-aware-workflow
```

### 첫 사용 (2분 완성)

```bash
# 1. 환경 초기화 (선택 - /cw:start에서 자동 실행됨)
/cw:init

# 2. 새 작업 시작
/cw:start "JWT 인증 시스템 구현"

# 3. 현재 상태 확인
/cw:status

# 4. 다음 단계 자동 실행 (병렬 실행 기본)
/cw:next

# 5. 코드 리뷰
/cw:review

# 6. 지속적 개선 (Ralph Loop)
/cw:reflect
```

### 명령어 한눈에 보기

| 명령어 | 단축형 | 설명 |
|--------|--------|------|
| `/context-aware-workflow:auto` | `/cw:auto` | **전체 워크플로우 자동 실행** |
| `/context-aware-workflow:loop` | `/cw:loop` | **자율 반복 실행** |
| `/context-aware-workflow:swarm` | `/cw:swarm` | **병렬 에이전트 스웜** (NEW v2.0) |
| `/context-aware-workflow:pipeline` | `/cw:pipeline` | **명시적 순차 파이프라인** (NEW v2.0) |
| `/context-aware-workflow:init` | `/cw:init` | 환경 초기화 (자동 실행) |
| `/context-aware-workflow:brainstorm` | `/cw:brainstorm` | 요구사항 발굴 (선택) |
| `/context-aware-workflow:design` | `/cw:design` | UX/UI, 아키텍처 설계 (선택) |
| `/context-aware-workflow:start` | `/cw:start` | 워크플로우 시작 |
| `/context-aware-workflow:status` | `/cw:status` | 진행 상태 표시 |
| `/context-aware-workflow:next` | `/cw:next` | 다음 단계 실행 (자동 병렬) |
| `/context-aware-workflow:review` | `/cw:review` | 코드 리뷰 |
| `/context-aware-workflow:fix` | `/cw:fix` | 리뷰 결과 수정 |
| `/context-aware-workflow:check` | `/cw:check` | 규칙 준수 검증 |
| `/context-aware-workflow:context` | `/cw:context` | 컨텍스트 관리 |
| `/context-aware-workflow:tidy` | `/cw:tidy` | Tidy First 분석/적용 |
| `/context-aware-workflow:reflect` | `/cw:reflect` | Ralph Loop 개선 사이클 |
| `/context-aware-workflow:evolve` | `/cw:evolve` | **인스팅트 진화** (NEW v2.0) |
| `/context-aware-workflow:sync` | `/cw:sync` | Serena 메모리 동기화 |
| `/context-aware-workflow:worktree` | `/cw:worktree` | Git Worktree 관리 |
| `/context-aware-workflow:merge` | `/cw:merge` | Worktree 브랜치 병합 |
| `/context-aware-workflow:qaloop` | `/cw:qaloop` | **QA 루프 (빌드→리뷰→수정)** |
| `/context-aware-workflow:ultraqa` | `/cw:ultraqa` | **자동 QA (빌드/테스트/린트)** |
| `/context-aware-workflow:research` | `/cw:research` | **통합 연구 모드** |
| `/context-aware-workflow:analytics` | `/cw:analytics` | **비용 분석 및 최적화** (NEW v2.0) |

---

## 💡 핵심 개념

### 1. 작업 계획 (.caw/task_plan.md)

모든 개발 작업의 중심이 되는 구조화된 계획 문서입니다. `.caw/` 폴더에 저장됩니다.

```markdown
# Task Plan: JWT 인증 시스템

## Metadata
| Field | Value |
|-------|-------|
| **Created** | 2024-01-15 14:30 |
| **Status** | In Progress |

## Execution Phases

### Phase 1: 설정
**Phase Deps**: -

| # | Step | Status | Agent | Deps | Notes |
|---|------|--------|-------|------|-------|
| 1.1 | JWT 라이브러리 설치 | ✅ Complete | Builder | - | jsonwebtoken@9.0 |
| 1.2 | 환경 변수 설정 | 🔄 In Progress | Builder | 1.1 | |

### Phase 2: 구현
**Phase Deps**: phase 1

| # | Step | Status | Agent | Deps | Notes |
|---|------|--------|-------|------|-------|
| 2.1 | 토큰 생성 함수 | ⏳ Pending | Builder | - | |
| 2.2 | 토큰 검증 함수 | ⏳ Pending | Builder | 2.1 | |
```

**상태 아이콘**:
| 아이콘 | 상태 | 설명 |
|--------|------|------|
| ⏳ | Pending | 대기 중 |
| 🔄 | In Progress | 진행 중 |
| ✅ | Complete | 완료 |
| ❌ | Blocked/Failed | 차단됨/실패 |
| ⏭️ | Skipped | 건너뜀 |

### 2. 컨텍스트 계층

| 계층 | 설명 | 토큰 영향 | 관리 명령 |
|------|------|----------|-----------|
| **Active** | 현재 편집 중인 파일 | 높음 (전체 내용) | `context add` |
| **Project** | 읽기 전용 참조 파일 | 중간 | `context add --project` |
| **Packed** | 인터페이스만 요약 | 낮음 | `context pack` |
| **Archived** | 저장만, 로드 안 함 | 없음 | `context remove` |

### 3. 자동 병렬 실행

CAW는 기본적으로 **자동 병렬 실행**을 지원합니다:

```
/cw:next 실행 시:
1. dependency-analyzer로 실행 가능한 step 분석
2. 병렬 가능 step 개수 확인:
   - 0개: "No runnable steps" 메시지
   - 1개: 단일 step 실행 (blocking)
   - ≥2개: 자동 background agent 병렬 실행
```

### 4. 티어별 모델 라우팅

에이전트는 작업 복잡도에 따라 자동으로 최적 모델을 선택합니다:

| 복잡도 점수 | 모델 | 용도 |
|------------|------|------|
| ≤ 0.3 | Haiku | 간단한 작업, 보일러플레이트 |
| 0.3 - 0.7 | Sonnet | 일반적인 구현 작업 |
| > 0.7 | Opus | 복잡한 로직, 보안 관련 |

---

## 📄 초기화 고급 기능

### 개요

v1.9.0에서 `/cw:init` 명령어에 강력한 문서 자동 생성 기능이 추가되었습니다. oh-my-claudecode의 deepinit 패턴을 도입하여 AI 에이전트를 위한 프로젝트 문서화를 자동화합니다.

### GUIDELINES.md 생성 (`--with-guidelines`)

워크플로우 가이드라인 문서를 자동 생성합니다.

```bash
# GUIDELINES.md 생성
/cw:init --with-guidelines

# 축약형
/cw:init -g
```

#### 생성되는 내용

| 섹션 | 설명 |
|------|------|
| **Workflow Rules** | CAW 워크플로우 규칙 및 Tidy First 원칙 |
| **Agent Usage** | 에이전트 사용 가이드라인 및 모델 라우팅 |
| **Project Context** | 감지된 프레임워크, 주요 파일, 규약 |
| **Quality Gates** | 품질 검증 기준 |
| **Commands Reference** | 주요 명령어 참조 |

#### 출력 예시

```markdown
# CAW Workflow Guidelines

> Auto-generated by /cw:init --with-guidelines on 2024-01-15T14:30:00Z
> Project: my-express-app (nodejs)

## Workflow Rules
### 1. Initialization
- Always ensure `.caw/` environment exists...

## Project-Specific Context
### Detected Environment
- **TypeScript** (language): 5.3.0
- **Express** (backend): 4.18.0
- **Jest** (testing): 29.7.0
```

### Deep Initialization (`--deep`)

각 디렉토리에 `AGENTS.md` 파일을 계층적으로 생성합니다 (oh-my-claudecode의 deepinit 패턴).

```bash
# AGENTS.md 계층 생성
/cw:init --deep

# 축약형
/cw:init -d
```

#### 생성되는 구조

```
project/
├── AGENTS.md                    # Root overview (<!-- Parent: - -->)
├── src/
│   ├── AGENTS.md               # <!-- Parent: ../AGENTS.md -->
│   ├── components/
│   │   └── AGENTS.md           # <!-- Parent: ../AGENTS.md -->
│   └── utils/
│       └── AGENTS.md           # <!-- Parent: ../AGENTS.md -->
└── tests/
    └── AGENTS.md               # <!-- Parent: ../AGENTS.md -->
```

#### AGENTS.md 내용

| 섹션 | 설명 |
|------|------|
| **Purpose** | 디렉토리 목적 설명 |
| **Key Files** | 주요 파일 및 설명 |
| **Subdirectories** | 하위 디렉토리 링크 |
| **For AI Agents** | AI 에이전트를 위한 작업 지침 |
| **Dependencies** | 내부/외부 의존성 |

#### 특징

1. **계층적 링크**: `<!-- Parent: ../AGENTS.md -->` 태그로 부모-자식 관계 표시
2. **수동 내용 보존**: `<!-- MANUAL: -->` 마커 아래 내용은 재생성 시 유지
3. **자동 제외**: `node_modules`, `.git`, `dist`, `build` 등 자동 제외
4. **병렬 처리**: 같은 레벨 디렉토리는 병렬로 처리

### 전체 초기화

```bash
# 모든 문서화 기능 사용
/cw:init --with-guidelines --deep

# 리셋 후 전체 초기화
/cw:init --reset --with-guidelines --deep

# 상세 출력과 함께
/cw:init --with-guidelines --deep --verbose
```

### 생성 파일 위치

| 파일 | 위치 | 설명 |
|------|------|------|
| `context_manifest.json` | `.caw/` | 프로젝트 컨텍스트 (기존) |
| `GUIDELINES.md` | `.caw/` | 워크플로우 가이드라인 |
| `AGENTS.md` | 각 디렉토리 | 디렉토리별 AI 문서 |

### 증분 업데이트

재실행 시 자동으로 증분 업데이트됩니다:

```
/cw:init --deep 재실행 시:
├─ 디렉토리 수정됨 > AGENTS.md 수정됨 → 재생성
├─ 새 디렉토리 발견 → 새 AGENTS.md 생성
├─ 디렉토리 삭제됨 → 고아 AGENTS.md 보고 (자동 삭제 안 함)
└─ <!-- MANUAL: --> 아래 내용 → 항상 보존
```

### 사용 시나리오

| 시나리오 | 명령어 |
|----------|--------|
| 새 프로젝트 첫 설정 | `/cw:init --with-guidelines --deep` |
| 팀원 온보딩 문서 | `/cw:init --with-guidelines` |
| AI를 위한 코드베이스 문서화 | `/cw:init --deep` |
| 대규모 리팩토링 후 | `/cw:init --reset --deep` |
| CI/CD에서 문서 검증 | `/cw:init --json --deep` |

---

## 🔄 QA Loop & UltraQA

### `/cw:qaloop` - QA 루프

자동 빌드 → 리뷰 → 수정 사이클을 반복하여 품질 기준을 충족할 때까지 실행합니다.

#### 사용법

```bash
# 기본 사용 - 현재 step QA
/cw:qaloop

# 특정 step QA
/cw:qaloop --step 2.3

# 전체 phase QA
/cw:qaloop --phase 2

# 커스텀 설정
/cw:qaloop --max-cycles 5 --severity major
```

#### 파라미터

| 파라미터 | 기본값 | 설명 |
|----------|--------|------|
| `--step N.M` | 현재 | 특정 step 대상 |
| `--phase N` | - | 전체 phase 대상 |
| `--max-cycles` | 3 | 최대 반복 횟수 |
| `--severity` | major | 최소 수정 심각도 |
| `--exit-on` | major | 이 심각도 없으면 종료 |
| `--continue` | false | 저장된 상태에서 재개 |

#### 실행 플로우

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌──────────────┐
│   BUILD     │ ──► │   REVIEW    │ ──► │    FIX      │ ──► │ EXIT CHECK   │
│  (Execute)  │     │ (Analyze)   │     │ (Correct)   │     │              │
└─────────────┘     └─────────────┘     └─────────────┘     └──────┬───────┘
      ▲                                                            │
      │                                                            │
      └──────────────────── Issues remain? ────────────────────────┘

종료 조건:
✅ Critical/Major 이슈 없음 (리뷰 통과)
⏱️ Max cycles 도달
🔁 동일 이슈 3회 반복 (stalled)
❌ 빌드 실패 지속
```

#### 출력 예시

```
🔄 /cw:qaloop --step 2.3

Cycle 1/3 ━━━━━━━━━━━━━━━━━━━━
  📦 Build...     ✅ Success
  🔍 Review...    ⚠️ 2 major, 1 minor
  🔧 Fixing...    ✅ 2 fixed

Cycle 2/3 ━━━━━━━━━━━━━━━━━━━━
  📦 Build...     ✅ Success
  🔍 Review...    ✅ 0 major, 1 minor

✅ QA Loop Complete

📊 Summary:
  • Cycles: 2 / 3
  • Issues found: 3 (2 major, 1 minor)
  • Issues fixed: 2
  • Remaining: 1 minor (below threshold)
```

---

### `/cw:ultraqa` - UltraQA

지능형 진단과 타겟 수정을 통한 고급 자동 QA입니다.

#### 사용법

```bash
# 기본 - 모든 이슈 자동 감지 및 수정
/cw:ultraqa

# 특정 타입 대상
/cw:ultraqa --target build      # 빌드 오류
/cw:ultraqa --target test       # 테스트 실패
/cw:ultraqa --target lint       # 린트 이슈
/cw:ultraqa --target all        # 모두 (기본)

# 딥 진단 모드
/cw:ultraqa --deep              # Opus로 철저한 분석

# 커스텀 설정
/cw:ultraqa --max-cycles 5 --target test
```

#### 파라미터

| 파라미터 | 기본값 | 설명 |
|----------|--------|------|
| `--target` | all | 타겟: build, test, lint, all |
| `--max-cycles` | 5 | 최대 수정 시도 횟수 |
| `--deep` | false | 딥 진단 (Opus 사용) |
| `--continue` | false | 저장된 상태에서 재개 |

#### 출력 예시

```
🔬 /cw:ultraqa --target all

Detecting issues...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📦 Build:  ❌ 3 errors
🧪 Tests:  ⚠️ 2 failures
📝 Lint:   ⚠️ 5 issues
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Cycle 1/5 ━━━━━━━━━━━━━━━━━━━━
  🔍 Diagnosing...

  📋 Root Cause Analysis:
  ┌────────────────────────────────────────────────
  │ Build Error #1: Missing type export
  │   Root: UserType not exported from types.ts
  │   Fix: Export UserType from types.ts:15
  └────────────────────────────────────────────────

  🔧 Applying fixes...
      ✅ types.ts: Added export

  🔄 Verifying...
      📦 Build: ✅ Success

✅ UltraQA Complete

📊 Summary:
  • Build errors: 3 → 0 ✅
  • Test failures: 2 → 0 ✅
  • Lint issues: 5 → 1 ⚠️
```

---

### QA Loop vs UltraQA 비교

| 기능 | /cw:qaloop | /cw:ultraqa |
|------|------------|-------------|
| 초점 | 코드 품질 리뷰 | 특정 오류 타입 |
| 대상 | 리뷰 이슈 전반 | Build/Test/Lint |
| 진단 | 표준 리뷰 | 딥 근본 원인 분석 |
| 최적 용도 | 품질 게이트 | CI 실패 수정 |

---

## 🔬 Research Mode

### 개요

`/cw:research`는 내부 코드베이스 분석과 외부 문서 연구를 통합하는 강력한 연구 도구입니다.

### 사용법

```bash
# 기본 연구 (내부 + 외부)
/cw:research "JWT 인증 베스트 프랙티스"

# 내부만 (코드베이스 탐색)
/cw:research "인증 처리 방식" --internal

# 외부만 (문서/웹)
/cw:research "React Server Components" --external

# 깊이 조절
/cw:research "데이터베이스 커넥션 풀링" --depth deep

# 연구 결과 저장
/cw:research "GraphQL 스키마 설계" --save context-graphql
```

### 파라미터

| 파라미터 | 기본값 | 설명 |
|----------|--------|------|
| `--internal` | false | 내부 코드베이스만 분석 |
| `--external` | false | 외부 문서만 검색 |
| (둘 다 없음) | - | 내부 + 외부 모두 |
| `--depth` | normal | 연구 깊이: shallow, normal, deep |
| `--save` | - | 연구 결과 저장 이름 |
| `--load` | - | 이전 연구 컨텍스트 로드 |

### 연구 깊이

| 깊이 | 시간 | 내부 분석 | 외부 검색 |
|------|------|----------|----------|
| **shallow** | ~1-2분 | 키워드 매칭 | 상위 3-5 결과 |
| **normal** | ~3-5분 | 심볼 분석 + 참조 | 상위 10 결과 + 페이지 |
| **deep** | ~10-15분 | 전체 아키텍처 분석 | 다중 쿼리 + 검증 |

### 출력 예시

```
🔬 /cw:research "JWT 인증" --depth normal

Analyzing query...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[1/4] Internal Research
      🔍 Searching symbols...    Found 12 matches
      📁 Analyzing files...      3 relevant files
      🔗 Tracing references...   8 usages found
      ✅ Internal analysis complete

[2/4] External Research
      🌐 Web searching...        15 results
      📖 Fetching docs...        5 pages analyzed
      ✅ External research complete

[3/4] Synthesis
      🔄 Comparing findings...
      📊 Identifying gaps...
      💡 Generating recommendations...
      ✅ Synthesis complete

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 Research Complete

## Summary:
- Internal: 3 files, 12 symbols (HS256, 24h expiry)
- External: RS256 권장, 15-60분 expiry

## Gap Analysis:
| Aspect | Current | Recommended |
|--------|---------|-------------|
| Algorithm | HS256 | RS256 |
| Expiry | 24h | 15-60m |

## Recommendations:
1. 🔴 RS256으로 마이그레이션 (보안 강화)
2. 🟡 토큰 expiry 축소 (15-60분)
3. 🟢 Refresh 토큰 로테이션 추가

📁 Saved to: .caw/research/jwt-auth-20240115.md
```

### 워크플로우 연계

```bash
# 연구 후 구현에 활용
/cw:research "인증 패턴" --save auth-research
/cw:start "OAuth 구현" --research-context auth-research
```

---

## 🔄 Autonomous Loop

### 개요

`/cw:loop`는 작업이 완료될 때까지 자율적으로 반복 실행하는 명령어입니다. 5단계 오류 복구 시스템을 통해 자동으로 문제를 해결합니다.

### 사용법

```bash
# 기본 사용
/cw:loop "JWT 인증 구현"

# 중단된 루프 재개
/cw:loop --continue

# 커스텀 설정
/cw:loop "다크 모드 추가" --max-iterations 30
/cw:loop "린트 오류 수정" --completion-promise "ALL_FIXED"

# 엄격 모드 (자동 수정 비활성화)
/cw:loop "중요 보안 수정" --no-auto-fix

# 회고 단계 건너뛰기
/cw:loop "빠른 리팩토링" --no-reflect

# 상세 출력
/cw:loop "복잡한 기능" --verbose
```

### 파라미터

| 파라미터 | 기본값 | 설명 |
|----------|--------|------|
| `--max-iterations` | 20 | 최대 반복 횟수 |
| `--completion-promise` | "DONE" | 완료 감지 키워드 |
| `--continue` | false | 저장된 상태에서 재개 |
| `--auto-fix` | true | Fixer 에이전트로 오류 복구 |
| `--no-auto-fix` | - | 자동 수정 비활성화 |
| `--reflect` | true | 완료 후 /cw:reflect 실행 |
| `--no-reflect` | - | 회고 단계 건너뛰기 |
| `--verbose` | false | 상세 진행 상황 출력 |

### 종료 조건

| 조건 | 상태 | 설명 |
|------|------|------|
| Completion Promise | `completed` | 출력에 완료 키워드 포함 |
| All Steps Complete | `completed` | task_plan.md의 모든 step이 ✅ |
| Max Iterations | `max_iterations_reached` | 최대 반복 횟수 도달 |
| Consecutive Failures | `failed` | 3회 이상 연속 실패 |
| Critical Error | `failed` | 복구 불가능한 오류 |
| Manual Abort | `paused` | 사용자가 중단 |

### 5단계 오류 복구

```
Level 1: Retry      → 동일 step 재시도
Level 2: Fixer      → Fixer-Haiku로 자동 수정
Level 3: Alternative → Planner-Haiku로 대안 제시
Level 4: Skip       → 비차단 step 건너뛰기
Level 5: Abort      → 상태 저장 후 중단
```

### /cw:auto vs /cw:loop 비교

| 기능 | /cw:loop | /cw:auto |
|------|----------|----------|
| 초점 | 완료될 때까지 반복 | 전체 워크플로우 단계 |
| 종료 조건 | 유연 (promise/steps/max) | 단계 완료 |
| 오류 복구 | 5단계 점진적 복구 | 중단 및 보고 |
| 리뷰/수정 | 선택적 (복구 통해) | 내장 단계 |
| 적합한 용도 | 집중된 단일 작업 | 전체 기능 개발 |

---

## 🐝 Swarm 병렬 실행 (NEW v2.0.0)

### 개요

`/cw:swarm`은 여러 독립적인 작업을 병렬로 실행하는 에이전트 스웜 모드입니다.

### 사용법

```bash
# 기본 사용 - 여러 작업 병렬 실행
/cw:swarm "task1" "task2" "task3"

# 워커 수 제한
/cw:swarm --workers 4 "taskA" "taskB" "taskC" "taskD" "taskE"

# 타임아웃 설정
/cw:swarm --timeout 120 "long-task1" "long-task2"

# 결과 자동 병합
/cw:swarm --merge "feature-A" "feature-B"

# 작업 계획에서 병렬 가능한 step 추출
/cw:swarm --from-plan

# 실행 미리보기
/cw:swarm --dry-run "task1" "task2"
```

### 파라미터

| 파라미터 | 기본값 | 설명 |
|----------|--------|------|
| `--workers N` | 작업 수 | 최대 동시 워커 수 |
| `--timeout S` | 300 | 작업당 타임아웃 (초) |
| `--merge` | false | 완료 후 결과 자동 병합 |
| `--from-plan` | false | task_plan.md에서 병렬 step 추출 |
| `--worktrees` | false | 각 작업에 git worktree 할당 |
| `--dry-run` | false | 실행 없이 미리보기 |

### 실행 플로우

```
작업 분석
     │
     ▼
┌─────────────────────────────────────────────────┐
│ 독립성 검증 & 복잡도 분석                          │
│ → 병렬 가능: independent[]                       │
│ → 순차 필요: dependent[]                         │
└────────────────────┬────────────────────────────┘
                     │
     ┌───────────────┼───────────────┐
     ▼               ▼               ▼
┌─────────┐   ┌─────────┐   ┌─────────┐
│ Worker 1│   │ Worker 2│   │ Worker 3│
│ Task A  │   │ Task B  │   │ Task C  │
│ Context │   │ Context │   │ Context │
└────┬────┘   └────┬────┘   └────┬────┘
     │             │             │
     └─────────────┴─────────────┘
                   │
              Result Aggregation
```

### 출력 예시

```
Swarm Status
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Workers: 3/3 active | Timeout: 120s

[1] login API      ████████░░░░ 65%  builder-sonnet
[2] logout button  ██████████░░ 85%  builder-haiku
[3] auth review    ████░░░░░░░░ 35%  Reviewer

Elapsed: 45s | Est. remaining: 30s
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Swarm Complete

[1] login API      ✅ Complete (52s)
[2] logout button  ✅ Complete (38s)
[3] auth review    ✅ Complete (67s)

Tokens: 45,200 | Cost: $0.42 | Duration: 1m 7s
Speedup: 2.7x vs sequential
```

### /cw:swarm vs /cw:next --parallel 비교

| 기능 | /cw:swarm | /cw:next --parallel |
|------|-----------|---------------------|
| 대상 | 임의 작업 | task_plan.md step |
| 에이전트 선택 | 자동 분석 | 미리 정의됨 |
| Worktree 지원 | 선택적 | 자동 |
| 충돌 해결 | 대화형 | 자동 |
| 적합한 용도 | 독립 기능 | 계획된 병렬 step |

---

## 📊 Pipeline 명시적 파이프라인 (NEW v2.0.0)

### 개요

`/cw:pipeline`은 명시적으로 정의된 스테이지를 순차적으로 실행하는 파이프라인 모드입니다.

### 사용법

```bash
# 인라인 스테이지 정의
/cw:pipeline --stages "plan,build,review,deploy"

# 설정 파일에서 로드
/cw:pipeline --config pipeline.yaml

# 중단된 파이프라인 재개
/cw:pipeline --resume

# 특정 스테이지부터 시작
/cw:pipeline --from build

# 특정 스테이지까지 실행
/cw:pipeline --to review

# 스테이지 건너뛰기
/cw:pipeline --skip-stage test

# 실행 미리보기
/cw:pipeline --dry-run
```

### 파이프라인 설정 파일

```yaml
# .caw/pipeline.yaml
name: feature-implementation
stages:
  - name: plan
    agent: Planner
    timeout: 300
    checkpoint: true

  - name: build
    agent: Builder
    timeout: 600
    depends_on: plan
    parallel_substeps: true

  - name: review
    agent: Reviewer
    timeout: 300
    depends_on: build
    gate: true  # Must pass to continue

  - name: deploy
    agent: builder-haiku
    timeout: 120
    depends_on: review
    optional: true
```

### 파라미터

| 파라미터 | 기본값 | 설명 |
|----------|--------|------|
| `--stages` | - | 쉼표로 구분된 스테이지 목록 |
| `--config` | - | 설정 파일 경로 |
| `--resume` | false | 마지막 체크포인트에서 재개 |
| `--from STAGE` | - | 특정 스테이지부터 시작 |
| `--to STAGE` | - | 특정 스테이지까지 실행 |
| `--skip-stage` | - | 스테이지 건너뛰기 |
| `--dry-run` | false | 미리보기만 |
| `--eco` | false | 에코 모드 (비용 절감) |

### 스테이지 속성

| 속성 | 설명 |
|------|------|
| `checkpoint` | 완료 후 상태 저장 (재개 가능) |
| `gate` | 통과해야 다음 스테이지 진행 |
| `optional` | 건너뛸 수 있음 |
| `retries` | 실패 시 재시도 횟수 |
| `parallel_substeps` | 스테이지 내 병렬 실행 허용 |

### 출력 예시

```
Pipeline: feature-implementation
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Stage 1/4: plan
─────────────────────────────────────────────
Agent: Planner (Sonnet)
Status: ████████████ 100% Complete
Duration: 2m 15s
Checkpoint: ✅ Saved

Stage 2/4: build
─────────────────────────────────────────────
Agent: Builder (Opus)
Status: ████████░░░░ 65% In Progress
Duration: 4m 32s (ongoing)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Progress: 2/4 stages | 41% overall
```

### 내장 파이프라인

```bash
/cw:pipeline --config standard   # plan → build → test → review
/cw:pipeline --config quickfix   # fix → test
/cw:pipeline --config release    # plan → build → test → review → security-scan → deploy
```

---

## 📈 Analytics 비용 분석 (NEW v2.0.0)

### 개요

`/cw:analytics`는 토큰 사용량, 비용 분석, 워크플로우 효율성 지표를 제공합니다.

### 사용법

```bash
# 전체 대시보드
/cw:analytics

# 비용 분석
/cw:analytics --cost

# 토큰 사용량 분석
/cw:analytics --tokens

# 세션 비교
/cw:analytics --sessions

# 트렌드 분석
/cw:analytics --trends

# JSON으로 내보내기
/cw:analytics --export
```

### 파라미터

| 파라미터 | 설명 |
|----------|------|
| `--cost` | 모델별 비용 분석 |
| `--tokens` | 토큰 사용량 분석 |
| `--sessions` | 다중 세션 비교 |
| `--trends` | 시간별 트렌드 |
| `--export` | JSON 파일로 내보내기 |

### 출력 예시

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
               WORKFLOW ANALYTICS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Session: abc123 | Duration: 1h 30m

TOKEN USAGE
───────────────────────────────────────────────
Input:   45,000 tokens (79%)
Output:  12,000 tokens (21%)
Total:   57,000 tokens

COST BREAKDOWN
───────────────────────────────────────────────
Model        Tokens     Cost      %
─────────────────────────────────────────
Haiku        15,000     $0.02     4%
Sonnet       35,000     $0.15     29%
Opus          7,000     $0.35     67%
─────────────────────────────────────────
TOTAL        57,000     $0.52    100%

MODEL DISTRIBUTION
───────────────────────────────────────────────
Haiku:  ██████░░░░░░░░░░░░░░ 26%
Sonnet: ████████████░░░░░░░░ 61%
Opus:   ███░░░░░░░░░░░░░░░░░ 13%

OPTIMIZATION INSIGHTS
───────────────────────────────────────────────
• Opus usage for 13% of tokens drove 67% of cost
• Consider: Use Sonnet for initial review, Opus for deep analysis
• Eco mode would save ~$0.18 (35%) on this workflow
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 비용 계산 (참고)

```python
PRICING = {
    "haiku": {"input": 0.25, "output": 1.25},    # per 1M tokens
    "sonnet": {"input": 3.00, "output": 15.00},
    "opus": {"input": 15.00, "output": 75.00}
}
```

---

## 🧹 Tidy First 방법론

Kent Beck의 **Tidy First** 방법론을 적용하여 코드 품질을 향상시킵니다.

### 핵심 원칙

> "구조적 변경과 동작 변경을 같은 커밋에 혼합하지 마라.
> 둘 다 필요할 때는 항상 구조적 변경을 먼저 하라."
> — Kent Beck

### Step Type 분류

| 아이콘 | Type | 설명 | 커밋 프리픽스 |
|--------|------|------|--------------|
| 🧹 | Tidy | 구조적 변경 (동작 변화 없음) | `[tidy]` |
| 🔨 | Build | 동작 변경 (새 기능, 버그 수정) | `[feat]`, `[fix]` |

### Tidy Step 예시

| 작업 | Type | 설명 |
|------|------|------|
| 변수/함수 이름 변경 | 🧹 Tidy | 명확한 네이밍 |
| 메서드 추출 | 🧹 Tidy | 중복 코드 분리 |
| 파일 재구성 | 🧹 Tidy | 디렉토리 정리 |
| 사용하지 않는 코드 제거 | 🧹 Tidy | Dead code 삭제 |

### task_plan.md 형식 (Tidy First)

```markdown
### Phase 2: Core Implementation
**Phase Deps**: phase 1

| # | Step | Type | Status | Agent | Deps | Notes |
|---|------|------|--------|-------|------|-------|
| 2.0 | 기존 auth 코드 정리 | 🧹 Tidy | ⏳ | Builder | - | 네이밍 개선 |
| 2.1 | JWT 유틸리티 구현 | 🔨 Build | ⏳ | Builder | 2.0 | |
| 2.2 | 토큰 검증 함수 | 🔨 Build | ⏳ | Builder | 2.1 | |
```

### /cw:tidy 명령어

```bash
/cw:tidy                  # 현재 step 대상 분석
/cw:tidy --scope src/     # 특정 디렉토리 분석
/cw:tidy --preview        # 미리보기만 (변경 없음)
/cw:tidy --apply          # 변경 적용
/cw:tidy --add-step       # Tidy step 추가
```

### 분석 카테고리

| 카테고리 | 탐지 항목 |
|----------|----------|
| **Naming** | 불명확한 변수/함수 이름 (`val`, `cb`, `e`) |
| **Duplication** | 중복 코드 블록 (>3줄 동일) |
| **Dead Code** | 사용되지 않는 함수, 도달 불가 코드 |
| **Structure** | 대형 함수 (>50줄), 깊은 중첩 (>3레벨) |

---

## 📌 명령어 상세

### `/cw:init` - 환경 초기화

CAW 환경을 초기화합니다. `/cw:start` 실행 시 자동으로 호출되지만, 수동으로도 실행 가능합니다.

#### 사용법

```bash
# 환경 초기화 (자동 탐지)
/cw:init

# 환경 리셋 (기존 환경 삭제 후 재생성)
/cw:init --reset

# 특정 프로젝트 타입 지정
/cw:init --type typescript

# GUIDELINES.md 생성 (NEW v1.9.0)
/cw:init --with-guidelines
/cw:init -g

# 계층적 AGENTS.md 생성 (NEW v1.9.0)
/cw:init --deep
/cw:init -d

# 전체 초기화 (NEW v1.9.0)
/cw:init --with-guidelines --deep
```

#### 플래그 (v1.9.0 확장)

| 플래그 | 축약 | 설명 |
|--------|------|------|
| `--reset` | | 기존 환경 삭제 후 재생성 |
| `--type <type>` | | 프로젝트 타입 지정 |
| `--with-guidelines` | `-g` | `.caw/GUIDELINES.md` 생성 **(NEW)** |
| `--deep` | `-d` | 계층적 `AGENTS.md` 생성 **(NEW)** |
| `--verbose` | `-v` | 상세 출력 |
| `--quiet` | `-q` | 오류만 출력 |
| `--json` | | JSON 형식 출력 |

#### Bootstrapper 에이전트 동작

1. **환경 확인**: `.caw/` 디렉토리 존재 여부 확인
2. **프로젝트 분석**: 파일 구조, 기술 스택, 패키지 매니저 탐지
3. **디렉토리 생성**: `.caw/`, `.caw/design/`, `.caw/archives/`, `.caw/knowledge/`, `.caw/insights/`
4. **매니페스트 생성**: `context_manifest.json` 초기화
5. **GUIDELINES.md 생성** (`--with-guidelines`): 워크플로우 가이드라인 문서 **(NEW)**
6. **AGENTS.md 계층 생성** (`--deep`): 각 디렉토리에 AI 문서 **(NEW)**

자세한 내용은 [초기화 고급 기능](#-초기화-고급-기능-new) 섹션을 참조하세요.

---

### `/cw:start` - 워크플로우 시작

워크플로우 세션을 시작하고 `.caw/task_plan.md`를 생성합니다.

#### 사용법

```bash
# 새 작업 시작 (가장 일반적)
/cw:start "사용자 인증 시스템 구현"

# Plan Mode 계획 가져오기
/cw:start --from-plan

# 특정 계획 파일 지정
/cw:start --plan-file docs/feature-plan.md
```

---

### `/cw:loop` - 자율 반복 실행 (NEW)

작업이 완료될 때까지 자율적으로 반복 실행합니다. 5단계 오류 복구 시스템을 포함합니다.

#### 사용법

```bash
# 기본 사용
/cw:loop "작업 설명"

# 중단된 루프 재개
/cw:loop --continue

# 커스텀 설정
/cw:loop "작업" --max-iterations 30
/cw:loop "작업" --no-auto-fix
/cw:loop "작업" --verbose
```

#### 플래그

| 플래그 | 설명 |
|--------|------|
| `--max-iterations N` | 최대 반복 횟수 (기본: 20) |
| `--completion-promise` | 완료 감지 키워드 |
| `--continue` | 저장된 상태에서 재개 |
| `--no-auto-fix` | 자동 수정 비활성화 |
| `--no-reflect` | 회고 단계 건너뛰기 |
| `--verbose` | 상세 진행 상황 출력 |

---

### `/cw:next` - 다음 단계 실행 (자동 병렬)

Builder 에이전트를 호출하여 다음 Pending 단계를 자동 구현합니다. **자동 병렬 실행이 기본값입니다.**

#### 사용법

```bash
# 기본 - 자동 병렬 (DEFAULT)
/cw:next                      # 병렬 가능 step ≥2개 → 자동 background 병렬 실행
/cw:next --sequential         # 강제 순차 실행 (병렬 가능해도 단일 step만)
/cw:next --step 2.3           # 특정 step 실행

# Phase 기반 실행
/cw:next phase 1              # Phase 1 실행 (자동 병렬 적용)
/cw:next --sequential phase 1 # Phase 1 순차 실행
/cw:next --parallel phase 1   # Phase 1 강제 병렬 (1개여도 background)
/cw:next --worktree phase 2   # Phase 2용 worktree 생성

# 배치 제어
/cw:next --batch 3            # 최대 3개 step 병렬 실행
/cw:next --all                # 현재 phase 전체 순차 실행
```

#### 플래그

| 플래그 | 설명 |
|--------|------|
| (없음) | **자동 병렬**: 실행 가능 step ≥2개면 background agent 병렬 실행 |
| `--sequential` | 강제 순차 실행 (병렬 가능해도 단일 step만) |
| `--parallel` | 강제 병렬 실행 (1개여도 background agent 사용) |
| `--all` | 현재 phase 전체 순차 실행 |
| `--worktree` | Phase 단위 git worktree 생성 |
| `--step N.M` | 특정 step 실행 |
| `--batch N` | 최대 N개 병렬 실행 (기본: 5) |
| `phase N` | Phase 번호 지정 |

---

### `/cw:review` - 코드 리뷰

Reviewer 에이전트를 호출하여 코드 품질을 분석합니다.

#### 사용법

```bash
# 현재 Phase 리뷰 (기본)
/cw:review

# 특정 Phase 리뷰
/cw:review --phase 2

# 딥 리뷰 (보안/성능 집중)
/cw:review --deep

# 특정 영역 집중
/cw:review --focus security
/cw:review --focus performance
```

---

### `/cw:fix` - 리뷰 결과 수정

Reviewer 결과를 기반으로 코드를 자동 또는 대화형으로 수정합니다.

#### 사용법

```bash
# 간단한 이슈 자동 수정 (기본)
/cw:fix

# 대화형 모드 (수정 전 확인)
/cw:fix --interactive

# 특정 카테고리만 수정
/cw:fix --category docs       # 문서 (JSDoc 등)
/cw:fix --category style      # 스타일/린트
/cw:fix --category constants  # 매직 넘버 상수화

# 복잡한 리팩토링 (Fixer 에이전트 사용)
/cw:fix --deep
```

---

### `/cw:tidy` - Tidy First 분석/적용

Kent Beck의 Tidy First 방법론을 적용하여 구조적 개선을 분석하고 적용합니다.

#### 사용법

```bash
# 현재 step 대상 분석 (기본)
/cw:tidy

# 특정 디렉토리/파일 분석
/cw:tidy --scope src/auth/

# 미리보기만 (변경 없음)
/cw:tidy --preview

# 분석된 변경 적용
/cw:tidy --apply

# Tidy step을 task_plan.md에 추가
/cw:tidy --add-step

# 변경 적용 후 커밋
/cw:tidy --commit
```

---

### `/cw:reflect` - Ralph Loop 개선 사이클

작업 완료 후 지속적 개선 사이클을 실행합니다.

#### 사용법

```bash
# 마지막 완료 작업 회고
/cw:reflect

# 특정 step 회고
/cw:reflect --task 2.3

# 전체 워크플로우 회고
/cw:reflect --full
```

#### Ralph Loop 단계

**RALPH** = **R**eflect → **A**nalyze → **L**earn → **P**lan → **H**abituate

```
📝 REFLECT  - 무엇이 일어났는지 검토
🔍 ANALYZE  - 패턴과 이슈 식별
💡 LEARN    - 교훈 추출
📋 PLAN     - 개선 계획 수립
🔧 HABITUATE - 향후 작업에 적용
```

---

### `/cw:sync` - Serena 메모리 동기화

CAW 워크플로우 지식을 Serena MCP 메모리 시스템과 동기화합니다.

#### 사용법

```bash
# 양방향 동기화 (기본)
/cw:sync

# CAW → Serena 업로드
/cw:sync --to-serena

# Serena → CAW 복원
/cw:sync --from-serena

# 동기화 상태 확인
/cw:sync --status

# 강제 덮어쓰기
/cw:sync --to-serena --force
```

#### 동기화 카테고리

| 카테고리 | CAW 소스 | Serena 메모리 |
|----------|----------|---------------|
| Domain Knowledge | `.caw/knowledge/**` | `domain_knowledge` |
| Lessons Learned | `.caw/learnings.md` | `lessons_learned` |
| Workflow Patterns | `.caw/knowledge/patterns.md` | `workflow_patterns` |
| Insights | `.caw/insights/**` | `caw_insights` |

---

### `/cw:worktree` - Git Worktree 관리

Phase 단위로 격리된 git worktree를 관리합니다.

#### 사용법

```bash
# Phase 기반 (PRIMARY)
/cw:worktree create phase 2          # Phase 2용 worktree 생성
/cw:worktree create phase 2,3,4      # 여러 phase worktree 생성

# 관리
/cw:worktree list                    # 모든 worktree 상태 표시
/cw:worktree clean                   # 완료된 worktree 제거
/cw:worktree clean --all             # 모든 CAW worktree 제거
```

---

### `/cw:merge` - Worktree 브랜치 병합

완료된 worktree 브랜치를 main 브랜치로 병합합니다.

#### 사용법

```bash
# 완료된 worktree 자동 감지 및 병합
/cw:merge

# 모든 phase worktree 병합 (의존성 순서)
/cw:merge --all

# 특정 phase 병합
/cw:merge phase 2

# 미리보기
/cw:merge --dry-run

# 충돌 해결 후 계속
/cw:merge --continue

# 병합 취소
/cw:merge --abort
```

---

### `/cw:qaloop` - QA 루프

자동 빌드 → 리뷰 → 수정 사이클입니다. 상세 내용은 [QA Loop & UltraQA](#-qa-loop--ultraqa) 섹션 참조.

```bash
/cw:qaloop                        # 현재 step QA
/cw:qaloop --step 2.3             # 특정 step
/cw:qaloop --phase 2              # 전체 phase
/cw:qaloop --max-cycles 5         # 최대 5회 반복
```

---

### `/cw:ultraqa` - UltraQA

지능형 자동 QA입니다. 상세 내용은 [QA Loop & UltraQA](#-qa-loop--ultraqa) 섹션 참조.

```bash
/cw:ultraqa                       # 모든 이슈 자동 수정
/cw:ultraqa --target build        # 빌드 오류만
/cw:ultraqa --target test         # 테스트 실패만
/cw:ultraqa --deep                # 딥 진단 (Opus)
```

---

### `/cw:research` - 통합 연구

내부 코드베이스 + 외부 문서 통합 연구입니다. 상세 내용은 [Research Mode](#-research-mode) 섹션 참조.

```bash
/cw:research "JWT 인증"           # 내부 + 외부 연구
/cw:research "auth" --internal    # 내부만
/cw:research "React" --external   # 외부만
/cw:research "설계" --depth deep  # 딥 연구
/cw:research "topic" --save name  # 결과 저장
```

---

### `/cw:swarm` - 병렬 에이전트 스웜 (NEW v2.0)

여러 독립적인 작업을 병렬로 실행합니다. 상세 내용은 [Swarm 병렬 실행](#-swarm-병렬-실행-new-v200) 섹션 참조.

```bash
/cw:swarm "task1" "task2" "task3"     # 병렬 실행
/cw:swarm --workers 2 "t1" "t2" "t3"  # 워커 수 제한
/cw:swarm --from-plan                  # 계획에서 추출
/cw:swarm --worktrees "f1" "f2"       # Worktree 격리
/cw:swarm --dry-run "t1" "t2"         # 미리보기
```

---

### `/cw:pipeline` - 명시적 파이프라인 (NEW v2.0)

정의된 스테이지를 순차적으로 실행합니다. 상세 내용은 [Pipeline 명시적 파이프라인](#-pipeline-명시적-파이프라인-new-v200) 섹션 참조.

```bash
/cw:pipeline --stages "plan,build,review"  # 인라인 정의
/cw:pipeline --config pipeline.yaml        # 설정 파일
/cw:pipeline --resume                      # 재개
/cw:pipeline --from build                  # 특정 스테이지부터
/cw:pipeline --eco                         # 비용 절감 모드
```

---

### `/cw:analytics` - 비용 분석 (NEW v2.0)

토큰 사용량과 비용을 분석합니다. 상세 내용은 [Analytics 비용 분석](#-analytics-비용-분석-new-v200) 섹션 참조.

```bash
/cw:analytics            # 전체 대시보드
/cw:analytics --cost     # 비용 분석
/cw:analytics --tokens   # 토큰 사용량
/cw:analytics --sessions # 세션 비교
/cw:analytics --export   # JSON 내보내기
```

---

### `/cw:evolve` - 인스팅트 진화 (NEW v2.0)

학습된 인스팅트를 명령어, 스킬, 에이전트로 진화시킵니다.

```bash
/cw:evolve                                    # 대화형 선택
/cw:evolve --preview                          # 후보만 표시
/cw:evolve --id <instinct-id>                 # 상세 보기
/cw:evolve --create command <id> <name>       # 명령어 생성
/cw:evolve --create skill <id> <name>         # 스킬 생성
/cw:evolve --create agent <id> <name>         # 에이전트 생성
```

#### 진화 유형

| 유형 | 조건 | 출력 |
|------|------|------|
| **Command** | 사용자 트리거, 3+ 단계 | `.caw/evolved/commands/*.md` |
| **Skill** | 자동 적용, 행동 규칙 | `.caw/evolved/skills/*/SKILL.md` |
| **Agent** | 복잡한 추론, 의사결정 | `.caw/evolved/agents/*.md` |

---

### `/cw:status` - 진행 상태 표시

현재 워크플로우 상태와 진행률을 표시합니다.

```bash
/cw:status
/cw:status --worktrees    # Worktree 상태 포함
/cw:status --hud          # HUD 표시 (NEW v2.0)
```

---

### `/cw:check` - 규칙 준수 검증

ComplianceChecker 에이전트를 호출하여 프로젝트 규칙 준수를 검증합니다.

```bash
/cw:check            # 전체 검사
/cw:check --workflow # 워크플로우 구조 검증
/cw:check --rules    # CLAUDE.md 규칙 검증
```

---

### `/cw:context` - 컨텍스트 관리

컨텍스트 파일을 관리합니다.

```bash
/cw:context show                          # 현재 상태 표시
/cw:context add src/auth/jwt.ts           # 파일 추가
/cw:context add package.json --project    # 읽기 전용 추가
/cw:context pack src/utils/helpers.ts     # 압축 (인터페이스만)
/cw:context prune                         # 오래된 파일 정리
```

---

## 🤖 에이전트

### 티어별 모델 라우팅

모든 핵심 에이전트는 작업 복잡도에 따라 자동으로 최적 모델을 선택합니다:

| 에이전트 | Haiku (≤0.3) | Sonnet (0.3-0.7) | Opus (>0.7) |
|----------|--------------|------------------|-------------|
| **Planner** | 간단한 계획 | 일반 계획 (기본) | 복잡한 아키텍처 |
| **Builder** | 보일러플레이트 | 일반 구현 | 복잡한 로직 (기본) |
| **Reviewer** | 빠른 스타일 체크 | 일반 리뷰 (기본) | 보안 심층 리뷰 |
| **Fixer** | 간단한 수정 | 리팩토링 (기본) | 복잡한 리팩토링 |

### 에이전트 목록 (18개)

**초기화 에이전트**:
| 에이전트 | 역할 | 출력물 |
|----------|------|--------|
| **Bootstrapper** | 환경 초기화, 프로젝트 탐지 | `.caw/context_manifest.json` |

**설계 에이전트**:
| 에이전트 | 역할 | 트리거 | 출력물 |
|----------|------|--------|--------|
| **Ideator** | 요구사항 발굴, Socratic 질문 | `/cw:brainstorm` | `.caw/brainstorm.md` |
| **Designer** | UX/UI 설계, 와이어프레임 | `/cw:design --ui` | `.caw/design/ux-ui.md` |
| **Architect** | 시스템 아키텍처 설계 | `/cw:design --arch` | `.caw/design/architecture.md` |
| **Analyst** | 요구사항 분석, 기능 명세 | `/cw:start --analyze` | `.caw/analysis.md` |

**구현 에이전트** (티어별 변형 포함):
| 에이전트 | 역할 | 트리거 | 티어 변형 |
|----------|------|--------|-----------|
| **Planner** | 실행 계획 생성 | `/cw:start` | Haiku, Sonnet, Opus |
| **Builder** | TDD 구현 및 테스트 | `/cw:next` | Haiku, Sonnet, Opus |
| **Reviewer** | 코드 품질 리뷰 | `/cw:review` | Haiku, Sonnet, Opus |
| **Fixer** | 리뷰 결과 수정/리팩토링 | `/cw:fix --deep` | Haiku, Sonnet, Opus |
| **ComplianceChecker** | 규칙 준수 검증 | `/cw:check` | - |

---

## 🧠 스킬 (20개)

CAW는 20개의 전문 스킬을 포함합니다:

### 핵심 스킬

| 스킬 | 설명 | 사용 시점 |
|------|------|----------|
| **reflect** | Ralph Loop 개선 사이클 | `/cw:reflect` |
| **serena-sync** | Serena 메모리 동기화 | `/cw:sync` |
| **plan-detector** | Plan Mode 계획 감지 | 자동 |
| **context-manager** | 컨텍스트 파일 관리 | `/cw:context` |
| **context-helper** | 에이전트 컨텍스트 지원 | 에이전트 내부 |
| **quick-fix** | 간단한 이슈 자동 수정 | `/cw:fix` |
| **quality-gate** | 품질 기준 검증 (Tidy First 포함) | Builder 완료 시 |
| **commit-discipline** | Tidy First 커밋 분리 검증 | 커밋 전 |
| **research** | 내부/외부 통합 연구 | `/cw:research` |

### 지식 관리 스킬

| 스킬 | 설명 | 사용 시점 |
|------|------|----------|
| **knowledge-base** | 프로젝트 지식 저장소 | 에이전트 내부 |
| **pattern-learner** | 코드베이스 패턴 학습 | `/cw:start`, Builder |
| **insight-collector** | 인사이트 수집 및 저장 | 자동 |
| **decision-logger** | 아키텍처 결정 기록 | 자동 |
| **evolve** | 인스팅트를 명령/스킬/에이전트로 진화 **(NEW v2.0)** | `/cw:evolve` |

### 진행 관리 스킬

| 스킬 | 설명 | 사용 시점 |
|------|------|----------|
| **progress-tracker** | 진행률 추적 | `/cw:status`, Builder |
| **session-persister** | 세션 상태 저장/복원 | 세션 시작/종료 |
| **review-assistant** | 컨텍스트 인식 리뷰 체크리스트 | `/cw:review` |
| **dependency-analyzer** | Phase/Step 의존성 분석 | `/cw:next` |

### 시각화 스킬 (NEW v2.0)

| 스킬 | 설명 | 사용 시점 |
|------|------|----------|
| **dashboard** | 인터랙티브 HTML 대시보드 생성 | `/cw:analytics`, 수동 |
| **hud** | 실시간 Heads-Up Display | `/cw:status --hud`, Builder 실행 중 |

---

## 📖 워크플로우 예시

### 예시 1: 기본 워크플로우 (자동 병렬)

```bash
# 1. 워크플로우 시작
/cw:start "사용자 프로필 API 구현"

# 2. 계획 검토
/cw:status

# 3. 자동 병렬 실행 (기본)
/cw:next          # 병렬 가능한 step 자동 감지 및 실행

# 4. 진행 확인
/cw:status

# 5. 완료 후 리뷰
/cw:review

# 6. 지속적 개선
/cw:reflect
```

### 예시 2: Autonomous Loop 워크플로우

```bash
# 간단한 작업: 자율 실행
/cw:loop "사용자 인증 시스템 구현"

# 상세 모니터링
/cw:loop "복잡한 기능" --verbose

# 중단 후 재개
/cw:loop --continue
```

### 예시 3: Git Worktree 병렬 워크플로우

```bash
# 1. Phase 1 완료 (main에서)
/cw:start "대규모 리팩토링"
/cw:next phase 1

# 2. 독립 Phase들을 위한 worktree 생성
/cw:worktree create phase 2,3,4

# 3. 각 터미널에서 병렬 작업
# Terminal 1: cd .worktrees/phase-2 && claude && /cw:next --parallel phase 2
# Terminal 2: cd .worktrees/phase-3 && claude && /cw:next --parallel phase 3
# Terminal 3: cd .worktrees/phase-4 && claude && /cw:next --parallel phase 4

# 4. 병합
cd /project
/cw:merge --all

# 5. 정리 및 리뷰
/cw:worktree clean
/cw:review
/cw:reflect --full
```

### 예시 4: Plan Mode 연계

```bash
# 1. Claude의 Plan Mode에서 계획 작성
# (Plan Mode 사용)

# 2. CAW로 계획 가져오기
/cw:start --from-plan

# 3. 자동 병렬 구현 시작
/cw:next

# 4. 지식 동기화
/cw:sync --to-serena
```

### 예시 5: QA 중심 워크플로우

```bash
# 1. 기능 구현
/cw:start "사용자 인증 API"
/cw:next phase 1

# 2. QA 루프로 품질 검증
/cw:qaloop --phase 1

# 3. 빌드/테스트 오류 자동 수정
/cw:ultraqa --target all

# 4. 최종 리뷰
/cw:review --deep

# 5. 회고
/cw:reflect
```

### 예시 6: 연구 기반 개발

```bash
# 1. 구현 전 연구
/cw:research "JWT 인증 베스트 프랙티스" --depth deep --save jwt

# 2. 연구 결과 검토
cat .caw/research/jwt.md

# 3. 연구 기반 구현
/cw:start "RS256 기반 JWT 인증" --research-context jwt

# 4. 구현 중 추가 연구
/cw:research "refresh 토큰 로테이션" --load jwt

# 5. 완료 후 학습 저장
/cw:reflect
/cw:sync --to-serena
```

### 예시 7: CI 실패 수정

```bash
# CI에서 빌드 실패 시
/cw:ultraqa --target build

# 테스트 실패 시
/cw:ultraqa --target test

# 린트 실패 시
/cw:ultraqa --target lint

# 모든 이슈 한번에
/cw:ultraqa --target all --max-cycles 5
```

### 예시 8: Swarm 병렬 실행 (NEW v2.0)

```bash
# 1. 독립적인 여러 기능 병렬 구현
/cw:swarm "로그인 API 구현" "로그아웃 버튼 추가" "인증 모듈 리뷰"

# 2. 워커 수 제한 (리소스 관리)
/cw:swarm --workers 2 "기능A" "기능B" "기능C" "기능D"

# 3. 작업 계획에서 병렬 가능한 step 자동 추출
/cw:start "대규모 리팩토링"
/cw:swarm --from-plan

# 4. Worktree 기반 격리 실행
/cw:swarm --worktrees "feature-auth" "feature-payment"

# 5. 결과 확인 및 병합
/cw:merge --all
```

### 예시 9: Pipeline 순차 실행 (NEW v2.0)

```bash
# 1. 인라인 파이프라인 정의
/cw:pipeline --stages "plan,build,test,review"

# 2. 설정 파일 기반 파이프라인
/cw:pipeline --config .caw/pipeline.yaml

# 3. 특정 스테이지부터 재개
/cw:pipeline --from build

# 4. 게이트 스테이지 포함 (통과 필수)
# pipeline.yaml에서 gate: true 설정
/cw:pipeline --config release

# 5. 에코 모드로 비용 절감
/cw:pipeline --config standard --eco
```

### 예시 10: Analytics 기반 최적화 (NEW v2.0)

```bash
# 1. 워크플로우 실행
/cw:start "복잡한 기능 구현"
/cw:next --all

# 2. 비용 분석
/cw:analytics --cost

# 3. 모델 분포 확인
/cw:analytics --tokens

# 4. 최적화 인사이트 확인
/cw:analytics

# 5. 세션별 비교
/cw:analytics --sessions

# 6. 보고서 내보내기
/cw:analytics --export
```

### 예시 11: Evolve 인스팅트 진화 (NEW v2.0)

```bash
# 1. 진화 후보 확인
/cw:evolve --preview

# 2. 특정 인스팅트 상세 보기
/cw:evolve --id safe-modify-pattern-abc12345

# 3. 명령어로 진화
/cw:evolve --create command safe-modify-pattern-abc12345 safe-modify

# 4. 스킬로 진화
/cw:evolve --create skill pre-commit-check-def67890 pre-commit-quality

# 5. 진화된 컴포넌트 테스트
/cw:safe-modify <args>
```

---

## 🪝 훅 동작

### SessionStart 훅

세션 시작 시 CAW 플러그인 로드를 알립니다.

```json
{
  "type": "command",
  "command": "echo CAW plugin loaded"
}
```

### PreToolUse 훅

#### Edit/Write 도구 사용 시

1. **Plan Adherence Check**: 계획 준수 여부 검증
2. **Gemini Edit Review**: Gemini CLI로 편집 내용 리뷰 (NEW)

#### Bash 도구 사용 시 (git commit)

1. **Tidy First 커밋 검증**: 구조적/동작적 변경 혼합 차단
2. **Gemini Commit Review**: Gemini CLI로 커밋 메시지 리뷰 (NEW)

```
git commit 감지
     │
     ▼
┌─────────────────────────────┐
│ Analyze staged changes      │
│ (git diff --staged)         │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│ Classify change types       │
│ • Structural (Tidy)         │
│ • Behavioral (Build)        │
└──────────────┬──────────────┘
               │
       ┌───────┴───────┐
       ▼               ▼
  All Tidy?       All Build?
       │               │
       ▼               ▼
  ✅ Allow         ✅ Allow
  [tidy] prefix   [feat]/[fix]

       │
       ▼ Mixed?
       │
       ▼
  ❌ Block commit
  → 분리 필요
  → /cw:tidy --split
```

**검증 기준**:

| 변경 유형 | 예시 | 커밋 프리픽스 |
|----------|------|--------------|
| Structural (Tidy) | 이름 변경, 메서드 추출, 파일 이동 | `[tidy]` |
| Behavioral (Build) | 새 기능, 로직 변경, 버그 수정 | `[feat]`, `[fix]` |
| Mixed | 위 두 가지 혼합 | ❌ 차단됨 |

### Quality Gate (Builder 내부 트리거)

> **Note**: Quality Gate는 hooks.json이 아닌 Builder 에이전트 내부에서 호출됩니다.

Step 완료 시 자동으로 품질 검증을 수행합니다:

```
Step 구현 완료
     │
     ▼
┌─────────────────────────────┐
│ 1. Code Changes (Required)  │──→ 변경 없음? → ❌ Fail
└──────────────┬──────────────┘
               ▼
┌─────────────────────────────┐
│ 2. Compilation (Required)   │──→ 오류? → ❌ Fail
└──────────────┬──────────────┘
               ▼
┌─────────────────────────────┐
│ 3. Linting (Warning)        │──→ 경고 수집
└──────────────┬──────────────┘
               ▼
┌─────────────────────────────┐
│ 4. Tidy First (Required)    │──→ 혼합 변경? → ❌ Fail
└──────────────┬──────────────┘
               ▼
┌─────────────────────────────┐
│ 5. Tests (Required)         │──→ 실패? → ❌ Fail (3회 재시도)
└──────────────┬──────────────┘
               ▼
┌─────────────────────────────┐
│ 6. Conventions (Warning)    │──→ 경고 수집
└──────────────┬──────────────┘
               ▼
     ✅ Quality Gate PASSED
     → Step 완료로 표시
```

---

## ✅ 베스트 프랙티스

### 1. 작업 유형에 맞는 명령어 선택

```bash
# 집중된 단일 작업 → /cw:loop
/cw:loop "JWT 인증 구현"

# 전체 기능 개발 → /cw:auto
/cw:auto "사용자 관리 시스템"

# 세밀한 제어 필요 → /cw:next
/cw:next --step 2.1
```

### 2. QA 통합 워크플로우

```bash
# 구현 후 자동 QA
/cw:next phase 1
/cw:qaloop --phase 1          # QA 루프로 품질 검증

# CI 실패 시 UltraQA
/cw:ultraqa --target build    # 빌드 오류 자동 수정

# 각 step 후 자동 QA (loop 명령어)
/cw:loop "기능 구현" --qa-each-step
```

### 3. 연구 기반 개발

```bash
# 구현 전 연구
/cw:research "JWT 베스트 프랙티스" --save jwt-research

# 연구 결과 기반 구현
/cw:start "JWT 인증 구현" --research-context jwt-research

# 필요시 추가 연구
/cw:research "refresh 토큰" --load jwt-research
```

### 4. 대규모 작업은 Worktree 사용

```bash
# Phase가 3개 이상인 대규모 작업
/cw:worktree create phase 2,3,4
# 각 터미널에서 병렬 작업
```

### 5. 작업 완료 후 Ralph Loop

```bash
# 모든 작업 완료 후 회고
/cw:reflect --full

# 주요 학습 내용 영속화
/cw:sync --to-serena
```

### 6. 정기적 동기화

```bash
# 세션 종료 전
/cw:sync --to-serena

# 새 세션 시작 시
/cw:sync --from-serena
```

---

## ❓ 문제 해결

### Q: 병렬 실행이 되지 않아요

```bash
# 의존성 확인
/cw:status

# 강제 병렬 실행
/cw:next --parallel
```

### Q: /cw:loop가 계속 실패해요

```bash
# 상세 출력으로 문제 파악
/cw:loop "작업" --verbose

# 자동 수정 비활성화하고 수동 개입
/cw:loop "작업" --no-auto-fix
```

### Q: Worktree 충돌이 발생해요

```bash
# 충돌 파일 수정 후
git add <resolved-files>
/cw:merge --continue

# 또는 병합 취소
/cw:merge --abort
```

### Q: Serena 연결이 안 돼요

MCP 서버 설정을 확인하세요. Serena MCP가 실행 중인지 확인합니다.

### Q: 학습 내용이 사라져요

```bash
# Serena에 동기화
/cw:sync --to-serena

# 복원
/cw:sync --from-serena
```

### Q: QA 루프가 같은 이슈로 멈춰요 (stalled)

```bash
# 수동 수정 후 재개
/cw:qaloop --continue

# 또는 심각도 낮춰서 통과
/cw:qaloop --exit-on critical

# 딥 진단으로 근본 원인 분석
/cw:ultraqa --deep
```

### Q: UltraQA 진단이 부정확해요

```bash
# 딥 모드 사용 (Opus 활용)
/cw:ultraqa --deep

# 심층 진단 모드로 품질 향상
```

### Q: 연구 결과가 불완전해요

```bash
# 깊이 증가
/cw:research "topic" --depth deep

# 특정 영역 집중
/cw:research "topic" --internal  # 내부만
/cw:research "topic" --external  # 외부만

# 이전 결과에 추가
/cw:research "related topic" --load previous-research
```

---

## 🗺️ 로드맵

### 완료된 기능

- [x] Bootstrapper 에이전트 - 환경 초기화 (v1.1.0)
- [x] Fixer 에이전트 - 코드 수정/리팩토링 (v1.2.0)
- [x] 티어별 모델 라우팅 (v1.3.0)
- [x] 자동 병렬 실행 (v1.4.0)
- [x] Git Worktree 지원 (v1.5.0)
- [x] Ralph Loop 지속적 개선 (v1.5.0)
- [x] Serena 메모리 동기화 (v1.5.0)
- [x] Tidy First 방법론 (v1.6.0)
- [x] Autonomous Loop `/cw:loop` (v1.7.0)
- [x] Gemini CLI 리뷰 통합 (v1.7.0)
- [x] QA Loop `/cw:qaloop` (v1.8.0)
- [x] UltraQA `/cw:ultraqa` (v1.8.0)
- [x] Research Mode `/cw:research` (v1.8.0)
- [x] 병렬 실행 강화 (v1.8.0)
- [x] GUIDELINES.md 자동 생성 `--with-guidelines` (v1.9.0)
- [x] AGENTS.md 계층 생성 `--deep` (v1.9.0)
- [x] **Swarm 병렬 실행** `/cw:swarm` (v2.0.0)
- [x] **Pipeline 명시적 파이프라인** `/cw:pipeline` (v2.0.0)
- [x] **Analytics 비용 분석** `/cw:analytics` (v2.0.0)
- [x] **Evolve 인스팅트 진화** `/cw:evolve` (v2.0.0)
- [x] **Dashboard 시각화** 스킬 (v2.0.0)
- [x] **HUD 실시간 표시** 스킬 (v2.0.0)
- [x] 모든 핵심 에이전트 (18개)
- [x] 모든 핵심 스킬 (20개)

### 예정된 기능

- [ ] VS Code 확장 통합
- [ ] GitHub Actions 통합
- [ ] 멀티 프로젝트 지원
- [ ] 웹 대시보드 (외부 호스팅)
- [ ] 멀티모달 지원 (이미지/다이어그램 생성)

---

## 📚 테스트

```bash
# 전체 테스트 실행
cd plugins/context-aware-workflow
python3 -m pytest tests/ -v

# 플러그인 구조 테스트만
python3 tests/test_plugin_structure.py
```
