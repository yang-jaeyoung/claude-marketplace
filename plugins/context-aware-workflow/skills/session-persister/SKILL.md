---
name: session-persister
description: Saves and restores CAW workflow session state. Use at session start to restore previous state, and at session end to persist current progress for continuity.
allowed-tools: Read, Write, Glob, Bash
forked-context: true
forked-context-returns: |
  status: restored | saved | archived | fresh_start
  session: { task_title, progress_percentage }
  action: 수행된 작업 요약
hooks:
  SessionStart:
    action: restore
    priority: 1
    condition: "requires .caw/ directory"
---

# Session Persister

Maintain workflow continuity across Claude Code sessions by persisting and restoring state.

## Triggers

This skill activates:
1. **SessionStart**: Check for existing session to restore
2. **Manual**: User requests save/restore via `/caw:status`

## Session Data Structure

### Session File: `.caw/session.json`

세션 데이터는 `templates/session-template.json` 스키마를 따릅니다.

**주요 필드:**

| 필드 | 설명 |
|------|------|
| `session_id` | 고유 식별자 (sess_YYYYMMDD_HHMMSS) |
| `workflow` | task_plan 경로, 제목, 상태 |
| `progress` | 현재 phase/step, 완료/대기 step 목록 |
| `context` | 활성 파일, 최근 편집, 미해결 질문 |
| `metrics` | 인사이트/결정/품질게이트 카운트 |
| `notes` | 자유 형식 메모 |

**예시:**
```json
{
  "session_id": "sess_20260104_143000",
  "workflow": {
    "task_plan": ".caw/task_plan.md",
    "task_title": "JWT Authentication",
    "status": "in_progress"
  },
  "progress": {
    "current_phase": "phase_2",
    "current_step": "2.3",
    "progress_percentage": 45
  }
}
```

## Behavior

### On Session Start (Restore)

```
1. Check for .caw/session.json
2. If exists and recent (< 24 hours):
   - Display session summary
   - Offer restore options
3. If exists but old (> 24 hours):
   - Offer to start fresh
4. If not exists:
   - Silent continue (no action needed)
```

**Restore Prompt:**
```
🔄 이전 세션 발견

Session: sess_20260104_143000
Task: JWT Authentication Implementation
Progress: Phase 2, Step 2.3 (45% 완료)
Last Activity: 2시간 전

최근 작업:
  • src/auth/jwt.ts - 토큰 갱신 로직 추가
  • src/auth/middleware.ts - 검증 미들웨어 수정

[1] 이전 세션 이어서 진행
[2] 세션 상태 확인만 (/caw:status)
[3] 새로 시작 (이전 세션 아카이브)
```

### On Manual Save

```
1. Gather current state:
   - Parse task_plan.md for progress
   - Identify active context files
   - Collect any pending questions
2. Write to .caw/session.json
3. Display save confirmation
```

**Save Confirmation:**
```
💾 세션 상태 저장됨

Progress: Phase 2, Step 2.3 (45%)
Files tracked: 4개
Insights captured: 3개

다음 세션에서 /caw:status 또는 자동 복구로 이어서 진행할 수 있습니다.
```

## Directory Structure

### Skill Files
```
skills/session-persister/
├── SKILL.md                      # This file
└── templates/
    └── session-template.json     # Session data schema
```

### Runtime Files
```
.caw/
├── session.json                  # Current session state
└── archives/
    └── session_YYYYMMDD.json     # Archived sessions
```

## State Extraction

### From task_plan.md

```yaml
extract:
  title: "# Task Plan: {title}"
  phases:
    pattern: "### Phase {n}: {name}"
    steps:
      pattern: "| {step_id} | {description} | {status} |"
      status_map:
        "✅": completed
        "🔄": in_progress
        "⏳": pending
```

### From Context

```yaml
context_files:
  source: ".caw/context_manifest.json"
  fallback:
    - Recently read files (last 10)
    - Recently edited files (last 5)
```

## Recovery Scenarios

