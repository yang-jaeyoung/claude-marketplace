---
description: Display token usage, cost analysis, and workflow optimization insights
argument-hint: "[--cost] [--tokens] [--sessions] [--export]"
---

# /cw:analytics - Workflow Analytics

Analyze token usage, cost breakdown, and workflow efficiency metrics.

## Usage

```bash
/cw:analytics           # Overview dashboard
/cw:analytics --cost    # Cost breakdown by model tier
/cw:analytics --tokens  # Token usage analysis
/cw:analytics --sessions # Multi-session comparison
/cw:analytics --export  # Export metrics to JSON
/cw:analytics --trends  # Usage trends over time
```

## Workflow

1. **Load**: Read `.caw/metrics.json` and aggregate session data
2. **Calculate**: Cost efficiency, model optimization, time efficiency
3. **Display**: Dashboard with usage, cost, distribution, insights

## Flags

| Flag | Description |
|------|-------------|
| `--cost` | Cost breakdown: current, weekly, monthly, top drivers |
| `--tokens` | Token analysis: I/O ratio, category breakdown, tips |
| `--sessions` | Compare last 5 sessions: tokens, cost, steps |
| `--export` | Export to `.caw/analytics_export_[date].json` |
| `--trends` | 30-day trends: daily avg, weekly trend, model shift |

## Output

```
━━━━━━━━━━━━━ WORKFLOW ANALYTICS ━━━━━━━━━━━━━
Session: abc123 | Duration: 1h 30m

TOKEN USAGE
  Input: 45,000 (79%) | Output: 12,000 (21%) | Total: 57,000

COST BREAKDOWN
  Haiku: 15K/$0.02 (4%) | Sonnet: 35K/$0.15 (29%) | Opus: 7K/$0.35 (67%)
  TOTAL: $0.52

OPTIMIZATION INSIGHTS
  • Opus 13% of tokens drove 67% of cost
  • Eco mode would save ~$0.18 (35%)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## Metrics Schema

See `schemas/metrics.schema.json` for complete schema definition.

Key fields: `token_usage`, `cost_breakdown`, `model_distribution`, `phase_metrics`, `background_tasks`, `eco_mode_savings`

## Integration

- **Reads**: `.caw/metrics.json`, `.caw/sessions/*.json`
- **Writes**: `.caw/analytics_export_*.json` (with --export)
- **Uses**: HUD skill for real-time metrics
- **Works with**: Eco mode, model routing, background heuristics

## Best Practices

1. Review weekly for cost trends
2. Use eco mode for simple tasks (saves 30-50%)
3. Monitor Opus usage (highest cost)
4. Track phase efficiency for bottlenecks
5. Export for team reviews
