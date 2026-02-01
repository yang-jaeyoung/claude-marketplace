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
/cw:analytics --trends  # Show usage trends over time
```

## Behavior

### Step 1: Load Metrics

Read from `.caw/metrics.json` and aggregate session data:

```json
{
  "session_id": "abc123",
  "started_at": "2024-01-15T10:00:00Z",
  "ended_at": "2024-01-15T11:30:00Z",
  "token_usage": {
    "input": 45000,
    "output": 12000,
    "total": 57000
  },
  "cost_breakdown": {
    "haiku": {"tokens": 15000, "cost": 0.02},
    "sonnet": {"tokens": 35000, "cost": 0.15},
    "opus": {"tokens": 7000, "cost": 0.35}
  },
  "model_distribution": {
    "haiku": 0.26,
    "sonnet": 0.61,
    "opus": 0.13
  },
  "phase_metrics": {
    "planning": {"tokens": 12000, "duration_s": 300},
    "implementation": {"tokens": 38000, "duration_s": 4200},
    "review": {"tokens": 7000, "duration_s": 600}
  }
}
```

### Step 2: Calculate Insights

```python
# Cost efficiency
cost_per_step = total_cost / completed_steps
avg_tokens_per_step = total_tokens / completed_steps

# Model optimization
haiku_savings = (sonnet_cost - haiku_cost) if haiku_used else 0
eco_mode_savings = calculate_eco_savings()

# Time efficiency
tokens_per_minute = total_tokens / (duration_s / 60)
```

### Step 3: Display Analytics

**Standard Output:**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
               WORKFLOW ANALYTICS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Session: abc123 | Duration: 1h 30m

TOKEN USAGE
───────────────────────────────────────────────
Input:   45,000 tokens (79%)
Output:  12,000 tokens (21%)
Total:   57,000 tokens

COST BREAKDOWN
───────────────────────────────────────────────
Model        Tokens     Cost      %
─────────────────────────────────────────
Haiku        15,000     $0.02     4%
Sonnet       35,000     $0.15     29%
Opus          7,000     $0.35     67%
─────────────────────────────────────────
TOTAL        57,000     $0.52    100%

MODEL DISTRIBUTION
───────────────────────────────────────────────
Haiku:  ██████░░░░░░░░░░░░░░ 26%
Sonnet: ████████████░░░░░░░░ 61%
Opus:   ███░░░░░░░░░░░░░░░░░ 13%

PHASE METRICS
───────────────────────────────────────────────
Phase          Tokens    Time     Efficiency
───────────────────────────────────────────────
Planning       12,000    5m       2.4k/min
Implementation 38,000    1h 10m   540/min
Review          7,000    10m      700/min

OPTIMIZATION INSIGHTS
───────────────────────────────────────────────
• Opus usage for 13% of tokens drove 67% of cost
• Consider: Use Sonnet for initial review, Opus for deep analysis
• Eco mode would save ~$0.18 (35%) on this workflow
• Implementation phase used 67% of tokens

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## Flags

### --cost

Focus on cost analysis:

```
COST ANALYSIS
───────────────────────────────────────────────
Current Session:    $0.52
Last 7 days:        $12.45
This month:         $28.90

Cost Trend:
Mon │ ██░░░░░░░░ $1.20
Tue │ █████░░░░░ $2.80
Wed │ ███░░░░░░░ $1.60
Thu │ ██████░░░░ $3.20
Fri │ ████░░░░░░ $2.10
Sat │ █░░░░░░░░░ $0.80
Sun │ █░░░░░░░░░ $0.75

Top Cost Drivers:
1. Opus deep reviews: $4.20 (33%)
2. Complex implementations: $3.80 (30%)
3. Architecture planning: $2.40 (19%)
```

### --tokens

Focus on token analysis:

```
TOKEN ANALYSIS
───────────────────────────────────────────────
Input/Output Ratio: 3.75:1

By Category:
Context loading:  18,000 (32%)
Code generation:  22,000 (39%)
Review/analysis:  12,000 (21%)
Other:             5,000 (8%)

Optimization Tips:
• High context loading suggests opportunity to prune
• Consider using --focus flag to reduce context
```

### --sessions

Compare multiple sessions:

```
SESSION COMPARISON (Last 5)
───────────────────────────────────────────────
Session     Date        Tokens    Cost    Steps
───────────────────────────────────────────────
abc123      Jan 15      57,000    $0.52   12
xyz789      Jan 14      42,000    $0.38   8
def456      Jan 13      89,000    $0.95   18
ghi012      Jan 12      31,000    $0.28   6
jkl345      Jan 11      55,000    $0.48   11

Average: 54,800 tokens | $0.52 | 11 steps
```

### --export

Export metrics to JSON file:

```bash
/cw:analytics --export
# Creates: .caw/analytics_export_20240115.json
```

### --trends

Show usage trends:

```
USAGE TRENDS (Last 30 days)
───────────────────────────────────────────────
Daily Avg:    45,000 tokens | $0.42
Weekly Trend: ↗ +15% tokens, +12% cost

Model Shift:
Week 1: Opus 25% → Week 4: Opus 13%
Cost savings from tier optimization: $8.40 (18%)

Busiest Days: Tuesday, Thursday
Quietest Day: Sunday
```

## Metrics Schema

See `schemas/metrics.schema.json` for complete schema definition.

Key fields:
- `token_usage`: Input/output token counts
- `cost_breakdown`: Cost by model tier
- `model_distribution`: Percentage of tokens per tier
- `phase_metrics`: Tokens and duration per workflow phase
- `background_tasks`: Async task statistics
- `eco_mode_savings`: Calculated savings from eco mode

## Integration

- **Reads**: `.caw/metrics.json`, `.caw/sessions/*.json`
- **Writes**: `.caw/analytics_export_*.json` (with --export)
- **Uses**: HUD skill for real-time metrics
- **Works with**: Eco mode, model routing, background heuristics

## Best Practices

1. **Review weekly**: Check cost trends and optimize model usage
2. **Use eco mode**: For simple tasks, eco mode saves 30-50%
3. **Monitor Opus usage**: Highest cost, use only when needed
4. **Track phase efficiency**: Identify bottlenecks
5. **Export for reporting**: Use --export for team reviews
