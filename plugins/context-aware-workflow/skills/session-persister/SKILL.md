---
name: session-persister
description: Saves and restores CAW workflow session state for continuity across sessions
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
---

# Session Persister

Maintain workflow continuity across Claude Code sessions.

## Triggers

1. **SessionStart**: Check for existing session
2. **Manual**: `/cw:status` save/restore

## Session Data (`.caw/session.json`)

| Field | Description |
|-------|-------------|
| session_id | sess_YYYYMMDD_HHMMSS |
| workflow | task_plan path, title, status |
| progress | current_phase, current_step, percentage |
| context | active_files, recent_edits, questions |
| metrics | insight/decision/quality gate counts |

## Behavior

### On Session Start (Restore)

```
1. Check .caw/session.json
2. If recent (<24h): Display summary, offer restore
3. If old (>24h): Offer fresh start
4. If not exists: Silent continue
```

**Restore Prompt:**
```
🔄 Previous session found

Task: JWT Authentication | Progress: 45% | Last: 2 hours ago
Recent: src/auth/jwt.ts, src/auth/middleware.ts

[1] Continue | [2] Check status | [3] Start fresh
```

### On Save

```
💾 Session saved: Progress 45% | Files: 4 | Insights: 3
```

## Recovery Scenarios

| Scenario | Action |
|----------|--------|
| Clean Resume | Restore context, continue |
| Plan Modified | Warn, offer sync or restart |
| Corrupted State | Archive, recover from task_plan.md |
| Multiple Sessions | Ask user to select |

## Serena Integration

```yaml
backup_to_serena:
  memory_name: session_backup
  trigger: [session_save, phase_complete]

restore_priority:
  1: .caw/session.json (local)
  2: Serena session_backup
  3: Parse task_plan.md
  4: Fresh start
```

## Integration

| Skill | Integration |
|-------|-------------|
| progress-tracker | Includes progress metrics |
| insight-collector | Tracks insight count |
| context-helper | Provides context priority |

## Boundaries

**Will:** Auto-save on exit, restore with confirmation, maintain history, backup to Serena
**Won't:** Save credentials, auto-restore without confirmation, keep >30 days, sync across machines
