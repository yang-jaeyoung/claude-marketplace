# Session Management

## Session File Structure

Location: `.caw/session.json`

```json
{
  "session_id": "[task-id]-[YYYYMMDD]",
  "task_id": "[task-name]",
  "last_updated": "[ISO8601]",
  "current_phase": 1,
  "current_step": "1.1",
  "progress_percentage": 0,
  "context_snapshot": {
    "active_files": [],
    "completed_steps": []
  }
}
```

## Session Restore Workflow

```
1. Check: Read .caw/session.json
2. If exists:
   - Check last_updated, current_step
   - Ask user: [1] Resume | [2] New (keep data) | [3] New (clear)
3. On resume:
   - Load task_plan.md, context_manifest.json, metrics.json
   - Continue from current_step
```

## Session Save (on checkpoint/exit)

```
1. Update session.json with current state
2. Save context_manifest.json
3. Update metrics.json (progress)
```
