# Context-Aware Workflow (CAW) 사용자 가이드

> **버전**: 1.2.1
> **목적**: 구조화된 작업 계획과 컨텍스트 관리를 통한 효율적인 개발 워크플로우
> **업데이트**: Quick Fix 스킬 추가, Reviewer JSON 출력 지원 (Fixer 연동 강화)

---

## 📋 목차

1. [빠른 시작](#-빠른-시작)
2. [핵심 개념](#-핵심-개념)
3. [명령어 상세](#-명령어-상세)
4. [에이전트](#-에이전트)
5. [워크플로우 예시](#-워크플로우-예시)
6. [스크립트 도구](#-스크립트-도구)
7. [훅 동작](#-훅-동작)
8. [베스트 프랙티스](#-베스트-프랙티스)
9. [문제 해결](#-문제-해결)

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
# 1. 환경 초기화 (선택 - /caw:start에서 자동 실행됨)
/context-aware-workflow:init

# 2. 새 작업 시작
/context-aware-workflow:start "JWT 인증 시스템 구현"

# 3. 현재 상태 확인
/context-aware-workflow:status

# 4. 다음 단계 자동 실행
/context-aware-workflow:next

# 5. 코드 리뷰
/context-aware-workflow:review

# 6. 규칙 준수 검증
/context-aware-workflow:check
```

### 명령어 한눈에 보기

| 명령어 | 단축형 | 설명 |
|--------|--------|------|
| `/context-aware-workflow:init` | `/caw:init` | 환경 초기화 (자동 실행) |
| `/context-aware-workflow:brainstorm` | `/caw:brainstorm` | 요구사항 발굴 (선택) |
| `/context-aware-workflow:design` | `/caw:design` | UX/UI, 아키텍처 설계 (선택) |
| `/context-aware-workflow:start` | `/caw:start` | 워크플로우 시작 |
| `/context-aware-workflow:status` | `/caw:status` | 진행 상태 표시 |
| `/context-aware-workflow:next` | `/caw:next` | 다음 단계 실행 |
| `/context-aware-workflow:review` | `/caw:review` | 코드 리뷰 |
| `/context-aware-workflow:fix` | `/caw:fix` | 리뷰 결과 수정 (NEW) |
| `/context-aware-workflow:check` | `/caw:check` | 규칙 준수 검증 |
| `/context-aware-workflow:context` | `/caw:context` | 컨텍스트 관리 |

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
| # | Step | Status | Agent | Notes |
|---|------|--------|-------|-------|
| 1.1 | JWT 라이브러리 설치 | ✅ Complete | Builder | jsonwebtoken@9.0 |
| 1.2 | 환경 변수 설정 | 🔄 In Progress | Builder | |

### Phase 2: 구현
| # | Step | Status | Agent | Notes |
|---|------|--------|-------|-------|
| 2.1 | 토큰 생성 함수 | ⏳ Pending | Builder | |
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

### 3. 에이전트 시스템

CAW는 9개의 전문 에이전트를 사용합니다:

**초기화 에이전트**:
| 에이전트 | 역할 | 출력물 |
|----------|------|--------|
| **Bootstrapper** | 환경 초기화, 프로젝트 탐지 | `.caw/context_manifest.json` |

**선택적 설계 에이전트** (사전 설계 단계):
| 에이전트 | 역할 | 출력물 |
|----------|------|--------|
| **Ideator** | 요구사항 발굴, Socratic 질문 | `.caw/brainstorm.md` |
| **Designer** | UX/UI 설계, 와이어프레임 | `.caw/design/ux-ui.md` |
| **Architect** | 시스템 아키텍처 설계 | `.caw/design/architecture.md` |

**핵심 구현 에이전트**:
| 에이전트 | 역할 | 출력물 |
|----------|------|--------|
| **Planner** | 실행 계획 생성 | `.caw/task_plan.md` |
| **Builder** | TDD 구현 및 테스트 | 코드 파일 |
| **Reviewer** | 코드 품질 리뷰 | 리뷰 리포트 |
| **Fixer** | 리뷰 결과 수정/리팩토링 | 수정된 코드 |
| **ComplianceChecker** | 규칙 준수 검증 | 검증 리포트 |

**전체 워크플로우 다이어그램**:
```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     CAW (Context-Aware Workflow) Pipeline                    │
└─────────────────────────────────────────────────────────────────────────────┘

 User Request
      │
      ▼
┌─────────────┐
│ BOOTSTRAPPER│  ◄── /caw:init (자동 또는 수동)
│   (haiku)   │
├─────────────┤
│ • 환경 체크  │
│ • .caw/ 생성│
│ • 프로젝트   │
│   분석      │
└──────┬──────┘
       │
       ▼ .caw/context_manifest.json
       │
┌──────┴──────────────────────────────────────────────────────────────────────┐
│                        [선택적 Discovery/Design Phase]                       │
│  ┌───────────────┐    ┌───────────────┐    ┌───────────────┐               │
│  │   IDEATOR     │    │   DESIGNER    │    │   ARCHITECT   │               │
│  │   (sonnet)    │    │   (sonnet)    │    │   (sonnet)    │               │
│  ├───────────────┤    ├───────────────┤    ├───────────────┤               │
│  │/caw:brainstorm│    │/caw:design    │    │/caw:design    │               │
│  │               │    │  --ui         │    │  --arch       │               │
│  └───────┬───────┘    └───────┬───────┘    └───────┬───────┘               │
│          │                    │                    │                        │
│          ▼                    ▼                    ▼                        │
│   brainstorm.md        ux-ui.md            architecture.md                  │
└─────────────────────────────────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                         [핵심 Implementation Phase]                          │
│                                                                              │
│  ┌───────────────┐                                                           │
│  │    PLANNER    │  ◄── /caw:start "작업 설명"                               │
│  │   (sonnet)    │                                                           │
│  ├───────────────┤                                                           │
│  │ • 요구사항    │                                                           │
│  │   분석       │                                                           │
│  │ • Phase/Step │                                                           │
│  │   계획 생성  │                                                            │
│  └───────┬───────┘                                                           │
│          │                                                                   │
│          ▼ task_plan.md                                                      │
│          │                                                                   │
│  ┌───────────────┐                                                           │
│  │    BUILDER    │  ◄── /caw:next                                           │
│  │   (sonnet)    │                                                           │
│  ├───────────────┤                                                           │
│  │ • TDD 구현    │  ───┐                                                     │
│  │ • 테스트 실행 │     │ 반복                                                │
│  │ • 상태 갱신   │  ◄──┘                                                     │
│  └───────┬───────┘                                                           │
│          │                                                                   │
│          ▼ 구현 코드 + 테스트                                                 │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                            [Quality Gate Phase]                              │
│                                                                              │
│  ┌───────────────┐         ┌───────────────┐         ┌───────────────┐      │
│  │   REVIEWER    │         │    FIXER      │         │  COMPLIANCE   │      │
│  │   (sonnet)    │         │   (sonnet)    │         │   CHECKER     │      │
│  ├───────────────┤         ├───────────────┤         │   (haiku)     │      │
│  │/caw:review    │         │/caw:fix       │         ├───────────────┤      │
│  │               │   ────▶ │  --deep       │         │/caw:check     │      │
│  └───────┬───────┘         └───────┬───────┘         └───────┬───────┘      │
│          │                         │                         │              │
│          ▼                         ▼                         ▼              │
│   리뷰 리포트              수정된 코드               컴플라이언스 리포트       │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
       │
       ▼
   ✅ 작업 완료
```

**간단 워크플로우**:
```
/caw:init → /caw:brainstorm → /caw:design → /caw:start → /caw:next → /caw:review → /caw:fix → /caw:check
    ↓            ↓                ↓             ↓            ↓            ↓           ↓          ↓
  환경설정   brainstorm.md   design/*.md  task_plan.md   구현 코드    리뷰 리포트  수정코드    검증 리포트
  (자동)       (선택)          (선택)        (필수)        (반복)       (권장)      (선택)      (권장)
```

---

## 📌 명령어 상세

### `/caw:init` - 환경 초기화

CAW 환경을 초기화합니다. `/caw:start` 실행 시 자동으로 호출되지만, 수동으로도 실행 가능합니다.

#### 사용법

```bash
# 환경 초기화 (자동 탐지)
/caw:init

# 환경 리셋 (기존 환경 삭제 후 재생성)
/caw:init --reset

# 특정 프로젝트 타입 지정
/caw:init --type typescript
```

#### Bootstrapper 에이전트 동작

1. **환경 확인**: `.caw/` 디렉토리 존재 여부 확인
2. **프로젝트 분석**: 파일 구조, 기술 스택, 패키지 매니저 탐지
3. **디렉토리 생성**: `.caw/`, `.caw/design/`, `.caw/sessions/`, `.caw/archives/`
4. **매니페스트 생성**: `context_manifest.json` 초기화

#### 출력 예시

```
🚀 CAW Environment Initialized

📁 Created:
  ✅ .caw/
  ✅ .caw/design/
  ✅ .caw/sessions/
  ✅ .caw/archives/

📋 Project Analysis:
  • Type: TypeScript (Node.js)
  • Package Manager: npm
  • Test Framework: Jest
  • Entry Point: src/index.ts

📄 Generated: .caw/context_manifest.json

💡 Next Steps:
   • /caw:brainstorm - 요구사항 발굴
   • /caw:design - UX/UI 또는 아키텍처 설계
   • /caw:start "작업 설명" - 바로 구현 시작
```

---

### `/caw:brainstorm` - 요구사항 발굴 (선택)

Socratic 대화를 통해 모호한 아이디어를 구조화된 요구사항으로 변환합니다.

#### 사용법

```bash
# 새 아이디어 탐색
/caw:brainstorm "사용자 알림 시스템"

# 기존 brainstorm 계속
/caw:brainstorm

# 처음부터 다시 시작
/caw:brainstorm --reset
```

#### Ideator 에이전트 동작

1. **Socratic 질문**: 목표, 사용자, 제약사항 탐색
2. **체계적 탐색**: 문제/솔루션 공간 분석
3. **문서화**: `.caw/brainstorm.md` 생성

#### 출력 예시

```
📝 Brainstorm Complete

Created: .caw/brainstorm.md

## Summary
- Problem: 실시간 알림 부재로 사용자 이탈
- Users: 일반 사용자, 관리자
- Must Have: 3 requirements
- Open Questions: 2 items

💡 Next Steps:
   • /caw:design --ui for UX/UI design
   • /caw:design --arch for architecture
   • /caw:start to begin planning
```

---

### `/caw:design` - 설계 단계 (선택)

UX/UI 설계 또는 시스템 아키텍처 문서를 생성합니다.

#### 사용법

```bash
# UX/UI 설계
/caw:design --ui

# 아키텍처 설계
/caw:design --arch

# 둘 다 생성
/caw:design --all

# 대화형 선택
/caw:design
```

#### Designer 에이전트 동작 (--ui)

1. **사용자 흐름 설계**: 주요 작업 경로 매핑
2. **와이어프레임 생성**: ASCII 기반 화면 설계
3. **컴포넌트 명세**: 상태, 동작 정의
4. **출력**: `.caw/design/ux-ui.md`

#### Architect 에이전트 동작 (--arch)

1. **시스템 설계**: 컴포넌트 경계, 상호작용
2. **데이터 모델링**: ERD, 스키마 정의
3. **API 설계**: 엔드포인트 명세
4. **출력**: `.caw/design/architecture.md`

#### 출력 예시

```
📐 Design Complete

Created Files:
  ✅ .caw/design/ux-ui.md
     - 3 user flows
     - 5 wireframes
     - 12 component specs

  ✅ .caw/design/architecture.md
     - 4 services
     - 8 API endpoints
     - 3 technical decisions

💡 Next: /caw:start to create implementation plan
```

---

### `/caw:start` - 워크플로우 시작

워크플로우 세션을 시작하고 `.caw/task_plan.md`를 생성합니다.

#### 사용법

```bash
# 새 작업 시작 (가장 일반적)
/caw:start "사용자 인증 시스템 구현"

# Plan Mode 계획 가져오기
/caw:start --from-plan

# 특정 계획 파일 지정
/caw:start --plan-file docs/feature-plan.md
```

#### Planner 에이전트 동작

1. **요구사항 분석**: 작업 설명 파싱
2. **코드베이스 탐색**: 관련 파일, 패턴 발견
3. **명확화 질문**: 필요시 사용자에게 질문
4. **계획 생성**: `.caw/task_plan.md` 작성

---

### `/caw:status` - 진행 상태 표시

현재 워크플로우 상태와 진행률을 표시합니다.

#### 사용법

```bash
/caw:status
```

#### 출력 예시

```
📊 Workflow Status

📋 Task: JWT 인증 시스템 구현
📁 Plan: .caw/task_plan.md

Phase 2: Core Implementation
├─ 2.1 JWT 유틸리티 생성    ✅ Complete
├─ 2.2 인증 미들웨어         🔄 In Progress  ← 현재
├─ 2.3 로그인 엔드포인트      ⏳ Pending
└─ 2.4 테스트 추가           ⏳ Pending

진행률: 40% (4/10 steps)

💡 다음: /caw:next 로 2.3 단계 진행
```

---

### `/caw:next` - 다음 단계 실행

Builder 에이전트를 호출하여 다음 Pending 단계를 자동 구현합니다.

#### 사용법

```bash
# 다음 1개 Step 진행 (기본)
/caw:next

# 현재 Phase 전체 진행
/caw:next --all

# 특정 Step 진행
/caw:next --step 2.3
```

#### Builder 에이전트 동작

```
1. .caw/task_plan.md 읽기 → 현재 Step 파악
2. 테스트 먼저 작성 (TDD)
3. 구현 코드 작성
4. 테스트 실행 (자동)
5. 성공 시 .caw/task_plan.md 상태 업데이트 (⏳ → ✅)
6. 실패 시 수정 후 재시도 (최대 3회)
```

---

### `/caw:review` - 코드 리뷰

Reviewer 에이전트를 호출하여 코드 품질을 분석합니다.

#### 사용법

```bash
# 현재 Phase 리뷰 (기본)
/caw:review

# 특정 Phase 리뷰
/caw:review --phase 2

# 특정 Step 리뷰
/caw:review --step 2.3

# 딥 리뷰 (보안/성능 집중)
/caw:review --deep

# 특정 영역 집중
/caw:review --focus security
/caw:review --focus performance
/caw:review --focus quality
```

#### 출력 예시

```
📝 Code Review Report

## Phase 2: Core Implementation

### Step 2.1: JWT 유틸리티 생성
**파일**: src/auth/jwt.ts

#### 🔴 Critical
- Line 45: JWT secret이 하드코딩됨 → 환경 변수 사용 필요

#### 🟡 Warning
- Line 23: 토큰 만료 시간 체크 누락

#### 🟢 Suggestion
- Line 12: async/await 사용 권장

### Summary
| Severity | Count |
|----------|-------|
| Critical | 1 |
| Warning  | 2 |
| Suggestion | 3 |
```

---

### `/caw:fix` - 리뷰 결과 수정 (NEW)

Reviewer 결과를 기반으로 코드를 자동 또는 대화형으로 수정합니다.

#### 사용법

```bash
# 간단한 이슈 자동 수정 (기본)
/caw:fix

# 대화형 모드 (수정 전 확인)
/caw:fix --interactive

# 특정 카테고리만 수정
/caw:fix --category docs       # 문서 (JSDoc 등)
/caw:fix --category style      # 스타일/린트
/caw:fix --category constants  # 매직 넘버 상수화

# 복잡한 리팩토링 (Fixer 에이전트 사용)
/caw:fix --deep

# 미리보기 (실제 수정 안 함)
/caw:fix --dry-run
```

#### 수정 가능 유형

| 카테고리 | 자동화 | 예시 |
|----------|--------|------|
| `constants` | ✅ 가능 | `3600` → `TOKEN_EXPIRY_SECONDS` |
| `docs` | ✅ 가능 | 누락된 JSDoc 템플릿 생성 |
| `style` | ✅ 가능 | ESLint/Prettier 자동 수정 |
| `imports` | ✅ 가능 | Import 정렬, 미사용 제거 |
| `naming` | ⚠️ 반자동 | 변수명 변경 (확인 필요) |
| `logic` | ❌ 수동 | Fixer 에이전트 필요 (`--deep`) |
| `performance` | ❌ 수동 | Fixer 에이전트 필요 (`--deep`) |

#### 모드 선택

```
┌─────────────────────────────────────────────────────┐
│                   /caw:fix                           │
├─────────────────────────────────────────────────────┤
│                                                     │
│  Simple Issues           Complex Issues             │
│  (auto-fixable)          (needs analysis)           │
│       │                        │                    │
│       ▼                        ▼                    │
│  ┌─────────┐            ┌─────────────┐             │
│  │  Quick  │            │   Fixer     │             │
│  │   Fix   │            │   Agent     │             │
│  └─────────┘            │  (--deep)   │             │
│       │                 └─────────────┘             │
│       ▼                        │                    │
│  • 상수 추출                • 로직 개선              │
│  • JSDoc 생성              • 다중 파일 리팩토링       │
│  • 린트 수정               • 패턴 추출               │
│                           • 아키텍처 변경            │
│                                                     │
└─────────────────────────────────────────────────────┘
```

#### 출력 예시

**Quick Fix 결과**:
```
🔧 Quick Fix Mode

스캔 중: review 결과 분석...

자동 수정 가능:
  ✓ 3 매직 넘버 → 상수화
  ✓ 2 누락된 JSDoc → 템플릿 생성
  ✓ 5 린트 위반 → 자동 수정

자동 수정 불가 (--deep 필요):
  ⚠ 2 성능 개선 제안
  ⚠ 1 아키텍처 권장사항

수정 적용 중...

✅ 수정 완료: src/auth/jwt.ts
   • Line 45: 3600 → TOKEN_EXPIRY_SECONDS
   • Line 67: generateToken() JSDoc 추가

📊 요약:
   적용됨: 10개 수정
   건너뜀: 3개 (--deep 필요)

💡 복잡한 수정은:
   /caw:fix --deep
```

**Deep Fix 결과** (Fixer 에이전트):
```
🔧 Deep Fix Mode - Fixer Agent 호출

분석 중: 리뷰 결과...

복잡한 이슈 발견:
  1. Performance: DB 쿼리 배치 처리
  2. Architecture: 검증 모듈 분리

📋 리팩토링 계획:
┌────────────────────────────────────────────────────┐
│ 1. DB 쿼리 배치 처리                                │
│    파일: src/auth/jwt.ts, src/services/user.ts     │
│    영향: DB 호출 ~30% 감소                          │
│    위험도: 낮음                                     │
├────────────────────────────────────────────────────┤
│ 2. 검증 모듈 분리                                   │
│    파일: 신규 src/validation/auth.ts               │
│    영향: 관심사 분리 개선                           │
│    위험도: 중간                                     │
└────────────────────────────────────────────────────┘

진행하시겠습니까? [Y/n/선택]
```

---

### `/caw:check` - 규칙 준수 검증

ComplianceChecker 에이전트를 호출하여 프로젝트 규칙 준수를 검증합니다.

#### 사용법

```bash
# 전체 검사
/caw:check

# 워크플로우 구조 검증
/caw:check --workflow

# CLAUDE.md 규칙 검증
/caw:check --rules

# 문서 완성도 검증
/caw:check --docs

# 네이밍 컨벤션 검증
/caw:check --conventions

# 모든 검사 실행
/caw:check --all
```

#### 출력 예시

```
✅ Compliance Check Results

📊 Overall Score: 94/100 🟢 COMPLIANT

| Category | Score | Status |
|----------|-------|--------|
| Plugin Structure | 100% | ✅ |
| Code Quality | 98% | ✅ |
| Naming Conventions | 100% | ✅ |
| Documentation | 100% | ✅ |
| Testing | 85% | ⚠️ |

### Recommendations
1. 🟡 Medium: 4개 return type hint 추가 (15분)
2. 🟢 Low: pyproject.toml 생성 (45분)
```

---

### `/caw:context` - 컨텍스트 관리

컨텍스트 파일을 관리합니다.

#### 사용법

```bash
# 현재 컨텍스트 상태 표시
/caw:context show

# 파일 추가 (Active 계층)
/caw:context add src/auth/jwt.ts

# 파일 추가 (Project 계층, 읽기 전용)
/caw:context add package.json --project

# 파일 제거 (Archive로 이동)
/caw:context remove src/old/deprecated.ts

# 파일 압축 (인터페이스만 추출)
/caw:context pack src/utils/helpers.ts

# 오래된 파일 정리 제안
/caw:context prune
/caw:context prune --threshold 3  # 3턴 이상 미사용
```

#### 컨텍스트 상태 예시

```
📂 Current Context

══════════════════════════════════════════
📊 Context Status: Active Workflow
══════════════════════════════════════════

### Active Files (3)
| File | Reason | Last Accessed |
|------|--------|---------------|
| src/auth/jwt.ts | Main implementation | 2분 전 |
| src/middleware/auth.ts | Auth middleware | 5분 전 |

### Project Files (2)
- package.json
- tsconfig.json

### Packed Files (1)
- src/utils/helpers.ts (12 exports)

📈 Token Usage: 2,025 / 5,000 (40%)
```

---

## 🤖 에이전트

### 초기화 에이전트

#### Bootstrapper 에이전트

**역할**: 환경 초기화 및 프로젝트 컨텍스트 탐지

| 속성 | 값 |
|------|-----|
| 모델 | haiku (빠른 초기화) |
| 도구 | Read, Write, Glob, Bash, AskUserQuestion |
| 트리거 | `/caw:init`, `/caw:start` (자동) |
| 출력 | `.caw/context_manifest.json` |

**특징**:
- `.caw/` 디렉토리 존재 여부 확인 및 생성
- 프로젝트 타입 자동 탐지 (package.json, pyproject.toml 등)
- 컨텍스트 매니페스트 초기화
- 기존 환경 재사용 또는 리셋 지원

**동작 흐름**:
```
1. 환경 확인: .caw/ 디렉토리 존재 여부
2. 프로젝트 분석: 파일 구조, 기술 스택 탐지
3. 디렉토리 생성: .caw/, .caw/design/, .caw/sessions/, .caw/archives/
4. 매니페스트 생성: context_manifest.json 초기화
5. 완료 보고: 환경 상태 요약 제공
```

---

### 설계 에이전트 (선택적)

#### Ideator 에이전트

**역할**: Socratic 대화를 통한 요구사항 발굴 및 아이디어 구조화

| 속성 | 값 |
|------|-----|
| 모델 | sonnet |
| 도구 | Read, Write, Glob, Grep, WebSearch, AskUserQuestion |
| 트리거 | `/caw:brainstorm` |
| 출력 | `.caw/brainstorm.md` |

**특징**:
- Socratic 질문법으로 숨겨진 요구사항 발굴
- 문제/솔루션 공간 체계적 탐색
- 리스크 및 제약사항 조기 식별

---

#### Designer 에이전트

**역할**: 사용자 중심 UX/UI 설계 및 와이어프레임 생성

| 속성 | 값 |
|------|-----|
| 모델 | sonnet |
| 도구 | Read, Write, Glob, Grep, AskUserQuestion |
| 트리거 | `/caw:design --ui` |
| 출력 | `.caw/design/ux-ui.md` |

**특징**:
- 사용자 흐름 다이어그램 생성
- ASCII 와이어프레임 설계
- 컴포넌트 상태/동작 명세
- 접근성 요구사항 정의

---

#### Architect 에이전트

**역할**: 확장 가능한 시스템 아키텍처 설계

| 속성 | 값 |
|------|-----|
| 모델 | sonnet |
| 도구 | Read, Write, Glob, Grep, Bash, AskUserQuestion |
| 트리거 | `/caw:design --arch` |
| 출력 | `.caw/design/architecture.md` |

**특징**:
- 컴포넌트 경계 및 상호작용 설계
- 데이터 모델 (ERD) 생성
- API 명세 및 계약 정의
- 기술 결정 문서화 (Trade-off 분석)

---

### 구현 에이전트 (핵심)

#### Planner 에이전트

**역할**: 요구사항 분석 및 `.caw/task_plan.md` 생성

| 속성 | 값 |
|------|-----|
| 모델 | sonnet |
| 도구 | Read, Write, Glob, Grep, Bash, AskUserQuestion |
| 트리거 | `/caw:start` |

**특징**:
- Socratic 질문법으로 요구사항 명확화
- 코드베이스 탐색으로 패턴 발견
- Phase/Step 구조로 계획 분해

---

### Builder 에이전트

**역할**: TDD 방식 구현 및 테스트 자동 실행

| 속성 | 값 |
|------|-----|
| 모델 | sonnet |
| 도구 | Read, Write, Edit, Bash, Grep, Glob |
| 트리거 | `/caw:next` |

**특징**:
- 테스트 먼저 작성 (TDD)
- 테스트 프레임워크 자동 감지 (npm test, pytest 등)
- 실패 시 자동 수정 및 재시도 (최대 3회)
- 완료 시 `.caw/task_plan.md` 상태 업데이트

---

### Reviewer 에이전트

**역할**: 코드 품질 분석 및 리뷰 리포트 생성

| 속성 | 값 |
|------|-----|
| 모델 | sonnet |
| 도구 | Read, Grep, Glob, Bash |
| 트리거 | `/caw:review` |

**리뷰 카테고리**:
- **Correctness**: 로직 오류, 엣지 케이스
- **Security**: 보안 취약점
- **Performance**: 성능 이슈
- **Quality**: 코드 품질, 가독성

**심각도 분류**:
| 레벨 | 설명 |
|------|------|
| 🔴 Critical | 즉시 수정 필요 |
| 🟡 Warning | 수정 권장 |
| 🟢 Suggestion | 개선 제안 |
| 💡 Note | 참고 사항 |

---

### Fixer 에이전트

**역할**: 리뷰 결과 기반 지능형 코드 수정 및 리팩토링

| 속성 | 값 |
|------|-----|
| 모델 | sonnet |
| 도구 | Read, Write, Edit, Bash, Grep, Glob |
| 트리거 | `/caw:fix --deep` |
| 출력 | 수정된 소스 코드, `.caw/fix_history.json` |

**특징**:
- 리뷰 피드백 심층 분석
- 멀티파일 리팩토링 지원
- 안전한 실행 (백업 → 적용 → 검증 → 롤백)
- 의존성 분석 및 영향 범위 파악

**수정 전략 (카테고리별)**:

| 카테고리 | 복잡도 | 접근법 |
|----------|--------|--------|
| 🔴 Security | 높음 | 취약점 즉시 수정 |
| 🔴 Logic | 높음 | 버그 근본 원인 해결 |
| 🟡 Performance | 중간 | DB 배치, 캐싱, 알고리즘 최적화 |
| 🟡 Architecture | 중간 | 모듈 추출, 패턴 리팩토링 |
| 🟢 Quality | 낮음 | 코드 품질 개선 |

**실행 흐름**:
```
1. 리뷰 결과 로드 (.caw/last_review.json)
2. 이슈 분류 및 우선순위 정렬
3. 의존성 분석 (영향 범위 파악)
4. 리팩토링 계획 생성
5. 안전 실행 (백업 → 수정 → 테스트)
6. 결과 리포트 생성
```

**안전 메커니즘**:
- 변경 전 git 상태 확인
- 각 수정 후 타입 체크 실행
- 테스트 실패 시 자동 롤백
- 고위험 변경은 사용자 확인 요청

---

### ComplianceChecker 에이전트

**역할**: 프로젝트 규칙 및 컨벤션 준수 검증

| 속성 | 값 |
|------|-----|
| 모델 | haiku (빠른 검증) |
| 도구 | Read, Glob, Grep |
| 트리거 | `/caw:check` |

**검사 항목**:
- CLAUDE.md 규칙 준수
- 린트 설정 준수
- 네이밍 컨벤션
- 워크플로우 구조
- 문서 완성도

---

## 📖 워크플로우 예시

### 예시 1: 전체 워크플로우

```bash
# 1. 워크플로우 시작
/caw:start "사용자 프로필 API 구현"

# 2. 계획 검토
/caw:status

# 3. 단계별 구현 (반복)
/caw:next          # Step 1.1 구현
/caw:status        # 진행 확인
/caw:next          # Step 1.2 구현
# ... 반복 ...

# 4. Phase 완료 후 리뷰
/caw:review --phase 1

# 5. 규칙 준수 검증
/caw:check --all

# 6. 다음 Phase 진행
/caw:next --all    # Phase 2 전체 진행
```

### 예시 2: Plan Mode 연계

```bash
# 1. Claude의 Plan Mode에서 계획 작성
# (Plan Mode 사용)

# 2. CAW로 계획 가져오기
/caw:start --from-plan

# 3. 자동 구현 시작
/caw:next --all
```

### 예시 3: 빠른 버그 수정

```bash
# 1. 버그 수정 시작
/caw:start "로그인 토큰 만료 버그 수정"

# 2. 자동 구현 (전체)
/caw:next --all

# 3. 빠른 리뷰
/caw:review --deep

# 4. 완료 확인
/caw:status
```

---

## 🔧 스크립트 도구

### detect_plan.py

Plan Mode 출력물을 탐지합니다.

```bash
# 기본 사용
python3 skills/context-manager/scripts/detect_plan.py

# JSON 형식 출력
python3 skills/context-manager/scripts/detect_plan.py --format json
```

### pack_context.py

파일을 인터페이스 요약으로 압축합니다.

```bash
# 단일 파일 압축
python3 skills/context-manager/scripts/pack_context.py --file src/utils/helpers.ts
```

### prune_context.py

오래된 파일 정리를 제안합니다.

```bash
# 기본 실행
python3 skills/context-manager/scripts/prune_context.py

# 임계값 조정
python3 skills/context-manager/scripts/prune_context.py --threshold 3
```

---

## 🪝 훅 동작

### SessionStart 훅

세션 시작 시 자동으로 Plan Mode 계획을 탐지합니다.

```
📋 Plan Mode 계획이 감지되었습니다.

파일: .claude/plan.md
수정: 30분 전
진행: 20% (2/10 완료)

[1] 이 계획으로 시작  [2] 미리보기  [3] 새 작업  [4] 나중에
```

### PreToolUse 훅

파일 수정 전에 `.caw/task_plan.md` 존재 여부를 확인합니다.

```
⚠️ 참고: .caw/task_plan.md가 없습니다.
구조화된 워크플로우를 위해 /caw:start를 먼저 실행하는 것을 권장합니다.
```

### PostToolUse 훅

파일 작업 후 자동으로 컨텍스트를 추적합니다.

**동작**:
- **Read**: `last_accessed` 타임스탬프 업데이트
- **Edit/Write**: 파일을 Active 계층으로 자동 승격
- 토큰 사용량 자동 추정

---

## ✅ 베스트 프랙티스

### 1. 계획 먼저, 구현 나중

```
❌ 잘못된 방법: 바로 코딩 시작 → 방향 수정 반복

✅ 올바른 방법:
1. /caw:start로 계획 생성
2. 계획 검토 및 수정
3. /caw:next로 체계적 구현
```

### 2. 작은 Step으로 분할

```
❌ 잘못된 방법:
Step 1: 전체 인증 시스템 구현

✅ 올바른 방법:
Step 1.1: JWT 토큰 생성
Step 1.2: JWT 토큰 검증
Step 1.3: 미들웨어 구현
```

### 3. 정기적 리뷰

```bash
# Phase 완료 후 리뷰
/caw:review --phase 1

# 중요 Step 완료 후 딥 리뷰
/caw:review --step 2.3 --deep
```

### 4. 컨텍스트 관리

```bash
# 대용량 파일 압축
/caw:context pack src/utils/largeHelper.ts

# 오래된 파일 정리
/caw:context prune --threshold 3
```

---

## ❓ 문제 해결

### Q: 플러그인이 로드되지 않아요

```bash
# 플러그인 경로 확인
claude --plugin-dir /path/to/context-aware-workflow

# 설치 확인
claude plugin list
```

### Q: 명령어가 인식되지 않아요

```bash
# 전체 명령어 이름 사용
/context-aware-workflow:start "task"

# 또는 플러그인 재로드
# Claude 재시작
```

### Q: Builder 에이전트가 테스트를 찾지 못해요

- `package.json`에 test 스크립트 확인
- `pytest.ini` 또는 `pyproject.toml` 확인
- 테스트 파일 위치 확인 (`tests/`, `__tests__/`)

### Q: 컨텍스트 토큰이 너무 많아요

```bash
# 대용량 파일 압축
/caw:context pack src/utils/largeFile.ts

# 오래된 파일 정리
/caw:context prune

# 현재 상태 확인
/caw:context show
```

---

## 🗺️ 향후 로드맵

### 에이전트
- [x] Bootstrapper 에이전트 - 환경 초기화 (v1.1.0)
- [x] Fixer 에이전트 - 코드 수정/리팩토링 (v1.2.0)
- [x] Ideator 에이전트 - 요구사항 발굴
- [x] Designer 에이전트 - UX/UI 설계
- [x] Architect 에이전트 - 아키텍처 설계
- [x] Planner 에이전트 - 계획 생성
- [x] Builder 에이전트 - TDD 구현
- [x] Reviewer 에이전트 - 코드 리뷰
- [x] ComplianceChecker 에이전트 - 규칙 검증

### 명령어
- [x] `/caw:init` - 환경 초기화 (v1.1.0)
- [x] `/caw:fix` - 리뷰 결과 수정 (v1.2.0)
- [x] `/caw:brainstorm` - 요구사항 발굴
- [x] `/caw:design` - UX/UI, 아키텍처 설계
- [x] `/caw:start` - 워크플로우 시작
- [x] `/caw:status` - 진행 상태 표시
- [x] `/caw:next` - 다음 단계 실행
- [x] `/caw:review` - 코드 리뷰
- [x] `/caw:check` - 규칙 준수 검증
- [x] `/caw:context` - 컨텍스트 관리

### 기타
- [x] PostToolUse 훅 - 자동 컨텍스트 추적
- [ ] VS Code 확장 통합
- [ ] GitHub Actions 통합
- [ ] 멀티 프로젝트 지원

---

## 📚 테스트

```bash
# 전체 테스트 실행
python3 -m unittest discover -s tests -v

# 플러그인 구조 테스트만
python3 -m unittest tests.test_plugin_structure -v

# 단위 테스트만
python3 -m unittest discover -s tests/unit -v
```

**테스트 커버리지**:
- 플러그인 구조 검증: 26개 테스트
- Python 스크립트 단위 테스트: 63개 테스트
- 총 89개 테스트