### Scenario 1: Clean Resume
```
Previous session exists, task_plan matches
→ Restore context, continue from current_step
```

### Scenario 2: Plan Modified
```
Previous session exists, but task_plan changed
→ Warn user, offer to sync or restart
```

### Scenario 3: Corrupted State
```
Session file exists but invalid
→ Archive corrupted file, start fresh
→ Attempt to recover from task_plan.md
```

### Scenario 4: Multiple Sessions
```
Multiple .caw/ directories found (monorepo)
→ Ask user to select project context
```

## Integration

### With Other Skills

| Skill | Integration |
|-------|-------------|
| progress-tracker | Session includes progress metrics |
| insight-collector | Session tracks insight count |
| context-helper | Session provides context priority |
| quality-gate | Session records validation results |

### With Commands

- `/caw:status` - Shows current session state and offers save option
- `/caw:start` - Checks for existing session on workflow start

## User Commands

### Manual Save
```
"save session" or "세션 저장"
→ Immediate checkpoint with confirmation
```

### Manual Restore
```
"restore session" or "세션 복구"
→ Show available sessions, offer selection
```

### View History
```
"session history" or "세션 기록"
→ List recent sessions with summaries
```

## Error Handling

```yaml
errors:
  file_write_failed:
    action: retry_once
    fallback: warn_user

  corrupted_json:
    action: backup_and_recreate
    notify: true

  missing_task_plan:
    action: create_minimal_session
    note: "Task plan not found, saving basic state"
```

## Serena Memory Integration (NEW)

### Backup to Serena

세션 저장 시 Serena 메모리에도 백업하여 크로스 세션 영속성 강화:

```yaml
backup_to_serena:
  enabled: true  # .claude/caw.local.md에서 설정 가능
  memory_name: "session_backup"
  trigger:
    - session_save
    - phase_complete
    - explicit_request
```

**저장 워크플로우**:
```
On Session Save:
1. Write to .caw/session.json (기존 방식)
2. If serena_backup enabled:
   write_memory("session_backup", {
     session_id: "[id]",
     task_title: "[title]",
     progress: { current_phase, current_step, percentage },
     last_updated: "[ISO timestamp]",
     context_summary: "[active files summary]"
   })
3. Display: "💾 Session saved (+ Serena backup)"
```

### Restore from Serena

세션 복원 시 Serena 메모리 우선 체크:

```
On Session Restore:
1. Check .caw/session.json (기존 방식)
2. If not found or corrupted:
   - Check Serena: read_memory("session_backup")
   - If found: Offer to restore from Serena
3. Display available recovery options
```

**Serena 복원 프롬프트**:
```
⚠️ 로컬 세션 파일 없음

🔍 Serena 메모리에서 백업 발견:
   Task: JWT Authentication
   Progress: Phase 2, Step 2.3 (45%)
   Last Backup: 3일 전

[1] Serena 백업에서 복원
[2] 새로 시작
```

### Priority Order

```yaml
restore_priority:
  1: .caw/session.json (local, most recent)
  2: Serena session_backup (cross-session)
  3: Parse from .caw/task_plan.md (fallback)
  4: Fresh start
```

## Boundaries

**Will:**
- Automatically save session on exit
- Restore session on start (with confirmation)
- Maintain session history
- Handle corrupted states gracefully
- **Backup to Serena memory (if enabled)**
- **Restore from Serena if local not available**

**Will Not:**
- Save sensitive information (credentials, tokens)
- Automatically restore without user confirmation
- Keep sessions indefinitely (30-day max)
- Sync across different machines
- **Overwrite Serena backup without confirmation**

## Forked Context Behavior

See [Forked Context Pattern](../../_shared/forked-context.md).

**Returns**: `status: restored | saved | archived | fresh_start` with session summary

**Output Examples:**
- `🔄 Session Restored` - Task: [title], Progress: [%]
- `💾 Session Saved` - Progress: [%] | Files: N
- `🆕 Fresh Start` - Previous archived
- `⚠️ Recovery Failed` - Reason + action
