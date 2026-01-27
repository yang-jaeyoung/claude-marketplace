# Dashboard Skill

Interactive HTML visualization dashboard for insight-collector analytics.

## Overview

The dashboard skill generates a self-contained, offline-friendly HTML report that visualizes all insight-collector data including observations, instincts, and evolutions.

## Features

### 📊 Stats Overview
- **Total Observations**: Count of all recorded tool usage events
- **Total Instincts**: Number of learned behavioral patterns
- **Total Evolutions**: Count of commands/skills/agents evolved from instincts
- **Average Confidence**: Mean confidence score across all instincts

### 🔥 Tool Usage Heatmap
24-hour grid showing tool usage intensity by hour of day:
- **Visual**: Color-coded cells from dark (0 uses) to bright (30+ uses)
- **Interactive**: Hover over cells to see exact counts
- **Pattern Detection**: Quickly identify peak usage hours

### 🛠️ Top Tools Bar Chart
Ranked list of most frequently used tools:
- **Visual**: Gradient-filled percentage bars
- **Data**: Usage count and percentage for each tool
- **Limit**: Shows top 10 tools

### 📋 Instinct Registry Table
Complete list of all learned instincts:
- **Columns**: ID, Trigger, Confidence Bar, Percentage, Evidence Count, Domain
- **Sorting**: Pre-sorted by confidence (highest first)
- **Visual**: 10-dot confidence indicator bars

### 🚀 Evolution Timeline
Chronological history of component creation:
- **Types**: Commands, Skills, Agents
- **Layout**: Timeline view with dots and connecting lines
- **Limit**: Shows latest 20 evolutions

### 🧩 Pattern Summary
Breakdown of instincts by domain:
- **Categories**: workflow, preference, error-handling, general
- **Visual**: Grid layout with count per domain
- **Insight**: Quick overview of pattern distribution

## Usage

### Via instinct-cli (Recommended)

```bash
# Generate dashboard to default location (.caw/dashboard.html)
python3 skills/insight-collector/scripts/instinct-cli.py dashboard

# Generate and open in browser
python3 skills/insight-collector/scripts/instinct-cli.py dashboard --open

# Custom output path
python3 skills/insight-collector/scripts/instinct-cli.py dashboard -o /path/to/report.html
```

### Direct Script Execution

```bash
# Generate dashboard
python3 skills/insight-collector/scripts/dashboard.py

# Generate and open in browser
python3 skills/insight-collector/scripts/dashboard.py --open

# Custom output path
python3 skills/insight-collector/scripts/dashboard.py -o custom-report.html
```

## Output

The generated dashboard is a **single HTML file** with:
- ✅ Embedded CSS (no external stylesheets)
- ✅ No JavaScript dependencies
- ✅ Works completely offline
- ✅ Self-contained and portable
- ✅ Dark theme optimized for readability
- ✅ Responsive design

## Design System

### Color Palette

| Variable | Value | Usage |
|----------|-------|-------|
| `--bg-primary` | `#1a1a2e` | Main background |
| `--bg-secondary` | `#16213e` | Card backgrounds |
| `--accent` | `#e94560` | Headers, highlights |
| `--success` | `#4ecca3` | Positive indicators |
| `--text` | `#eaeaea` | Body text |

### Heatmap Color Scale

| Usage Count | Color | Hex Code | Meaning |
|-------------|-------|----------|---------|
| 0 | Dark | `#1a1a2e` | No activity |
| 1-5 | Medium Dark | `#16213e` | Low activity |
| 6-15 | Medium | `#0f3460` | Moderate activity |
| 16-30 | Accent | `#e94560` | High activity |
| 31+ | Success | `#4ecca3` | Very high activity |

## Data Sources

The dashboard reads from:

```
.caw/
├── observations/
│   └── observations.jsonl       # Tool usage events
├── instincts/
│   └── index.json               # Learned instincts registry
└── evolved/
    ├── commands/                # Evolved commands
    ├── skills/                  # Evolved skills
    └── agents/                  # Evolved agents
```

## Technical Details

### Implementation

- **Language**: Python 3
- **Dependencies**: Standard library only
- **Cross-platform**: macOS, Linux, Windows
- **File Size**: ~365 lines HTML (self-contained)

### Performance

- **Generation Time**: < 1 second for 1000+ observations
- **File Size**: ~50-100 KB (depending on data size)
- **Browser Compatibility**: All modern browsers
- **No Server Required**: Pure static HTML

## Empty State Handling

The dashboard gracefully handles missing or incomplete data:
- No observations → Shows "No observation data available"
- No instincts → Shows "No instincts generated yet"
- No evolutions → Shows "No evolutions yet"
- No patterns → Shows "No patterns detected yet"

## Examples

### Full Dashboard

When all data sources are available:
- 4 stat cards with metrics
- Heatmap with 24 hours of activity
- Top 10 tools bar chart
- Complete instinct table
- Timeline with recent evolutions
- Pattern summary grid

### Minimal Dashboard

With minimal data (e.g., just starting):
- Stats show zeros or low counts
- Heatmap is mostly empty (dark cells)
- Top tools shows only available tools
- Tables show available data
- Empty state messages where appropriate

## Integration

### With insight-collector

The dashboard automatically reads from insight-collector's data files and requires no configuration.

### With CAW Workflow

When used within context-aware-workflow, the dashboard respects the `.caw` directory structure and project context.

### Command Integration

Add to your workflow:

```bash
# After a work session
python3 scripts/instinct-cli.py analyze --incremental
python3 scripts/instinct-cli.py dashboard --open
```

## Boundaries

**Will:**
- Load and analyze all available data
- Generate visually appealing charts and graphs
- Handle missing or incomplete data gracefully
- Create fully self-contained HTML output
- Work completely offline
- Support all major browsers

**Will Not:**
- Modify any source data files
- Require external libraries or CDNs
- Use JavaScript (pure HTML/CSS)
- Connect to external services
- Require a web server
- Collect or transmit analytics

## Troubleshooting

### Dashboard shows all zeros
- Check that `.caw/observations/observations.jsonl` exists and has data
- Run `instinct-cli.py analyze` first to generate instincts

### Dashboard doesn't open in browser
- Verify the `--open` flag is used
- Check that `webbrowser` module is available (should be in standard library)
- Manually open the generated HTML file

### Missing sections
- Ensure all data directories exist in `.caw/`
- Run observation hooks to collect data
- Generate instincts with `analyze` command

## Future Enhancements

Potential improvements (not yet implemented):
- Confidence trend charts over time
- Session-based breakdown
- Tool sequence flow diagrams
- Export to PDF
- Dark/light theme toggle
- Interactive filtering

## See Also

- [insight-collector SKILL.md](../insight-collector/SKILL.md) - Main skill documentation
- [instinct-cli.py](../insight-collector/scripts/instinct-cli.py) - CLI tool
- [dashboard.py](../insight-collector/scripts/dashboard.py) - Dashboard generator script
