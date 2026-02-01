---
name: insight-collector
description: Hybrid learning system that captures insights and automatically learns behavioral patterns from tool usage. Combines manual insight blocks with automatic observation-based instinct generation.
allowed-tools: Read, Write, Glob, Bash
---

# Insight Collector

A hybrid learning system for capturing valuable insights and automatically learning behavioral patterns.

## System Overview

This skill operates in two modes:

1. **Manual Insight Capture**: When you generate an insight block (★ Insight), immediately save it
2. **Automatic Pattern Learning**: Background observation of tool usage to generate instincts

```
┌─────────────────────────────────────────────────────────────┐
│                    INSIGHT COLLECTOR                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐      │
│  │   Manual    │    │  Automatic  │    │  Evolution  │      │
│  │  Insights   │───▶│  Instincts  │───▶│  Commands/  │      │
│  │  (★ blocks) │    │ (patterns)  │    │   Skills    │      │
│  └─────────────┘    └─────────────┘    └─────────────┘      │
│        │                  │                   │              │
│        ▼                  ▼                   ▼              │
│  .caw/insights/    .caw/instincts/    .caw/evolved/         │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Part 1: Manual Insight Capture

### Core Principle

**Insight Generation = Immediate Save**

When you generate an insight, it must be saved in the same turn.

### Insight Generation Protocol

#### Step 1: Generate Insight Block

Display the insight to the user:

```
★ Insight ─────────────────────────────────────────
[2-3 key educational points]
───────────────────────────────────────────────────
```

#### Step 2: Immediately Save (Same Turn)

Immediately after outputting the insight block, save it using the Write tool:

```yaml
action: Write tool
path: .caw/insights/{date}-{slug}.md
content: |
  # Insight: [Title]

  ## Metadata
  | Field | Value |
  |-------|-------|
  | **Captured** | [timestamp] |
  | **Context** | [current task or topic] |

  ## Content

  [Original insight content]

  ## Tags

  [Auto-generated tags]
```

#### Step 3: Brief Confirmation

```
💡 Insight saved: [title]
```

### File Naming Convention

**Pattern**: `{YYYYMMDD}-{slug}.md`

- date: Today's date (e.g., 20260127)
- slug: 3-5 words from the title, kebab-case

**Examples**:
- `20260127-jwt-token-refresh-pattern.md`
- `20260127-react-state-management.md`

### When to Generate Insights

1. **Implementation Discovery**: Useful patterns discovered during implementation
2. **Problem Solution**: Lessons learned from the problem-solving process
3. **Best Practice**: Project-specific best practices
4. **Gotcha/Pitfall**: Traps or mistakes to watch out for
5. **Architecture Decision**: Rationale behind important design decisions

## Part 2: Automatic Pattern Learning (Instincts)

### Overview

The observation hook automatically tracks tool usage patterns and generates "instincts" - atomic behavioral rules learned from usage.

### How It Works

```
1. Tool Usage ──▶ 2. Observation ──▶ 3. Pattern Detection ──▶ 4. Instinct
   (any tool)       (hooks/observe.py)   (instinct-cli.py)       (.caw/instincts/)
```

### Detected Patterns

| Pattern Type | Example | Instinct Generated |
|--------------|---------|-------------------|
| **Tool Sequence** | Grep → Edit → Grep | "Verify with Grep after Edit" |
| **Error Recovery** | Edit fails → retry with changes | "Adjust parameters on retry" |
| **Tool Preference** | 80% use Grep over search | "Prefer Grep for code search" |
| **Workflow** | Same 3-tool sequence repeated | "Standard modification workflow" |

### Instinct Structure

```yaml
---
id: prefer-grep-before-edit
trigger: "when modifying code"
confidence: 0.7
domain: workflow
source: session-observation
evidence_count: 5
last_observed: 2026-01-27
---
# Action
Use Grep to find location before Edit.
```

### Confidence Scoring

| Evidence Count | Confidence |
|----------------|------------|
| 1-2 observations | 0.3 |
| 3-5 observations | 0.5 |
| 6-10 observations | 0.7 |
| 11+ observations | 0.9 (max) |

**Confidence changes:**
- Confirming observation: +0.05
- Contradicting observation: -0.10
- Weekly non-observation: -0.02 (decay)

### Managing Instincts

Use the CLI tool:

```bash
# Analyze observations and generate instincts
python3 scripts/instinct-cli.py analyze

# Incremental analysis (only new observations since last run)
python3 scripts/instinct-cli.py analyze --incremental

# Force full analysis (ignore last analyzed state)
python3 scripts/instinct-cli.py analyze --full

# List all instincts with confidence
python3 scripts/instinct-cli.py list

# Show specific instinct
python3 scripts/instinct-cli.py show <instinct-id>

# Manually adjust confidence
python3 scripts/instinct-cli.py promote <instinct-id>
python3 scripts/instinct-cli.py demote <instinct-id>

# Apply decay to unused instincts
python3 scripts/instinct-cli.py decay

# Statistics
python3 scripts/instinct-cli.py stats

