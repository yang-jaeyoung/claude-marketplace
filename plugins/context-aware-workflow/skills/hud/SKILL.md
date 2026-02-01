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

Real-time workflow metrics during execution.

## Display Format

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 Phase 2/3 │ Step 2.3/5 │ ████████░░░░ 45%
 Tokens: 12.4k │ Cost: $0.23 │ Model: Sonnet
 Mode: DEEP_WORK │ Time: 4m 32s
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## Metrics Tracked

| Category | Metrics |
|----------|---------|
| Progress | phase, step, progress_pct, elapsed_time |
| Cost | tokens_used, estimated_cost, model_tier |
| Status | active_mode, eco_mode, background_tasks |

## Cost Calculation

```python
PRICING = {  # per 1M tokens
    "haiku": {"input": 0.25, "output": 1.25},
    "sonnet": {"input": 3.00, "output": 15.00},
    "opus": {"input": 15.00, "output": 75.00}
}
cost = (tokens_in * pricing["input"] + tokens_out * pricing["output"]) / 1_000_000
```

## Display Modes

| Mode | Output |
|------|--------|
| Full | All metrics formatted |
| Minimal | `[45%] Phase 2/3 │ Sonnet` |
| Silent | No display, metrics collected |

## Configuration

```bash
export CAW_HUD=enabled   # Full HUD
export CAW_HUD=minimal   # Progress only
export CAW_HUD=disabled  # Off (default)
```

## Usage

```bash
/cw:status --hud      # Show HUD inline
/cw:analytics --cost  # Cost breakdown
```

## State File (`.caw/hud.json`)

```json
{
  "enabled": true,
  "metrics": {
    "phase": 2, "total_phases": 3,
    "step": 3, "total_steps": 5,
    "progress_pct": 45,
    "tokens_in": 8500, "tokens_out": 3900,
    "estimated_cost": 0.23,
    "model_tier": "sonnet",
    "active_mode": "DEEP_WORK"
  }
}
```
