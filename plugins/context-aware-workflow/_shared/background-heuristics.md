# Background Task Heuristics

Pattern-based automatic background execution decisions for CAW workflow.

## Overview

The Background Heuristics system automatically determines whether tasks should run in the background (async) or foreground (blocking) based on pattern matching. This enables intelligent parallelization without manual configuration.

## Configuration

Heuristics are evaluated in order of priority. First matching pattern wins.

### Foreground Patterns (Highest Priority)

Tasks matching these patterns **always run in foreground** for immediate feedback:

| Pattern | Rationale |
|---------|-----------|
| `security` | Security-critical operations need immediate attention |
| `critical` | Critical issues must block progress |
| `blocking` | Explicitly marked as blocking |
| `urgent` | Time-sensitive operations |
| `auth|authentication` | Authentication flows need immediate feedback |
| `credential|secret|key` | Credential handling requires attention |

### Background Patterns

Tasks matching these patterns run in background by default:

| Pattern | Timeout | Rationale |
|---------|---------|-----------|
| `lint\|format\|style` | 30s | Code style checks are non-blocking |
| `gemini\|external_review` | 45s | External API calls should not block |
| `test\|spec` | 60s | Tests can run asynchronously |
| `build\|compile` | 120s | Build processes are long-running |
| `deploy\|publish` | 180s | Deployment is inherently async |
| `validate\|check` | 30s | Validation passes quietly |

## Pattern Matching Rules

```yaml
background_heuristics:
  # Foreground patterns (checked first, force blocking)
  foreground_patterns:
    - pattern: "security|critical|blocking|urgent"
      force: true
    - pattern: "auth|authentication|credential|secret|key"
      force: true

  # Background patterns (async execution)
  background_patterns:
    - pattern: "lint|format|style|prettier|eslint"
      timeout: 30
      silent: true
    - pattern: "gemini|external_review|external_check"
      timeout: 45
      silent: false
    - pattern: "test|spec|jest|pytest|vitest"
      timeout: 60
      silent: false
    - pattern: "build|compile|webpack|vite|tsc"
      timeout: 120
      silent: false
    - pattern: "validate|check|verify"
      timeout: 30
      silent: true
```

## Decision Algorithm

```
FUNCTION should_run_background(task_name: string, context: dict) -> (bool, int):

  # [1] Check explicit user override
  IF context.force_foreground:
    RETURN (false, 0)
  IF context.force_background:
    RETURN (true, context.timeout or 30)

  # [2] Check foreground patterns (priority)
  FOR pattern IN foreground_patterns:
    IF regex_match(pattern, task_name):
      RETURN (false, 0)  # Force foreground

  # [3] Check background patterns
  FOR pattern, config IN background_patterns:
    IF regex_match(pattern, task_name):
      RETURN (true, config.timeout)

  # [4] Default: foreground for unknown tasks
  RETURN (false, 0)
```

## Integration Points

### With Hooks

In `hooks.json`, async execution is controlled by:

```json
{
  "type": "command",
  "command": "python3 script.py",
  "async": true,
  "timeout": 45
}
```

The heuristics system can suggest or auto-configure these settings based on the command pattern.

### With Model Routing

Background tasks typically use lower tiers:
- Background validation → Haiku
- Background review → Haiku/Sonnet
- Foreground critical → Sonnet/Opus

### With Magic Keywords

Keywords can override heuristics:
- `nowait`, `async`, `background` → Force background
- `wait`, `sync`, `blocking` → Force foreground

## Environment Variables

| Variable | Effect |
|----------|--------|
| `CAW_FORCE_FOREGROUND=1` | Disable all background execution |
| `CAW_FORCE_BACKGROUND=1` | Force async for all heuristic-matched tasks |
| `CAW_BACKGROUND_TIMEOUT=N` | Override default timeout (seconds) |

## Usage Examples

### Automatic Detection

```bash
# Gemini review → auto-background (45s timeout)
python3 gemini_edit_review.py

# Security audit → forced foreground
python3 security_scan.py

# ESLint check → auto-background (30s timeout, silent)
npx eslint --fix
```

### Manual Override

```bash
# Force foreground for normally-async task
CAW_FORCE_FOREGROUND=1 python3 gemini_edit_review.py

# Extend timeout for slow external service
CAW_BACKGROUND_TIMEOUT=90 python3 external_api_check.py
```

## Metrics Collection

Background task metrics are captured for analytics:

```json
{
  "background_tasks": {
    "total": 42,
    "completed": 40,
    "timed_out": 2,
    "average_duration_ms": 12500,
    "by_pattern": {
      "lint|format": {"count": 25, "avg_ms": 3200},
      "gemini|external": {"count": 12, "avg_ms": 28000},
      "test|spec": {"count": 5, "avg_ms": 45000}
    }
  }
}
```

## Best Practices

1. **Trust the defaults**: Heuristics are tuned for common workflows
2. **Override sparingly**: Only force foreground for truly blocking operations
3. **Monitor timeouts**: Adjust timeouts based on actual execution times
4. **Use silent mode**: Enable for frequent, low-priority checks
5. **Review metrics**: Analyze background task performance periodically

## Related Documentation

- [Magic Keywords](./magic-keywords.md) - Override keywords
- [Model Routing](./model-routing.md) - Tier selection for background tasks
- [Parallel Execution](./parallel-execution.md) - Parallel task management