# Export/Import for sharing
python3 scripts/instinct-cli.py export -o my-instincts.json
python3 scripts/instinct-cli.py import -i shared-instincts.json
```

### Incremental Analysis

For large observation files, incremental analysis provides significant performance improvements:

- **Marker File**: `.caw/observations/.last_analyzed` tracks analysis state
- **State Tracking**: Stores timestamp, line count, and file size
- **Memory Efficient**: Only loads new observations since last analysis
- **Automatic Updates**: Marker file updated after successful incremental analysis

**Usage Patterns:**

```bash
# First run - analyzes all observations
python3 scripts/instinct-cli.py analyze --incremental

# Subsequent runs - only analyzes new observations
python3 scripts/instinct-cli.py analyze --incremental

# Force full re-analysis when needed
python3 scripts/instinct-cli.py analyze --full
```

## Part 3: Evolution System

High-confidence instincts can evolve into reusable components:

| Evidence | Evolution Path |
|----------|---------------|
| Instinct confidence ≥ 0.6 | Eligible for evolution |
| User-triggered workflow (3+ steps) | → **Command** |
| Auto-applicable pattern | → **Skill** |
| Complex multi-step reasoning | → **Agent** |

Use `/cw:evolve` to:
- Preview evolution candidates
- Generate commands, skills, or agents from instincts
- Track evolution history

## Directory Structure

```
.caw/
├── insights/                    # Manual insights (Part 1)
│   ├── 20260127-jwt-refresh.md
│   └── 20260127-error-handling.md
├── instincts/                   # Automatic instincts (Part 2)
│   ├── index.json               # Instinct registry
│   └── personal/                # Learned instincts
│       ├── prefer-grep-before-edit.md
│       └── verify-after-change.md
├── observations/                # Raw observation data
│   ├── observations.jsonl       # Tool usage log
│   ├── .session_id              # Current session marker
│   └── .last_analyzed           # Incremental analysis state
└── evolved/                     # Evolved components (Part 3)
    ├── commands/
    ├── skills/
    └── agents/
```

## Integration

### With CAW Workflow

When workflow is active, insights include Phase/Step metadata:

```markdown
## Metadata
| Field | Value |
|-------|-------|
| **Phase** | Phase 2: Core Implementation |
| **Step** | 2.3: Token Refresh Logic |
```

### With Pattern Learner

Instincts feed into pattern-learner skill for higher-level analysis.

## Tag Generation Rules

Auto-generate tags by analyzing insight/instinct content:

| Content Pattern | Tag |
|-----------------|-----|
| auth, authentication, login, jwt | #authentication |
| security, vulnerability, xss, csrf | #security |
| performance, optimize, cache, speed | #performance |
| test, testing, coverage, mock | #testing |
| api, endpoint, rest, graphql | #api |
| database, query, sql, orm | #database |
| pattern, architecture, design | #architecture |
| error, exception, handling | #error-handling |

## Part 4: Analytics Dashboard

### Overview

Generate interactive HTML visualization dashboard for analyzing insight-collector data.

### Usage

```bash
# Generate dashboard
python3 scripts/instinct-cli.py dashboard

# Or directly
python3 scripts/dashboard.py

# Generate and open in browser
python3 scripts/dashboard.py --open

# Custom output path
python3 scripts/dashboard.py -o /path/to/report.html
```

### Dashboard Features

**Stats Overview:**
- Total observations recorded
- Total instincts learned
- Total evolved components
- Average confidence score

**Tool Usage Heatmap:**
- 24-hour grid showing tool usage intensity by hour
- Color-coded from dark (0 uses) to bright (30+ uses)

**Top Tools Bar Chart:**
- Top 10 most frequently used tools
- Percentage bars with usage counts

**Instinct Registry Table:**
- All instincts with ID, trigger, confidence bar, evidence count, domain
- Sortable and filterable

**Evolution Timeline:**
- Chronological history of component creation
- Commands, skills, and agents evolved from instincts

**Pattern Summary:**
- Breakdown by domain (workflow, preference, error-handling)
- Count per domain

### Output

Generated dashboard is a **self-contained HTML file** at `.caw/dashboard.html` (default):
- Embedded CSS styling (no external dependencies)
- Dark theme optimized for readability
- No JavaScript required
- Works completely offline

### Color Scheme

| Element | Color | Use |
|---------|-------|-----|
| Background | `#1a1a2e` / `#16213e` | Dark blue |
| Accent | `#e94560` | Red highlights |
| Success | `#4ecca3` | Green indicators |
| Text | `#eaeaea` | Light gray |

### Heatmap Intensity Colors

| Usage Count | Color | Hex |
|-------------|-------|-----|
| 0 uses | Dark | `#1a1a2e` |
| 1-5 uses | Medium dark | `#16213e` |
| 6-15 uses | Medium | `#0f3460` |
| 16-30 uses | Accent | `#e94560` |
| 31+ uses | Success | `#4ecca3` |

## Boundaries

**Will:**
- Save insights immediately upon generation
- Automatically observe tool usage patterns
- Generate instincts from patterns
- Auto-generate metadata and tags
- Preserve original content accurately
- Manage instincts based on confidence

**Will Not:**
- Arbitrarily modify insight/instinct content
- Overwrite existing files without user confirmation
- Auto-evolve low-confidence instincts
- Store sensitive information in observation logs
