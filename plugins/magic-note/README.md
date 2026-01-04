# Magic Note Plugin for Claude Code

AI 코딩 워크플로우를 위한 노트 관리 플러그인입니다.

## 기능 개요

| 컴포넌트 | 개수 | 설명 |
|---------|------|------|
| **Commands** | 10개 | `/magic-note:*` 슬래시 명령어 |
| **Agents** | 3개 | 전문 작업 에이전트 |
| **Skills** | 8개 | AI 자동 호출 스킬 |
| **Hooks** | 4개 | 세션 이벤트 자동화 |
| **MCP Tools** | 30개 | 노트 및 워크플로우 관리 도구 |

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
| `/magic-note:insights` | 프로젝트별 인사이트 조회 | `/magic-note:insights my-app` |

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

### 노트 스킬

| 스킬 | 트리거 | 동작 |
|------|--------|------|
| `auto-save-plan` | 구현 계획 생성 시 | plan 노트로 저장 제안 |
| `prompt-library` | 코드 리뷰/리팩토링 요청 시 | 저장된 프롬프트 제안 |
| `decision-logger` | 기술 선택 결정 시 | choice 노트로 기록 제안 |
| `auto-capture-insight` | ★ Insight 블록 생성 시 | 프로젝트별 insight 자동 저장 |

### 워크플로우 스킬

| 스킬 | 트리거 | 동작 |
|------|--------|------|
| `workflow` | 복잡한 구현 계획 생성 시 | 워크플로우로 변환 제안 |
| `resume` | 기존 작업 재개 요청 시 | 진행 중인 워크플로우 로드 |
| `status` | 진행 상황 확인 요청 시 | 워크플로우 상태 요약 표시 |
| `checkpoint` | 중요 마일스톤 완료 시 | 체크포인트 생성 제안 |

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

### 노트 관리 (10개)

| 도구 | 설명 |
|------|------|
| `list_notes` | 노트 목록 조회 (필터 지원) |
| `get_note` | 노트 내용 조회 |
| `add_note` | 새 노트 추가 |
| `update_note` | 노트 수정 |
| `delete_note` | 노트 삭제 |
| `upsert_insight` | **인사이트 자동 누적 저장** (프로젝트별) |
| `list_templates` | 템플릿 목록 |
| `use_template` | 템플릿으로 노트 생성 |
| `list_projects` | 프로젝트 목록 |
| `list_tags` | 태그 목록 |

### 워크플로우 관리 (20개)

| 도구 | 설명 |
|------|------|
| `create_workflow` | 새 워크플로우 생성 |
| `get_workflow` | 워크플로우 조회 |
| `list_workflows` | 워크플로우 목록 (필터 지원) |
| `update_workflow` | 워크플로우 수정 |
| `delete_workflow` | 워크플로우 삭제 |
| `add_task` | 태스크 추가 |
| `update_task` | 태스크 수정 |
| `complete_task` | 태스크 완료 처리 |
| `fail_task` | 태스크 실패 처리 |
| `skip_task` | 태스크 건너뛰기 |
| `remove_task` | 태스크 제거 |
| `reorder_tasks` | 태스크 순서 변경 (배치) |
| `complete_step` | 스텝 완료 처리 |
| `get_workflow_status` | 워크플로우 상태 요약 |
| `get_next_batch` | 다음 실행 가능 태스크 조회 |
| `start_batch` | 배치 실행 시작 |
| `create_checkpoint` | 체크포인트 생성 |
| `restore_checkpoint` | 체크포인트 복원 |
| `link_artifact` | 노트-태스크/워크플로우 연결 |
| `unlink_artifact` | 노트-태스크/워크플로우 연결 해제 |

## 설치

### 요구사항

