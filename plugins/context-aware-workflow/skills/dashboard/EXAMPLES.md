# Dashboard Examples

Real-world usage examples for the insight-collector dashboard.

## Basic Usage

### Generate Dashboard

```bash
cd /path/to/your/project
python3 "${CLAUDE_PLUGIN_ROOT}/skills/insight-collector/scripts/dashboard.py"
```

Output:
```
✅ Dashboard generated: /path/to/project/.caw/dashboard.html
```

### Generate and Open in Browser

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/insight-collector/scripts/dashboard.py" --open
```

Output:
```
✅ Dashboard generated: /path/to/project/.caw/dashboard.html
🌐 Opening in browser...
```

### Custom Output Path

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/insight-collector/scripts/dashboard.py" -o /tmp/report.html
```

Output:
```
✅ Dashboard generated: /tmp/report.html
```

## Via instinct-cli

### Quick Dashboard Generation

```bash
python3 scripts/instinct-cli.py dashboard
```

### Full Workflow

```bash
# 1. Analyze observations to generate instincts
python3 scripts/instinct-cli.py analyze --incremental

# 2. View instincts
python3 scripts/instinct-cli.py list

# 3. Generate and open dashboard
python3 scripts/instinct-cli.py dashboard --open
```

## Integration with Workflow

### End-of-Session Report

```bash
#!/bin/bash
# session-report.sh - Generate analytics after work session

echo "📊 Generating session report..."

# Analyze new observations
python3 scripts/instinct-cli.py analyze --incremental

# Show stats
python3 scripts/instinct-cli.py stats

# Generate dashboard
python3 scripts/instinct-cli.py dashboard --open

echo "✅ Report ready!"
```

### Scheduled Daily Report

```bash
#!/bin/bash
# daily-report.sh - Generate daily analytics dashboard

DATE=$(date +%Y%m%d)
OUTPUT="reports/dashboard-$DATE.html"

mkdir -p reports

python3 scripts/instinct-cli.py analyze --full
python3 scripts/instinct-cli.py dashboard -o "$OUTPUT"

echo "📊 Daily report: $OUTPUT"
```

### CI/CD Integration

```yaml
# .github/workflows/insight-report.yml
name: Generate Insight Report

on:
  schedule:
    - cron: '0 0 * * 0'  # Weekly on Sunday
  workflow_dispatch:

jobs:
  report:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Generate dashboard
        run: |
          python3 skills/insight-collector/scripts/dashboard.py -o dashboard.html

      - name: Upload artifact
        uses: actions/upload-artifact@v3
        with:
          name: insight-dashboard
          path: dashboard.html
```

## Sample Output Structure

### With Active Data

```
🔍 Insight Collector Dashboard
Generated: 2026-01-27 16:00:00 UTC

📊 Observations: 1,247
💡 Instincts: 23
⚡ Evolutions: 5
📈 Avg Confidence: 68%

🔥 Tool Usage Heatmap (by hour)
[24-hour grid showing activity peaks at 10h, 14h, 16h]

🛠️ Top Tools
Read        ████████████████████ 387 (31.0%)
Edit        ███████████████      245 (19.6%)
Grep        ████████████         198 (15.9%)
Bash        ██████████           156 (12.5%)
Write       ████████             123 (9.9%)
...

📋 Instinct Registry
ID                              Confidence    %    Evidence  Domain
read-before-edit               ██████████    90%     12      preference
prefer-grep-before-edit        ███████░░░    70%      5      workflow
verify-after-change            ██████░░░░    60%      4      workflow
...

🚀 Evolution Timeline
2026-01-27 14:30  Command: validate-schema
2026-01-27 12:15  Skill: auto-format
2026-01-26 16:45  Agent: code-reviewer
...

🧩 Pattern Summary
Workflow: 12
Preference: 8
Error-handling: 3
```

### With Minimal Data

```
🔍 Insight Collector Dashboard
Generated: 2026-01-27 10:00:00 UTC

📊 Observations: 9
💡 Instincts: 3
⚡ Evolutions: 1
📈 Avg Confidence: 73%

🔥 Tool Usage Heatmap (by hour)
[Mostly empty grid with a few cells at 10h, 14h]

🛠️ Top Tools
Read        ████████             3 (33.3%)
Edit        ████████             2 (22.2%)
Grep        ████                 2 (22.2%)
Bash        ████                 2 (22.2%)

📋 Instinct Registry
ID                              Confidence    %    Evidence  Domain
read-before-edit               █████████░    90%     12      preference
prefer-grep-before-edit        ███████░░░    70%      5      workflow
verify-after-change            ██████░░░░    60%      4      workflow

🚀 Evolution Timeline
2026-01-27 09:30  Command: test-command

🧩 Pattern Summary
Workflow: 2
Preference: 1
```

