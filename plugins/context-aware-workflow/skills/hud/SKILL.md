---
name: hud
description: Real-time Heads-Up Display for workflow metrics and progress
allowed-tools:
  - Read
  - Grep
  - Bash
context:
  - .caw/manifest.json
  - .caw/mode.json
  - .caw/metrics.json
---

# HUD (Heads-Up Display)

Real-time workflow metrics display during task execution.

## Purpose

The HUD provides at-a-glance visibility into:
- Current phase and step progress
- Token usage and estimated cost
- Active model tier
- Execution mode status

## Display Format

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 Phase 2/3 │ Step 2.3/5 │ ████████░░░░ 45%
 Tokens: 12.4k │ Cost: $0.23 │ Model: Sonnet
 Mode: DEEP_WORK │ Time: 4m 32s
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## Metrics Tracked

### Progress Metrics
| Metric | Source | Description |
|--------|--------|-------------|
| `phase` | manifest.json | Current workflow phase (1-N) |
| `step` | manifest.json | Current step within phase |
| `progress_pct` | Calculated | Overall completion percentage |
| `elapsed_time` | Session start | Time since workflow began |

### Cost Metrics
| Metric | Source | Description |
|--------|--------|-------------|
| `tokens_used` | metrics.json | Total tokens consumed |
| `estimated_cost` | Calculated | Cost based on model pricing |
| `model_tier` | mode.json | Current model (Haiku/Sonnet/Opus) |

### Status Metrics
| Metric | Source | Description |
|--------|--------|-------------|
| `active_mode` | mode.json | DEEP_WORK, RESEARCH, ECO, etc. |
| `eco_mode` | mode.json | Cost optimization active |
| `background_tasks` | metrics.json | Pending async tasks |

## Cost Calculation

```python
PRICING = {
    "haiku": {"input": 0.25, "output": 1.25},    # per 1M tokens
    "sonnet": {"input": 3.00, "output": 15.00},
    "opus": {"input": 15.00, "output": 75.00}
}

def calculate_cost(tokens_in, tokens_out, model):
    pricing = PRICING[model]
    return (tokens_in * pricing["input"] + tokens_out * pricing["output"]) / 1_000_000
```

## Progress Bar Rendering

```python
def render_progress_bar(percentage, width=12):
    filled = int(width * percentage / 100)
    empty = width - filled
    return "█" * filled + "░" * empty
```

## Integration Points

### PostToolUse Hook

The HUD updates after each tool use:

```json
{
  "PostToolUse": [{
    "matcher": "*",
    "hooks": [{
      "type": "command",
      "command": "python3 \"${CLAUDE_PLUGIN_ROOT}/skills/hud/update_hud.py\""
    }]
  }]
}
```

### Status Command

Display HUD via `/cw:status --hud`:

```bash
/cw:status --hud  # Show HUD inline
/cw:status        # Standard status (HUD shown if enabled)
```

## Configuration

### Enable/Disable HUD

```bash
# Enable HUD display
export CAW_HUD=enabled

# Disable HUD (default)
export CAW_HUD=disabled

# Minimal HUD (progress only)
export CAW_HUD=minimal
```

### HUD State File

HUD state is stored in `.caw/hud.json`:

```json
{
  "enabled": true,
  "last_update": "2024-01-15T10:35:00Z",
  "display_mode": "full",
  "metrics": {
    "phase": 2,
    "total_phases": 3,
    "step": 3,
    "total_steps": 5,
    "progress_pct": 45,
    "tokens_in": 8500,
    "tokens_out": 3900,
    "estimated_cost": 0.23,
    "model_tier": "sonnet",
    "active_mode": "DEEP_WORK",
    "elapsed_seconds": 272
  }
}
```

## Display Modes

### Full Mode (default)
Shows all metrics in formatted display.

### Minimal Mode
Shows only progress percentage:
```
[45%] Phase 2/3 │ Sonnet
```

### Silent Mode
No display, metrics collected only.

## Usage Examples

### During Workflow

```bash
# Start workflow with HUD enabled
CAW_HUD=enabled /cw:start "implement user authentication"

# HUD automatically displays after each step
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  Phase 1/3 │ Step 1/4 │ ██░░░░░░ 25%
#  Tokens: 3.2k │ Cost: $0.08 │ Sonnet
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Manual HUD Query

```bash
# Show current HUD state
/cw:status --hud

# Show cost breakdown
/cw:analytics --cost
```

## Best Practices

1. **Enable for long workflows**: HUD is most useful for deepwork/ultrawork
2. **Use minimal mode for quick tasks**: Reduces visual noise
3. **Monitor cost in eco mode**: Verify savings
4. **Check progress on complex tasks**: Ensure workflow is progressing

## Related Skills

- [Progress Tracker](../progress-tracker/SKILL.md) - Detailed progress tracking
- [Dashboard](../dashboard/SKILL.md) - Full dashboard display
- [Insight Collector](../insight-collector/SKILL.md) - Metrics collection
