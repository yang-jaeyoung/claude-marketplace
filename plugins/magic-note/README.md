# Magic Note Plugin for Claude Code

AI 코딩 워크플로우를 위한 노트 관리 플러그인입니다.

## 기능 개요

| 컴포넌트 | 개수 | 설명 |
|---------|------|------|
| **Commands** | 9개 | `/magic-note:*` 슬래시 명령어 |
| **Agents** | 3개 | 전문 작업 에이전트 |
| **Skills** | 3개 | AI 자동 호출 스킬 |
| **Hooks** | 4개 | 세션 이벤트 자동화 |
| **MCP Tools** | 9개 | 노트 관리 도구 |

## Commands (슬래시 명령어)

| 명령어 | 설명 | 예시 |
|--------|------|------|
| `/magic-note:add` | 새 노트 생성 | `/magic-note:add 인증 계획` |
| `/magic-note:list` | 목록 조회/필터 | `/magic-note:list #auth` |
| `/magic-note:save` | 대화 내용 저장 | `/magic-note:save the plan` |
| `/magic-note:load` | 노트 로드 | `/magic-note:load abc123` |
| `/magic-note:search` | 고급 검색 | `/magic-note:search jwt type:plan` |
| `/magic-note:view` | 상세 보기 | `/magic-note:view abc123` |
| `/magic-note:edit` | 노트 편집 | `/magic-note:edit abc123 add tag:done` |
| `/magic-note:delete` | 노트 삭제 | `/magic-note:delete abc123` |
| `/magic-note:copy` | 내용 복사 | `/magic-note:copy abc123 json` |

## Agents (전문 에이전트)

복잡한 다단계 작업을 위한 전문 에이전트입니다. `/agents`에서 선택하거나 Claude가 상황에 맞게 자동 호출합니다.

| 에이전트 | 역할 | 주요 기능 |
|---------|------|----------|
| `note-organizer` | 노트 라이브러리 정리 | 태그 최적화, 중복 감지, 아카이브 관리 |
| `prompt-curator` | 프롬프트 품질 관리 | 프롬프트 개선, 템플릿화, 효과성 분석 |
| `plan-reviewer` | 계획 진행 관리 | 진행률 추적, 상태 업데이트, 블로커 관리 |

### Agents 사용 예시

**note-organizer:**
```
사용자: "노트 정리 좀 해줘"

Claude: 🗂️ Note Organizer Agent

📊 Organization Report:
- Tags: 5 tags to merge, 3 to remove
- Duplicates: 2 duplicate groups found
- Archive: 4 notes are archive candidates

Would you like to apply all recommendations?
```

**plan-reviewer:**
```
사용자: "인증 구현 진행 상황 확인해줘"

Claude: 📋 Plan Progress Review

Progress: ████████░░░░░░░░ 53% complete

✅ Completed: User model, JWT generation
🔄 In Progress: Refresh tokens
⬜ Remaining: 5 items

Next: Complete refresh token logic
```

## Skills (자동 호출)

| 스킬 | 트리거 | 동작 |
|------|--------|------|
| `auto-save-plan` | 구현 계획 생성 시 | plan 노트로 저장 제안 |
| `prompt-library` | 코드 리뷰/리팩토링 요청 시 | 저장된 프롬프트 제안 |
| `decision-logger` | 기술 선택 결정 시 | choice 노트로 기록 제안 |

## Hooks (이벤트 자동화)

| 이벤트 | 동작 |
|--------|------|
| `SessionStart` | 프로젝트 관련 노트 자동 검색 및 알림 |
| `SessionEnd` | 저장하지 않은 중요 내용 저장 제안 |
| `PostToolUse` | 코드 변경 후 계획 저장 필요성 체크 (비침습적) |
| `SubagentStop` | 에이전트 결과물 저장 제안 |

### Hooks 동작 예시

**SessionStart:**
```
[세션 시작]
📚 Magic Note: Found 3 related notes for this project:
- Auth Implementation Plan (plan)
- API Review Checklist (prompt)

Use `/magic-note:load [id]` to load any note.
```

**SessionEnd:**
```
[세션 종료 전]
💾 Would you like to save any of this session's content to Magic Note?
- Implementation plan for user authentication

Quick save: `/magic-note:save the auth plan`
```

## MCP Tools

