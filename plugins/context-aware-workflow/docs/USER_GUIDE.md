# Context-Aware Workflow (CAW) 사용자 가이드

> **버전**: 1.7.0
> **목적**: 구조화된 작업 계획과 컨텍스트 관리를 통한 효율적인 개발 워크플로우
> **업데이트**: **Autonomous Loop**, Gemini CLI 리뷰 통합, Tidy First 방법론, 자동 병렬 실행, Git Worktree 지원

---

## 📋 목차

1. [빠른 시작](#-빠른-시작)
2. [핵심 개념](#-핵심-개념)
3. [Autonomous Loop](#-autonomous-loop-new) **(NEW)**
4. [Tidy First 방법론](#-tidy-first-방법론)
5. [명령어 상세](#-명령어-상세)
6. [에이전트](#-에이전트)
7. [스킬](#-스킬)
8. [워크플로우 예시](#-워크플로우-예시)
9. [훅 동작](#-훅-동작)
10. [베스트 프랙티스](#-베스트-프랙티스)
11. [문제 해결](#-문제-해결)

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
| `/context-aware-workflow:loop` | `/cw:loop` | **자율 반복 실행** (NEW) |
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
| `/context-aware-workflow:sync` | `/cw:sync` | Serena 메모리 동기화 |
| `/context-aware-workflow:worktree` | `/cw:worktree` | Git Worktree 관리 |
| `/context-aware-workflow:merge` | `/cw:merge` | Worktree 브랜치 병합 |

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

## 🔄 Autonomous Loop (NEW)

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
```

#### Bootstrapper 에이전트 동작

1. **환경 확인**: `.caw/` 디렉토리 존재 여부 확인
2. **프로젝트 분석**: 파일 구조, 기술 스택, 패키지 매니저 탐지
3. **디렉토리 생성**: `.caw/`, `.caw/design/`, `.caw/archives/`, `.caw/knowledge/`, `.caw/insights/`
4. **매니페스트 생성**: `context_manifest.json` 초기화

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

### `/cw:status` - 진행 상태 표시

현재 워크플로우 상태와 진행률을 표시합니다.

```bash
/cw:status
/cw:status --worktrees    # Worktree 상태 포함
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

### 에이전트 목록 (17개)

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

**구현 에이전트** (티어별 변형 포함):
| 에이전트 | 역할 | 트리거 | 티어 변형 |
|----------|------|--------|-----------|
| **Planner** | 실행 계획 생성 | `/cw:start` | Haiku, Sonnet, Opus |
| **Builder** | TDD 구현 및 테스트 | `/cw:next` | Haiku, Sonnet, Opus |
| **Reviewer** | 코드 품질 리뷰 | `/cw:review` | Haiku, Sonnet, Opus |
| **Fixer** | 리뷰 결과 수정/리팩토링 | `/cw:fix --deep` | Haiku, Sonnet, Opus |
| **ComplianceChecker** | 규칙 준수 검증 | `/cw:check` | - |

---

## 🧠 스킬 (16개)

CAW는 16개의 전문 스킬을 포함합니다:

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

### 지식 관리 스킬

| 스킬 | 설명 | 사용 시점 |
|------|------|----------|
| **knowledge-base** | 프로젝트 지식 저장소 | 에이전트 내부 |
| **pattern-learner** | 코드베이스 패턴 학습 | `/cw:start`, Builder |
| **insight-collector** | 인사이트 수집 및 저장 | 자동 |
| **decision-logger** | 아키텍처 결정 기록 | 자동 |

### 진행 관리 스킬

| 스킬 | 설명 | 사용 시점 |
|------|------|----------|
| **progress-tracker** | 진행률 추적 | `/cw:status`, Builder |
| **session-persister** | 세션 상태 저장/복원 | 세션 시작/종료 |
| **review-assistant** | 컨텍스트 인식 리뷰 체크리스트 | `/cw:review` |
| **dependency-analyzer** | Phase/Step 의존성 분석 | `/cw:next` |

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

### 2. 대규모 작업은 Worktree 사용

```bash
# Phase가 3개 이상인 대규모 작업
/cw:worktree create phase 2,3,4
# 각 터미널에서 병렬 작업
```

### 3. 작업 완료 후 Ralph Loop

```bash
# 모든 작업 완료 후 회고
/cw:reflect --full

# 주요 학습 내용 영속화
/cw:sync --to-serena
```

### 4. 정기적 동기화

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
- [x] **Autonomous Loop** `/cw:loop` (v1.7.0)
- [x] **Gemini CLI 리뷰 통합** (v1.7.0)
- [x] 모든 핵심 에이전트 (11개, 티어 변형 포함 17개)
- [x] 모든 핵심 스킬 (16개)

### 예정된 기능

- [ ] VS Code 확장 통합
- [ ] GitHub Actions 통합
- [ ] 멀티 프로젝트 지원
- [ ] 웹 대시보드

---

## 📚 테스트

```bash
# 전체 테스트 실행
cd plugins/context-aware-workflow
python3 -m pytest tests/ -v

# 플러그인 구조 테스트만
python3 tests/test_plugin_structure.py
```
