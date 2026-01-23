# Context-Aware Workflow (CAW) 문서

> **버전**: 1.9.0 | **최종 업데이트**: 2026-01-23

이 디렉토리는 CAW 플러그인의 모든 문서를 포함합니다.

---

## 📚 문서 구조

```
docs/
├── README.md              ← 현재 파일 (문서 인덱스)
├── USER_GUIDE.md          ← 사용자 가이드 (메인)
├── SKILL_DESIGN.md        ← 스킬 에코시스템 설계
├── design/                ← 설계 문서
│   ├── 01_philosophy.md
│   ├── 02_architecture_draft.md
│   ├── 03_feature_selection.md
│   ├── 04_plan_mode_integration.md
│   └── 05_ralph_loop_integration.md
└── references/            ← 참조 문서 (Claude Code 기능)
    ├── AgentSkills.md
    ├── Hooks.md
    ├── Plugins.md
    └── Subagents.md
```

---

## 🆕 v1.9.0 신규 기능

| 기능 | 설명 | 관련 문서 |
|------|------|----------|
| **`--with-guidelines`** | GUIDELINES.md 자동 생성 | [USER_GUIDE.md](./USER_GUIDE.md#-초기화-고급-기능-new) |
| **`--deep`** | 계층적 AGENTS.md 생성 (deepinit 패턴) | [USER_GUIDE.md](./USER_GUIDE.md#-초기화-고급-기능-new) |
| **템플릿 시스템** | `_shared/templates/`에 템플릿 저장 | [USER_GUIDE.md](./USER_GUIDE.md#-초기화-고급-기능-new) |

## v1.8.0 기능

| 기능 | 설명 | 관련 문서 |
|------|------|----------|
| **OMC 통합** | oh-my-claudecode 통합 및 Graceful Degradation | [USER_GUIDE.md](./USER_GUIDE.md#-omc-통합) |
| **`/cw:qaloop`** | QA 루프 (빌드→리뷰→수정 반복) | [USER_GUIDE.md](./USER_GUIDE.md#-qa-loop--ultraqa) |
| **`/cw:ultraqa`** | 지능형 자동 QA | [USER_GUIDE.md](./USER_GUIDE.md#-qa-loop--ultraqa) |
| **`/cw:research`** | 통합 연구 모드 | [USER_GUIDE.md](./USER_GUIDE.md#-research-mode) |

## v1.7.0 기능

| 기능 | 설명 | 관련 문서 |
|------|------|----------|
| **`/cw:loop`** | 자율 반복 실행 루프 (5단계 오류 복구) | [USER_GUIDE.md](./USER_GUIDE.md#-autonomous-loop) |
| **Gemini CLI 리뷰** | Edit/Commit 훅에서 Gemini CLI 리뷰 통합 | [USER_GUIDE.md](./USER_GUIDE.md#-훅-동작) |
| **루프 상태 지속성** | `.caw/loop_state.json`으로 중단/재개 가능 | [USER_GUIDE.md](./USER_GUIDE.md#생성-아티팩트) |

---

## 🎯 빠른 탐색

### 처음 사용자라면

1. **[USER_GUIDE.md](./USER_GUIDE.md)** - 설치부터 모든 명령어까지 완벽 가이드

### 개발자라면

| 관심 분야 | 문서 |
|----------|------|
| 전체 아키텍처 | [design/02_architecture_draft.md](./design/02_architecture_draft.md) |
| 설계 철학 | [design/01_philosophy.md](./design/01_philosophy.md) |
| 스킬 설계 | [SKILL_DESIGN.md](./SKILL_DESIGN.md) |
| Plan Mode 연동 | [design/04_plan_mode_integration.md](./design/04_plan_mode_integration.md) |
| Ralph Loop | [design/05_ralph_loop_integration.md](./design/05_ralph_loop_integration.md) |

### Claude Code 기능 참조

| 주제 | 문서 |
|------|------|
| 에이전트/스킬 시스템 | [references/AgentSkills.md](./references/AgentSkills.md) |
| 서브에이전트 | [references/Subagents.md](./references/Subagents.md) |
| 플러그인 구조 | [references/Plugins.md](./references/Plugins.md) |
| 훅 시스템 | [references/Hooks.md](./references/Hooks.md) |

---

## 📖 문서 개요

### USER_GUIDE.md (사용자 가이드)

**대상**: 모든 CAW 사용자

**주요 내용**:
- 빠른 시작 (2분 완성)
- 17개 명령어 상세 설명 (`/cw:loop` 포함)
- 9개 에이전트 (티어별 변형 포함 17개)
- 16개 스킬 목록
- 자율 실행 루프 (`/cw:loop` vs `/cw:auto`)
- Tidy First 방법론
- Git Worktree 병렬 실행
- Ralph Loop 지속적 개선
- Gemini CLI 리뷰 통합
- 워크플로우 예시
- 문제 해결 가이드

### SKILL_DESIGN.md (스킬 설계)

**대상**: 플러그인 개발자, 기여자

**주요 내용**:
- 스킬 설계 원칙
- 16개 스킬 상세 명세 (6개 신규 포함)
  - `commit-discipline` - Tidy First 커밋 분리
  - `context-manager` - 컨텍스트 윈도우 최적화
  - `dependency-analyzer` - 의존성 분석 및 병렬 실행
  - `quick-fix` - 자동 수정
  - `reflect` - Ralph Loop 지속적 개선
  - `serena-sync` - Serena MCP 동기화
- Hook 연동 패턴
- Agent-Skill 매핑
- Progressive Disclosure 전략

---

## 🏗️ 설계 문서 (design/)

| 문서 | 설명 |
|------|------|
| **01_philosophy.md** | Hybrid Automation, Human-in-the-Loop 등 핵심 철학 |
| **02_architecture_draft.md** | 컴포넌트 구조, 데이터 흐름, 에이전트 파이프라인 |
| **03_feature_selection.md** | MVP 기능 선정 기준 및 로드맵 |
| **04_plan_mode_integration.md** | Claude Code Plan Mode와의 연동 설계 |
| **05_ralph_loop_integration.md** | 지속적 개선 사이클 (RALPH) 설계 |

---

## 📚 참조 문서 (references/)

Claude Code의 핵심 기능에 대한 참조 문서입니다.

| 문서 | 설명 |
|------|------|
| **AgentSkills.md** | 에이전트와 스킬의 차이점, 사용 패턴 |
| **Subagents.md** | Task 도구를 통한 서브에이전트 실행 |
| **Plugins.md** | 플러그인 구조 (plugin.json, 컴포넌트 등) |
| **Hooks.md** | 이벤트 훅 시스템 (SessionStart, PreToolUse 등) |

---

## 🔗 관련 링크

- **README.md** (루트): [../README.md](../README.md) - 프로젝트 개요
- **AGENTS.md**: [../AGENTS.md](../AGENTS.md) - 에이전트 상세 명세
- **스키마 디렉토리**: [../schemas/](../schemas/) - JSON 스키마 정의
- **_shared 디렉토리**: [../_shared/](../_shared/) - 공유 리소스

---

## 📝 문서 기여

문서 개선을 환영합니다:

1. USER_GUIDE.md는 **한국어**로 작성
2. README.md (루트)는 **영어**로 작성
3. 설계 문서는 **한국어/영어 혼용** 가능
4. 마크다운 표, 다이어그램 적극 활용

---

## 📋 버전 이력

| 버전 | 날짜 | 주요 변경 |
|------|------|----------|
| **1.9.0** | 2026-01-23 | `--with-guidelines`, `--deep` 플래그, 템플릿 시스템 |
| 1.8.0 | 2026-01-22 | OMC 통합, QA Loop, UltraQA, Research Mode |
| 1.7.0 | 2026-01-21 | `/cw:loop` 자율 실행, Gemini CLI 통합, 6개 신규 스킬 |
| 1.6.0 | 2026-01-19 | Tidy First, Git Worktree, Serena 동기화 |
| 1.5.0 | 2026-01-15 | Ralph Loop 지속적 개선 |
| 1.4.0 | 2026-01-10 | 모델 라우팅, 티어별 에이전트, `/cw:auto` |

---

*마지막 업데이트: 2026-01-23*
