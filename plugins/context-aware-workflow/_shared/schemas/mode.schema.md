# Mode State Schema

Defines the structure for `.caw/mode.json` - tracks the active workflow mode.

## Schema

```json
{
  "active_mode": "DEEP_WORK" | "MINIMAL_CHANGE" | "DEEP_ANALYSIS" | "RESEARCH" | "NORMAL",
  "activated_at": "ISO 8601 timestamp",
  "keyword_trigger": "string | null",
  "completion_required": boolean,
  "session_id": "string | null"
}
```

## Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `active_mode` | string | ✅ | Current active mode |
| `activated_at` | string | ✅ | ISO timestamp when mode was activated |
| `keyword_trigger` | string/null | ❌ | The keyword that triggered this mode |
| `completion_required` | boolean | ❌ | If true, all tasks must complete before stopping |
| `session_id` | string/null | ❌ | Optional session identifier |

## Mode Types

| Mode | Trigger Keywords | Behavior |
|------|------------------|----------|
| `DEEP_WORK` | deepwork, fullwork, ultrawork, nonstop, keepgoing | Complete ALL tasks without stopping |
| `DEEP_ANALYSIS` | thinkhard, ultrathink, think | Extended reasoning and validation |
| `MINIMAL_CHANGE` | quickfix, quick, fast | Minimal changes, speed priority |
| `RESEARCH` | research, investigate, explore | Comprehensive information gathering |
| `NORMAL` | (default) | Standard behavior |

## Example Files

### Deep Work Mode Active
```json
{
  "active_mode": "DEEP_WORK",
  "activated_at": "2025-01-14T10:30:00Z",
  "keyword_trigger": "deepwork",
  "completion_required": true
}
```

### Normal Mode (Default)
```json
{
  "active_mode": "NORMAL",
  "activated_at": "2025-01-14T10:30:00Z",
  "keyword_trigger": null,
  "completion_required": false
}
```

## Integration

- **Magic keywords**: Detected keywords set the active mode
- **/cw:status**: Displays active mode in status output
- **Agents**: Check mode.json to adapt behavior accordingly
