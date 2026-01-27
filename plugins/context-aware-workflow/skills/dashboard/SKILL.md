---
name: dashboard
description: Generate interactive HTML dashboard for insight-collector analytics
allowed-tools: Read, Write, Bash
---

# Dashboard Skill

Generate a standalone HTML visualization dashboard for insight-collector analytics.

## Usage

```bash
# Generate dashboard
python3 "${CLAUDE_PLUGIN_ROOT}/skills/insight-collector/scripts/dashboard.py"

# Generate and open in browser
python3 "${CLAUDE_PLUGIN_ROOT}/skills/insight-collector/scripts/dashboard.py" --open

# Custom output path
python3 "${CLAUDE_PLUGIN_ROOT}/skills/insight-collector/scripts/dashboard.py" -o /path/to/report.html
```

## Features

- **Stats Overview**: Total observations, instincts, evolutions, average confidence
- **Tool Usage Heatmap**: 24-hour grid showing tool usage intensity
- **Top Tools Bar Chart**: Most frequently used tools with percentages
- **Instinct Registry Table**: All instincts with confidence bars and evidence counts
- **Evolution Timeline**: Chronological history of component creation
- **Pattern Summary**: Breakdown by domain (workflow, preference, error-handling)

## Output

Generates self-contained HTML file at `.caw/dashboard.html` (default) with:
- Embedded CSS styling (no external dependencies)
- Dark theme optimized for readability
- No JavaScript required
- Works completely offline

## Color Scheme

- Background: Dark blue (#1a1a2e, #16213e)
- Accent: Red (#e94560)
- Success: Green (#4ecca3)
- Text: Light gray (#eaeaea)

## Boundaries

**Will:**
- Load and analyze all observations and instincts
- Generate visual statistics and trends
- Create fully self-contained HTML
- Handle missing or incomplete data gracefully

**Will Not:**
- Modify any source data files
- Require external libraries or dependencies
- Execute JavaScript (pure HTML/CSS only)
- Connect to external services
