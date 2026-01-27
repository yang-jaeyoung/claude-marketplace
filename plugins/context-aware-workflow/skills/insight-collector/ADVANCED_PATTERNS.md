# Advanced Pattern Detection - Statistical Analysis

This document describes the advanced statistical analysis methods added to instinct-cli.py.

## Overview

The advanced pattern detection module extends basic pattern detection with statistical methods to identify more nuanced behavioral patterns, outliers, and relationships in tool usage data.

## Features

### 1. TF-IDF Analysis (`calculate_tf_idf`)

**Purpose**: Identify distinctive tool usage patterns by calculating Term Frequency-Inverse Document Frequency scores for tool sequences.

**How it works**:
- TF (Term Frequency): How often a pattern occurs relative to total patterns
- IDF (Inverse Document Frequency): Logarithmic scaling based on pattern rarity
- Higher scores = more distinctive/important patterns

**Usage**:
```bash
python instinct-cli.py analyze --advanced
python instinct-cli.py insights
```

**Example output**:
```
Read → Edit → Write: 0.4521
Grep → Bash: 0.3012
```

### 2. Time-Window Workflow Detection (`detect_workflow_patterns`)

**Purpose**: Identify tool sequences that occur within specific time windows, capturing temporal relationships.

**Parameters**:
- `window_minutes`: Size of sliding time window (default: 30 minutes)

**How it works**:
- Groups observations by session
- Uses sliding time windows to find co-occurring tools
- Detects patterns that happen together in time, not just sequence

**Example pattern detected**:
```
Pattern: Grep → Edit → Grep (within 15 minutes)
Observed: 8 times across 5 sessions
```

### 3. Anomaly Detection (`detect_anomalies`)

**Purpose**: Flag unusually high or low tool usage using statistical Z-score analysis.

**Parameters**:
- `threshold_std`: Z-score threshold for anomaly detection (default: 2.0)

**How it works**:
- Calculates mean and standard deviation of tool usage
- Computes Z-score for each tool: `(count - mean) / std`
- Flags tools with |Z-score| > threshold

**Example output**:
```
HIGH USAGE ANOMALY:
  Edit: 150 uses (z-score: 3.2)
  Expected ~45 uses, actual usage 3.3x higher

LOW USAGE ANOMALY:
  Rare: 2 uses (z-score: -2.1)
  Rarely used tool
```

### 4. Statistical Confidence (`calculate_statistical_confidence`)

**Purpose**: Calculate confidence scores using Wilson score interval instead of simple thresholding.

**How it works**:
- Uses binomial proportion confidence interval
- Accounts for sample size and pattern frequency
- More accurate than simple evidence counting for small samples

**Formula**:
```
Wilson Score = (p + z²/2n ± z√(p(1-p)/n + z²/4n²)) / (1 + z²/n)
where:
  p = pattern frequency
  n = total observations
  z = 1.96 (95% confidence)
```

**Usage in analyze**:
- Activated with `--advanced` flag
- Only used when total observations > 20
- Falls back to simple confidence if score too low

### 5. Pattern Clustering (`cluster_similar_patterns`)

**Purpose**: Group similar tool usage patterns using Jaccard similarity.

**Parameters**:
- `similarity_threshold`: Minimum similarity to cluster (0.0-1.0, default: 0.7)

**How it works**:
- Jaccard similarity: `|A ∩ B| / |A ∪ B|`
- Greedy clustering algorithm
- Groups patterns that share common tools

**Example output**:
```
Cluster 1 (3 patterns):
  - Read → Edit → Write
  - Read → Edit → Grep
  - Read → Write

Cluster 2 (2 patterns):
  - Bash → Test → Deploy
  - Bash → Deploy
```

## Commands

### analyze --advanced (-a)

Enables advanced pattern detection during analysis:

```bash
# Standard analysis
python instinct-cli.py analyze

# Advanced analysis
python instinct-cli.py analyze --advanced

# Incremental + advanced
python instinct-cli.py analyze -i -a
```

**What it adds**:
- Time-window workflow detection
- Anomaly detection
- TF-IDF scoring for sequences
- Statistical confidence calculation (when sufficient data)

### insights

Show advanced statistical insights:

```bash
python instinct-cli.py insights
```

**Sections displayed**:
1. **TF-IDF Analysis**: Most distinctive patterns
2. **Anomaly Detection**: Unusual usage patterns
3. **Time-Window Workflows**: Temporal patterns
4. **Pattern Clustering**: Grouped similar patterns
5. **Statistical Confidence**: Confidence intervals for top tools

**Example output**:
```
==============================================================
ADVANCED PATTERN INSIGHTS
==============================================================

--- TF-IDF Analysis (Most Distinctive Patterns) ---
  Read → Edit → Write: 0.4521
  Grep → Bash: 0.3012
  Edit → Grep → Edit: 0.2843

--- Anomaly Detection (Unusual Usage Patterns) ---
  [anomaly-high-usage] when using Edit
    Unusually high usage detected (150 times, z-score: 3.24)

--- Time-Window Workflow Patterns (30-min windows) ---
  Typical sequence: Grep → Read → Edit (observed 12 times)

--- Pattern Clustering (Similar Workflows) ---
  Cluster 1 (3 patterns):
    - Read → Edit
    - Read → Write
    - Edit → Write

--- Statistical Confidence (Wilson Score) ---
  Edit: 150 uses, frequency=0.35, confidence=0.334
  Read: 120 uses, frequency=0.28, confidence=0.272
```

## Implementation Details

### Dependencies

All implementations use **Python standard library only**:
- `math` - Mathematical functions (log, sqrt)
- `collections.Counter` - Frequency counting
- `datetime.timedelta` - Time-window calculations

### Performance

- **TF-IDF**: O(n) where n = number of unique sequences
- **Time-window**: O(n²) per session (sliding window)
- **Anomalies**: O(n) single pass for mean/std, O(n) for Z-scores
- **Clustering**: O(n²) greedy algorithm
- **Statistical confidence**: O(1) per pattern

### Testing

17 tests added in `TestAdvancedPatternDetection`:
- TF-IDF calculation and distinctiveness
- Time-window pattern detection
- Anomaly detection (high/low usage)
- Statistical confidence bounds and Wilson score
- Pattern clustering with Jaccard similarity
- Command integration (`analyze --advanced`, `insights`)

All tests pass: `pytest tests/test_insight_collector.py::TestAdvancedPatternDetection -v`

## When to Use

### Use --advanced when:
- You have sufficient observation data (>100 observations)
- You want to identify subtle patterns beyond simple frequency
- You need statistical confidence measures
- You want to detect outliers/anomalies

### Use insights when:
- You want an overview of pattern quality
- You need to identify distinctive vs. common patterns
- You want to see temporal relationships
- You want to cluster related patterns

### Use standard analysis when:
- You have limited data (<50 observations)
- You only need basic pattern detection
- Performance is critical
- You want simple confidence scores

## Future Enhancements

Potential additions (using only stdlib):
- Markov chain transition probabilities
- Sequential pattern mining (PrefixSpan-like)
- Confidence interval visualization (ASCII charts)
- Correlation analysis between tool pairs
- Session-level clustering