## Interpreting the Dashboard

### Tool Usage Heatmap

**What to look for:**
- **Peak hours**: When are you most productive?
- **Tool clusters**: Which hours have the most tool diversity?
- **Gaps**: When do you take breaks or switch activities?

**Example interpretation:**
- Strong activity at 10h, 14h, 16h → Morning and afternoon work sessions
- Low activity at 12h-13h → Lunch break
- No activity 18h-8h → After-hours downtime

### Top Tools

**What to look for:**
- **Read dominance**: High Read usage suggests exploration/learning phase
- **Edit concentration**: High Edit usage indicates active development
- **Grep patterns**: Frequent Grep suggests debugging or code search

**Example interpretation:**
- 31% Read, 19% Edit → More exploration than implementation
- High Bash usage → System configuration or script-heavy work
- Low Write usage → Mostly modifying existing files, not creating new ones

### Instinct Registry

**What to look for:**
- **High confidence (70%+)**: Strong, reliable patterns
- **Medium confidence (50-69%)**: Emerging patterns, needs more evidence
- **Low confidence (<50%)**: Weak patterns, may be coincidental

**Example interpretation:**
- "read-before-edit" at 90% → Consistent behavior, good practice
- "prefer-grep-before-edit" at 70% → Strong pattern, should formalize
- "verify-after-change" at 60% → Emerging pattern, needs reinforcement

### Pattern Summary

**What to look for:**
- **Domain distribution**: Where are patterns concentrated?
- **Workflow patterns**: Task execution sequences
- **Preference patterns**: Tool and approach preferences
- **Error-handling patterns**: How you deal with failures

**Example interpretation:**
- 12 workflow patterns → Strong task execution consistency
- 8 preference patterns → Clear tool and approach preferences
- 3 error-handling patterns → Growing resilience patterns

## Sharing and Reporting

### Export for Sharing

```bash
# Generate dashboard with current date
DATE=$(date +%Y-%m-%d)
OUTPUT="insight-report-$DATE.html"

python3 scripts/dashboard.py -o "$OUTPUT"

# Share via email, Slack, etc.
echo "Dashboard ready: $OUTPUT"
```

### Compare Over Time

```bash
# Generate weekly reports
for week in 1 2 3 4; do
  python3 scripts/dashboard.py -o "reports/week-$week.html"
done

# Open all for comparison
open reports/week-*.html
```

## Troubleshooting Examples

### No Data Showing

**Problem**: Dashboard shows all zeros

**Solution**:
```bash
# Check if observations exist
ls -lh .caw/observations/observations.jsonl

# If file is empty or missing, observations aren't being recorded
# Check if hooks are running:
grep -r "PreToolUse\|PostToolUse" hooks/hooks.json
```

### Incorrect Statistics

**Problem**: Dashboard stats don't match expectations

**Solution**:
```bash
# Verify observation count
wc -l .caw/observations/observations.jsonl

# Verify instinct count
jq '.instincts | length' .caw/instincts/index.json

# Re-analyze observations
python3 scripts/instinct-cli.py analyze --full
```

### Dashboard Won't Open

**Problem**: `--open` flag doesn't work

**Solution**:
```bash
# Get the output path
OUTPUT=$(python3 scripts/dashboard.py)

# Manually open in browser
open "$OUTPUT"  # macOS
xdg-open "$OUTPUT"  # Linux
start "$OUTPUT"  # Windows
```

## Advanced Usage

### Multiple Projects

```bash
# Generate dashboard for each project
for project in project1 project2 project3; do
  cd "$project"
  python3 scripts/dashboard.py -o "../reports/$project-dashboard.html"
  cd ..
done
```

### Filtered Dashboards

```bash
# Generate dashboard for specific time period
# (requires custom script to filter observations.jsonl)

python3 scripts/filter-observations.py --since "2026-01-01" --until "2026-01-31"
python3 scripts/dashboard.py -o "january-report.html"
```

## See Also

- [Dashboard README](README.md) - Complete feature documentation
- [SKILL.md](SKILL.md) - Skill definition
- [instinct-cli.py](../insight-collector/scripts/instinct-cli.py) - CLI tool
- [dashboard.py](../insight-collector/scripts/dashboard.py) - Dashboard generator