| 도구 | 설명 |
|------|------|
| `list_notes` | 노트 목록 조회 (필터 지원) |
| `get_note` | 노트 내용 조회 |
| `add_note` | 새 노트 추가 |
| `update_note` | 노트 수정 |
| `delete_note` | 노트 삭제 |
| `list_templates` | 템플릿 목록 |
| `use_template` | 템플릿으로 노트 생성 |
| `list_projects` | 프로젝트 목록 |
| `list_tags` | 태그 목록 |

## 설치

### 요구사항

- Claude Code v1.0.33 이상
- [Bun](https://bun.sh/) 런타임 (필수)

### Bun 설치

MCP 서버 실행을 위해 Bun이 필요합니다.

```bash
# macOS / Linux
curl -fsSL https://bun.sh/install | bash

# Windows (PowerShell)
powershell -c "irm bun.sh/install.ps1 | iex"

# Homebrew (macOS)
brew install oven-sh/bun/bun

# 설치 확인
bun --version
```

> ⚠️ **중요**: Bun이 설치되어 있지 않으면 MCP 서버가 실행되지 않아 Magic Note 기능을 사용할 수 없습니다.

### 방법 1: GitHub 마켓플레이스 (권장)

```bash
# 마켓플레이스 추가
/plugin marketplace add magic-note/magic-note

# 플러그인 설치
/plugin install magic-note@magic-note-marketplace
```

### 방법 2: 로컬 마켓플레이스

```bash
# 마켓플레이스 추가 (로컬 경로)
/plugin marketplace add /path/to/magic-note/plugin

# 플러그인 설치
/plugin install magic-note@magic-note-marketplace
```

### 방법 3: 직접 테스트

```bash
# CLI 플래그로 직접 로드
claude --plugin-dir /path/to/magic-note/plugin
```

### 설치 확인

```bash
# 설치된 플러그인 확인
/plugin list

# 플러그인 명령어 확인
/magic-note:list
```

## 사용 예시

### 계획 자동 저장 (auto-save-plan skill)

```
사용자: "인증 기능 구현 계획 세워줘"

Claude: [계획 생성]
📋 Plan saved to Magic Note: "Authentication Implementation Plan" (ID: abc123)
```

### 프롬프트 재사용 (prompt-library skill)

```
사용자: "이 코드 리뷰해줘"

Claude: 📚 Found saved prompts:
1. "API Code Review Checklist" - Tags: [api, review]

Would you like me to use this saved prompt?
```

### 결정 기록 (decision-logger skill)

```
사용자: "React vs Vue 중 뭘 쓸까?"

Claude: [비교 분석 후]

📝 Would you like to record this decision in Magic Note?
   Decision: Use React for Frontend Framework
   Rationale: Better ecosystem, team familiarity
```

### 빠른 저장 (save command)

```
사용자: /magic-note:save the implementation plan

Claude: 💾 Saving to Magic Note...
✅ Saved! (ID: abc123)
```

## 노트 타입

| 타입 | 용도 | 예시 |
|------|------|------|
| `prompt` | 재사용 가능한 프롬프트 | 코드 리뷰 체크리스트 |
| `plan` | 구현 계획 및 설계 | 기능 구현 로드맵 |
| `choice` | 기술 선택 기록 | 프레임워크 선정 이유 |

## 저장 위치

모든 노트는 `~/.magic-note/` 디렉토리에 저장됩니다.

```
~/.magic-note/
├── config.yaml
├── index.json
├── notes/
└── templates/
```

## 플러그인 구조

```
plugin/
├── .claude-plugin/
│   ├── plugin.json      # 플러그인 메타데이터
│   └── marketplace.json # 마켓플레이스 카탈로그
├── commands/            # 슬래시 명령어 (9개)
│   ├── add.md
│   ├── list.md
│   ├── save.md
│   ├── load.md
│   ├── search.md
│   ├── view.md
│   ├── edit.md
│   ├── delete.md
│   └── copy.md
├── agents/              # 전문 에이전트 (3개)
│   ├── note-organizer.md
│   ├── prompt-curator.md
│   └── plan-reviewer.md
├── skills/              # AI 자동 호출 스킬 (3개)
│   ├── auto-save-plan/
│   ├── prompt-library/
│   └── decision-logger/
├── hooks/
│   └── hooks.json       # 이벤트 훅 (4개)
├── .mcp.json            # MCP 서버 설정
└── README.md
```

## 개발

```bash
# 의존성 설치
cd /path/to/magic-note
bun install

# MCP 서버 초기화
mn init

# 플러그인 테스트
claude --plugin-dir ./plugin
```

## 라이센스

MIT License