- Claude Code v1.0.33 이상
- 다음 런타임 중 하나 (우선순위 순):
  1. **[Bun](https://bun.sh/)** - 권장 (가장 빠름)
  2. **Node.js 22.18+ / 23.6+** - 네이티브 TypeScript 지원
  3. **Node.js + tsx** - 이전 Node.js 버전용 폴백

### 런타임 설치 (택 1)

#### 옵션 1: Bun (권장)

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

#### 옵션 2: Node.js 22.18+ (네이티브 TypeScript)

```bash
# nvm 사용
nvm install 22
nvm use 22

# 또는 공식 사이트에서 설치
# https://nodejs.org/

# 버전 확인 (22.18+ 또는 23.6+ 필요)
node --version
```

#### 옵션 3: Node.js + tsx (폴백)

```bash
# 기존 Node.js가 있다면 tsx만 설치
npm install -g tsx

# 또는 npx로 자동 실행 (별도 설치 불필요)
```

> ℹ️ **자동 감지**: Magic Note는 설치된 런타임을 자동으로 감지하여 최적의 옵션을 선택합니다.

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

### 인사이트 자동 캡처 (auto-capture-insight skill)

Learning/Explanatory 모드에서 ★ Insight 블록이 생성되면 자동으로 프로젝트별 노트에 누적 저장됩니다.

```
[Claude 응답 중 Insight 블록이 생성되면]

★ Insight ─────────────────────────────────────
React hooks 사용 시 주의사항:
- useEffect의 dependency array를 정확히 지정해야 무한 루프 방지
- useState의 setter는 비동기적으로 동작함
─────────────────────────────────────────────────

[자동으로 프로젝트의 insight 노트에 저장됨]
💡 Insight added to existing note!
Project: my-react-app
Total insights: 5
```

인사이트 확인:
```
/magic-note:insights my-react-app
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
| `insight` | 교육적 인사이트 (자동 수집) | 코딩 세션 중 학습한 내용 |

## 저장 위치

모든 데이터는 **프로젝트 로컬** `.magic-note/` 디렉토리에 저장됩니다.

```
your-project/
└── .magic-note/
    ├── config.yaml      # 설정
    ├── index.json       # 노트 인덱스
    ├── projects/        # 프로젝트별 노트
    ├── templates/       # 노트 템플릿
    ├── workflows/       # 워크플로우 데이터
    │   ├── index.json
    │   └── {workflowId}/
    │       ├── workflow.json
    │       ├── events.jsonl
    │       └── checkpoints/
    └── workspaces/      # 워크스페이스
```

### 프로젝트-로컬 스토리지의 장점

- **프로젝트 격리**: 각 프로젝트의 노트/워크플로우가 독립적으로 관리됨
- **버전 관리**: `.magic-note`를 git에 커밋하거나 `.gitignore`에 추가 가능
- **이식성**: 프로젝트 디렉토리와 함께 컨텍스트가 이동

### 커스텀 경로

환경변수로 저장 위치를 오버라이드할 수 있습니다:

```bash
export MAGIC_NOTE_STORAGE=/custom/path/.magic-note
```

## 플러그인 구조

```
plugin/
├── .claude-plugin/
│   ├── plugin.json      # 플러그인 메타데이터
│   └── marketplace.json # 마켓플레이스 카탈로그
├── commands/            # 슬래시 명령어 (10개)
│   ├── add.md
│   ├── list.md
│   ├── save.md
│   ├── load.md
│   ├── search.md
│   ├── view.md
│   ├── edit.md
│   ├── delete.md
│   ├── copy.md
│   └── insights.md
├── agents/              # 전문 에이전트 (3개)
│   ├── note-organizer.md
│   ├── prompt-curator.md
│   └── plan-reviewer.md
├── skills/              # AI 자동 호출 스킬 (8개)
│   ├── auto-save-plan/
│   ├── prompt-library/
│   ├── decision-logger/
│   ├── auto-capture-insight/
│   ├── workflow/
│   ├── resume/
│   ├── status/
│   └── checkpoint/
├── hooks/
│   └── hooks.json       # 이벤트 훅 (4개)
├── .mcp.json            # MCP 서버 설정
└── README.md
```

## 개발

```bash
# 의존성 설치
cd /path/to/magic-note
npm install  # 또는 bun install

# MCP 서버 테스트 (런타임 자동 감지)
node bin/launcher.mjs

# 또는 특정 런타임으로 직접 실행
bun run src/mcp/server.ts           # Bun
node src/mcp/server.ts              # Node.js 22.18+
npx tsx src/mcp/server.ts           # Node.js + tsx

# 플러그인 테스트
claude --plugin-dir .
```

### 지원 플랫폼

| 플랫폼 | Bun | Node.js |
|--------|:---:|:-------:|
| macOS (Intel) | ✅ | ✅ |
| macOS (Apple Silicon) | ✅ | ✅ |
| Windows x64 | ✅ | ✅ |
| Windows ARM | ❌ | ✅ |
| Linux x64 | ✅ | ✅ |
| Linux ARM | ✅ | ✅ |

## 라이센스

MIT License
