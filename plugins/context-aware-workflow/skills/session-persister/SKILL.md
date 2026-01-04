---
name: session-persister
description: Saves and restores CAW workflow session state. Use at session start to restore previous state, and at session end to persist current progress for continuity.
allowed-tools: Read, Write, Glob, Bash
---

# Session Persister

Maintain workflow continuity across Claude Code sessions by persisting and restoring state.

## Triggers

This skill activates:
1. **SessionStart**: Check for existing session to restore
2. **Stop/Session End**: Save current session state
3. **Periodic**: Checkpoint every 30 minutes of activity
4. **Manual**: User requests save/restore

## Session Data Structure

### Session File: `.caw/sessions/current.json`

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
1. Check for .caw/sessions/current.json
2. If exists and recent (< 24 hours):
   - Display session summary
   - Offer restore options
3. If exists but old (> 24 hours):
   - Offer to archive and start fresh
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

### On Session End (Save)

```
1. Gather current state:
   - Parse task_plan.md for progress
   - Identify active context files
   - Collect any pending questions
2. Write to .caw/sessions/current.json
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

### Periodic Checkpoint

```
1. Every 30 minutes of activity
2. After completing each Step
3. After major file edits
4. Silent save (no prompt)
5. Brief indicator: "📌 Checkpoint saved"
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
└── sessions/
    ├── current.json              # Active session
    └── archive/
        ├── sess_20260103_100000.json
        └── sess_20260102_140000.json
```

## Archive Management

### Auto-Archive Rules

```yaml
archive_policy:
  trigger:
    - new_task_started
    - session_older_than: 24h
    - user_request

  retention:
    max_archived: 10
    max_age_days: 30

  cleanup:
    delete_oldest_when_full: true
```

### Archive Format

Archived sessions are moved to `.caw/sessions/archive/` with original session ID as filename.

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

### With Hooks

```json
{
  "SessionStart": [
    {
      "hooks": [{
        "type": "skill",
        "skill": "session-persister",
        "action": "restore"
      }]
    }
  ],
  "Stop": [
    {
      "hooks": [{
        "type": "skill",
        "skill": "session-persister",
        "action": "save"
      }]
    }
  ]
}
```

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

## Boundaries

**Will:**
- Automatically save session on exit
- Restore session on start (with confirmation)
- Maintain session history
- Handle corrupted states gracefully

**Will Not:**
- Save sensitive information (credentials, tokens)
- Automatically restore without user confirmation
- Keep sessions indefinitely (30-day max)
- Sync across different machines
