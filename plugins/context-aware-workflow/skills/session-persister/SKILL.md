---
name: session-persister
description: Saves and restores CAW workflow session state. Use at session start to restore previous state, and at session end to persist current progress for continuity.
allowed-tools: Read, Write, Glob, Bash
forked-context: true
forked-context-returns: |
  status: restored | saved | archived | fresh_start
  session: { task_title, progress_percentage }
  action: Summary of performed actions
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
2. **Manual**: User requests save/restore via `/cw:status`

## Session Data Structure

### Session File: `.caw/session.json`

Session data follows the `templates/session-template.json` schema.

**Key fields:**

| Field | Description |
|-------|-------------|
| `session_id` | Unique identifier (sess_YYYYMMDD_HHMMSS) |
| `workflow` | task_plan path, title, status |
| `progress` | Current phase/step, completed/pending step list |
| `context` | Active files, recent edits, unresolved questions |
| `metrics` | Insight/decision/quality gate counts |
| `notes` | Free-form notes |

**Example:**
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
🔄 Previous session found

Session: sess_20260104_143000
Task: JWT Authentication Implementation
Progress: Phase 2, Step 2.3 (45% complete)
Last Activity: 2 hours ago

Recent work:
  • src/auth/jwt.ts - Added token refresh logic
  • src/auth/middleware.ts - Modified validation middleware

[1] Continue previous session
[2] Check session status only (/cw:status)
[3] Start fresh (archive previous session)
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
💾 Session state saved

Progress: Phase 2, Step 2.3 (45%)
Files tracked: 4
Insights captured: 3

You can continue in the next session via /cw:status or automatic recovery.
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

- `/cw:status` - Shows current session state and offers save option
- `/cw:start` - Checks for existing session on workflow start

## User Commands

### Manual Save
```
"save session"
→ Immediate checkpoint with confirmation
```

### Manual Restore
```
"restore session"
→ Show available sessions, offer selection
```

### View History
```
"session history"
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

Backup to Serena memory when saving session for enhanced cross-session persistence:

```yaml
backup_to_serena:
  enabled: true  # Configurable in .claude/caw.local.md
  memory_name: "session_backup"
  trigger:
    - session_save
    - phase_complete
    - explicit_request
```

**Save workflow**:
```
On Session Save:
1. Write to .caw/session.json (existing method)
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

Check Serena memory first when restoring session:

```
On Session Restore:
1. Check .caw/session.json (existing method)
2. If not found or corrupted:
   - Check Serena: read_memory("session_backup")
   - If found: Offer to restore from Serena
3. Display available recovery options
```

**Serena restore prompt**:
```
⚠️ Local session file not found

🔍 Backup found in Serena memory:
   Task: JWT Authentication
   Progress: Phase 2, Step 2.3 (45%)
   Last Backup: 3 days ago

[1] Restore from Serena backup
[2] Start fresh
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
