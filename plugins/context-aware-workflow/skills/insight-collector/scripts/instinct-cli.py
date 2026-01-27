#!/usr/bin/env python3
"""
Instinct CLI - Manage learned instincts from observations

Commands:
    analyze     - Analyze observations and generate instinct candidates
    list        - List all instincts with confidence scores
    show        - Show details of a specific instinct
    promote     - Manually increase confidence of an instinct
    demote      - Manually decrease confidence of an instinct
    delete      - Delete an instinct
    export      - Export instincts for sharing
    import      - Import instincts from file
    decay       - Apply confidence decay to unused instincts
    stats       - Show observation and instinct statistics
    insights    - Show advanced statistical insights
    dashboard   - Generate HTML analytics dashboard
    diff        - Compare local instincts with another file
    merge       - Merge instincts from another file with conflict resolution

Cross-platform compatible (macOS, Linux, Windows).
"""

import argparse
import hashlib
import json
import logging
import math
import os
import re
import sys
import tempfile
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, Generator, List, Optional, Tuple

# Import common utilities
try:
    from lib.common import get_project_dir, get_caw_dir, ensure_dir
except ImportError:
    # Fallback for standalone usage
    def get_project_dir() -> Path:
        return Path(os.environ.get('CLAUDE_PROJECT_DIR', os.getcwd()))

    def get_caw_dir() -> Path:
        return get_project_dir() / '.caw'

    def ensure_dir(path: Path) -> Path:
        path.mkdir(parents=True, exist_ok=True)
        return path

# Type definitions (optional - for IDE support)
try:
    from lib.types import Observation, Instinct, InstinctSummary, InstinctIndex, PatternCandidate
except ImportError:
    # Fallback for standalone CLI usage
    pass

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

# Confidence calculation constants
MIN_CONFIDENCE = 0.1
MAX_CONFIDENCE = 0.95
LOW_EVIDENCE_THRESHOLD = 2
LOW_EVIDENCE_CONFIDENCE = 0.3
MEDIUM_EVIDENCE_THRESHOLD = 5
MEDIUM_EVIDENCE_CONFIDENCE = 0.5
HIGH_EVIDENCE_THRESHOLD = 10
HIGH_EVIDENCE_CONFIDENCE = 0.7
CONFIDENCE_INCREMENT = 0.02
WEEKLY_DECAY_RATE = 0.02

# Pattern detection thresholds
MIN_SEQUENCE_OCCURRENCES = 3
MIN_ERROR_RECOVERY_OCCURRENCES = 2
MIN_TOOL_PREFERENCE_COUNT = 5
TOOL_PREFERENCE_RATIO = 0.1


def get_instincts_dir() -> Path:
    """Get instincts directory."""
    return get_caw_dir() / 'instincts' / 'personal'


def get_instincts_index_file() -> Path:
    """Get instincts index file path."""
    return get_caw_dir() / 'instincts' / 'index.json'


def get_observations_file() -> Path:
    """Get observations JSONL file path."""
    return get_caw_dir() / 'observations' / 'observations.jsonl'


def get_last_analyzed_marker_file() -> Path:
    """Get last analyzed state marker file path."""
    return get_caw_dir() / 'observations' / '.last_analyzed'


def ensure_instincts_dir() -> Path:
    """Ensure instincts directory exists."""
    return ensure_dir(get_instincts_dir())


def get_last_analyzed_state() -> Dict[str, Any]:
    """Read last analyzed state from marker file.

    Returns:
        Dict with 'timestamp', 'line_count', 'file_size', or empty dict if not found
    """
    marker_file = get_last_analyzed_marker_file()
    if not marker_file.exists():
        return {}

    try:
        with open(marker_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}


def save_analyzed_state(line_count: int, file_size: int) -> None:
    """Save analysis state to marker file.

    Args:
        line_count: Number of lines analyzed
        file_size: File size at time of analysis
    """
    marker_file = get_last_analyzed_marker_file()
    marker_file.parent.mkdir(parents=True, exist_ok=True)

    state = {
        'timestamp': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
        'line_count': line_count,
        'file_size': file_size
    }

    try:
        with tempfile.NamedTemporaryFile(
            mode='w',
            encoding='utf-8',
            dir=marker_file.parent,
            delete=False,
            suffix='.tmp'
        ) as tmp_file:
            json.dump(state, tmp_file, indent=2)
            tmp_path = tmp_file.name

        # Atomic replace
        os.replace(tmp_path, marker_file)
    except (IOError, OSError) as e:
        logger.error(f"Failed to save analyzed state: {e}")


def load_new_observations() -> List[Dict[str, Any]]:
    """Load only observations added since last analysis.

    Returns:
        List of new observations, or empty list if none found
    """
    obs_file = get_observations_file()
    if not obs_file.exists():
        return []

    last_state = get_last_analyzed_state()
    last_line_count = last_state.get('line_count', 0)

    # Load observations starting from last analyzed line
    new_observations = list(load_observations(since_line=last_line_count))

    return new_observations


def load_observations(
    since_line: int = 0,
    chunk_size: int = 1000
) -> Generator[Dict[str, Any], None, None]:
    """Stream observations from JSONL file.

    Args:
        since_line: Start from this line number (0-indexed)
        chunk_size: Yield observations in chunks (not currently used, but available for batching)

    Yields:
        Individual observation dicts
    """
    obs_file = get_observations_file()
    if not obs_file.exists():
        return

    try:
        with open(obs_file, 'r', encoding='utf-8') as f:
            # Skip to starting line
            for _ in range(since_line):
                next(f, None)

            # Yield remaining observations
            for line in f:
                line = line.strip()
                if line:
                    try:
                        yield json.loads(line)
                    except json.JSONDecodeError:
                        continue
    except IOError:
        return


def load_instincts_index() -> Dict[str, Any]:
    """Load instincts index."""
    index_file = get_instincts_index_file()
    if not index_file.exists():
        return {'instincts': [], 'last_updated': None}

    try:
        with open(index_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {'instincts': [], 'last_updated': None}


def save_instincts_index(index: Dict[str, Any]) -> bool:
    """Save instincts index atomically using tempfile + os.replace pattern."""
    index_file = get_instincts_index_file()
    index_file.parent.mkdir(parents=True, exist_ok=True)

    try:
        index['last_updated'] = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

        # Atomic write: write to temp file, then replace
        with tempfile.NamedTemporaryFile(
            mode='w',
            encoding='utf-8',
            dir=index_file.parent,
            delete=False,
            suffix='.tmp'
        ) as tmp_file:
            json.dump(index, tmp_file, indent=2)
            tmp_path = tmp_file.name

        # Atomic replace
        os.replace(tmp_path, index_file)
        return True
    except (IOError, OSError) as e:
        logger.error(f"Failed to save instincts index: {e}")
        return False


def generate_instinct_id(trigger: str) -> str:
    """Generate a unique ID for an instinct."""
    # Create a slug from the trigger
    slug = re.sub(r'[^a-z0-9]+', '-', trigger.lower())[:40]
    # Add hash for uniqueness
    hash_suffix = hashlib.sha256(trigger.encode()).hexdigest()[:8]
    return f"{slug}-{hash_suffix}"


def calculate_confidence(evidence_count: int) -> float:
    """Calculate confidence score based on evidence count."""
    if evidence_count <= LOW_EVIDENCE_THRESHOLD:
        return LOW_EVIDENCE_CONFIDENCE
    elif evidence_count <= MEDIUM_EVIDENCE_THRESHOLD:
        return MEDIUM_EVIDENCE_CONFIDENCE
    elif evidence_count <= HIGH_EVIDENCE_THRESHOLD:
        return HIGH_EVIDENCE_CONFIDENCE
    else:
        return min(
            MAX_CONFIDENCE,
            HIGH_EVIDENCE_CONFIDENCE + (evidence_count - HIGH_EVIDENCE_THRESHOLD) * CONFIDENCE_INCREMENT
        )


def create_instinct_file(instinct: Dict[str, Any]) -> bool:
    """Create an instinct markdown file."""
    ensure_instincts_dir()
    instinct_file = get_instincts_dir() / f"{instinct['id']}.md"

    content = f"""---
id: {instinct['id']}
trigger: "{instinct['trigger']}"
confidence: {instinct['confidence']}
domain: {instinct.get('domain', 'workflow')}
source: {instinct.get('source', 'session-observation')}
evidence_count: {instinct.get('evidence_count', 1)}
last_observed: {instinct.get('last_observed', datetime.now(timezone.utc).strftime('%Y-%m-%d'))}
created_at: {instinct.get('created_at', datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'))}
---

# {instinct.get('title', instinct['trigger'].title())}

## Trigger

{instinct['trigger']}

## Action

{instinct.get('action', 'No action specified.')}

## Evidence

- Observed {instinct.get('evidence_count', 1)} times
- Last observed: {instinct.get('last_observed', 'N/A')}
- Source: {instinct.get('source', 'session-observation')}

## Notes

{instinct.get('notes', 'Auto-generated from behavior observation.')}
"""

    try:
        with open(instinct_file, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    except IOError:
        return False


def validate_instinct_id(instinct_id: str) -> bool:
    """Validate instinct ID to prevent path traversal attacks."""
    # Instinct IDs must match pattern: lowercase letters, numbers, and hyphens only
    return bool(re.match(r'^[a-z0-9\-]+$', instinct_id))


def load_instinct(instinct_id: str) -> Optional[Dict[str, Any]]:
    """Load an instinct by ID."""
    if not validate_instinct_id(instinct_id):
        return None

    instinct_file = get_instincts_dir() / f"{instinct_id}.md"
    if not instinct_file.exists():
        return None

    try:
        content = instinct_file.read_text(encoding='utf-8')

        # Parse YAML frontmatter
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                frontmatter = parts[1].strip()
                body = parts[2].strip()

                instinct = {}
                for line in frontmatter.split('\n'):
                    if ':' in line:
                        key, value = line.split(':', 1)
                        key = key.strip()
                        value = value.strip().strip('"')
                        if key in ('confidence', 'evidence_count'):
                            try:
                                value = float(value) if '.' in value else int(value)
                            except ValueError:
                                pass
                        instinct[key] = value

                instinct['body'] = body
                return instinct

    except IOError:
        pass

    return None


# =============================================================================
# Pattern Detection
# =============================================================================

def detect_tool_sequences(observations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Detect repeated tool sequences (workflow patterns)."""
    # Group observations by session
    sessions = defaultdict(list)
    for obs in observations:
        if obs.get('event_type') == 'pre':  # Only pre events for sequence
            sessions[obs.get('session_id', 'unknown')].append(obs)

    # Find sequences of 2-4 tools
    sequence_counts = Counter()

    for session_id, session_obs in sessions.items():
        tools = [o.get('tool_name', '') for o in session_obs]

        for seq_len in range(2, 5):
            for i in range(len(tools) - seq_len + 1):
                seq = tuple(tools[i:i + seq_len])
                if len(set(seq)) > 1:  # At least 2 different tools
                    sequence_counts[seq] += 1

    # Convert to instinct candidates
    candidates = []
    for seq, count in sequence_counts.most_common(20):
        if count >= MIN_SEQUENCE_OCCURRENCES:
            candidates.append({
                'type': 'workflow',
                'trigger': f"when performing {seq[0]}",
                'action': f"Follow with: {' → '.join(seq[1:])}",
                'evidence_count': count,
                'domain': 'workflow',
                'pattern': seq,
            })

    return candidates


def detect_error_recovery(observations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Detect error → fix patterns."""
    candidates = []

    # Group by session
    sessions = defaultdict(list)
    for obs in observations:
        sessions[obs.get('session_id', 'unknown')].append(obs)

    error_fix_counts = Counter()

    for session_id, session_obs in sessions.items():
        # Look for failed tool → same tool success pattern
        for i, obs in enumerate(session_obs):
            if obs.get('event_type') == 'post' and obs.get('success') is False:
                tool = obs.get('tool_name')
                # Look for successful retry
                for j in range(i + 1, min(i + 5, len(session_obs))):
                    next_obs = session_obs[j]
                    if (next_obs.get('event_type') == 'post' and
                            next_obs.get('tool_name') == tool and
                            next_obs.get('success') is True):
                        error_fix_counts[tool] += 1
                        break

    for tool, count in error_fix_counts.most_common(10):
        if count >= MIN_ERROR_RECOVERY_OCCURRENCES:
            candidates.append({
                'type': 'error-recovery',
                'trigger': f"when {tool} fails",
                'action': f"Retry {tool} with adjusted parameters",
                'evidence_count': count,
                'domain': 'error-handling',
            })

    return candidates


def detect_tool_preferences(observations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Detect tool usage preferences.

    Note: Works with lists for simplicity. Could be optimized to use Counter
    with streaming, but tool preferences need total count for percentage calculation.
    """
    tool_counts = Counter()

    for obs in observations:
        if obs.get('event_type') == 'pre':
            tool_counts[obs.get('tool_name', '')] += 1

    candidates = []
    total = sum(tool_counts.values())

    for tool, count in tool_counts.most_common(10):
        if count >= MIN_TOOL_PREFERENCE_COUNT and count / total > TOOL_PREFERENCE_RATIO:
            candidates.append({
                'type': 'preference',
                'trigger': f"when choosing tools",
                'action': f"Prefer using {tool} ({count} uses, {count / total * 100:.1f}%)",
                'evidence_count': count,
                'domain': 'preference',
            })

    return candidates


def detect_user_corrections(observations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Detect patterns where user corrected Claude's work.

    Analyzes Edit/Write tool outputs to find:
    1. Same file edited multiple times in quick succession
    2. Patterns suggesting the user corrected or refined Claude's changes
    """
    candidates = []

    # Filter to only Edit/Write post events with success
    edit_ops = [
        obs for obs in observations
        if obs.get('event_type') == 'post'
        and obs.get('tool_name') in ('Edit', 'Write')
        and obs.get('success') is True
    ]

    if len(edit_ops) < 2:
        return candidates

    # Group by file path
    file_edits = defaultdict(list)

    for obs in edit_ops:
        tool_input = obs.get('tool_input', {})
        file_path = tool_input.get('file_path', tool_input.get('path', ''))
        if file_path:
            file_edits[file_path].append(obs)

    # Analyze each file for correction patterns
    correction_counts = Counter()

    for file_path, edits in file_edits.items():
        if len(edits) < 2:
            continue

        # Sort by timestamp
        edits = sorted(edits, key=lambda x: x.get('timestamp', ''))

        # Look for rapid re-edits (within 5 minutes)
        for i in range(len(edits) - 1):
            curr = edits[i]
            next_edit = edits[i + 1]

            try:
                curr_time = datetime.fromisoformat(curr.get('timestamp', '').replace('Z', '+00:00'))
                next_time = datetime.fromisoformat(next_edit.get('timestamp', '').replace('Z', '+00:00'))

                time_diff = (next_time - curr_time).total_seconds()

                # If same file edited within 5 minutes, likely a correction
                if 0 < time_diff < 300:  # 5 minutes
                    # Extract file extension for pattern
                    ext = Path(file_path).suffix or 'unknown'
                    correction_counts[ext] += 1
            except (ValueError, TypeError):
                continue

    # Generate candidates for frequently corrected file types
    for ext, count in correction_counts.most_common(10):
        if count >= 2:  # At least 2 corrections
            candidates.append({
                'type': 'user-correction',
                'trigger': f"when editing {ext} files",
                'action': f"Review changes carefully - {ext} files were corrected {count} times",
                'evidence_count': count,
                'domain': 'user-correction',
            })

    # Also detect specific file patterns
    file_correction_counts = Counter()
    for file_path, edits in file_edits.items():
        rapid_edits = 0
        edits = sorted(edits, key=lambda x: x.get('timestamp', ''))
        for i in range(len(edits) - 1):
            try:
                curr_time = datetime.fromisoformat(edits[i].get('timestamp', '').replace('Z', '+00:00'))
                next_time = datetime.fromisoformat(edits[i + 1].get('timestamp', '').replace('Z', '+00:00'))
                if 0 < (next_time - curr_time).total_seconds() < 300:
                    rapid_edits += 1
            except (ValueError, TypeError):
                continue

        if rapid_edits >= 2:
            # Extract meaningful path component (last 2 parts)
            parts = Path(file_path).parts
            pattern = '/'.join(parts[-2:]) if len(parts) >= 2 else parts[-1] if parts else file_path
            file_correction_counts[pattern] += rapid_edits

    for pattern, count in file_correction_counts.most_common(5):
        if count >= 3:
            candidates.append({
                'type': 'user-correction',
                'trigger': f"when modifying {pattern}",
                'action': f"Take extra care - this file required {count} corrections",
                'evidence_count': count,
                'domain': 'user-correction',
            })

    return candidates


# =============================================================================
# Advanced Pattern Detection (Statistical Analysis)
# =============================================================================

def calculate_tf_idf(tool_sequences: List[Tuple[str, ...]], min_doc_freq: int = 2) -> Dict[Tuple[str, ...], float]:
    """Calculate TF-IDF scores for tool sequences.

    Higher scores indicate more distinctive patterns.

    Args:
        tool_sequences: List of tool sequence tuples
        min_doc_freq: Minimum document frequency to include

    Returns:
        Dict mapping sequences to TF-IDF scores
    """
    # Document frequency
    doc_count = len(tool_sequences)
    if doc_count == 0:
        return {}

    df = Counter()
    tf = Counter(tool_sequences)

    for seq in set(tool_sequences):
        df[seq] = sum(1 for s in tool_sequences if seq == s)

    # TF-IDF calculation
    tfidf = {}
    for seq, freq in tf.items():
        if df[seq] >= min_doc_freq:
            tf_score = freq / len(tool_sequences)
            idf_score = math.log(doc_count / df[seq]) + 1
            tfidf[seq] = tf_score * idf_score

    return tfidf


def detect_workflow_patterns(observations: List[Dict[str, Any]],
                            window_minutes: int = 30) -> List[Dict[str, Any]]:
    """Detect workflow patterns using time-window analysis.

    Groups tool usage into time windows and finds repeated patterns.

    Args:
        observations: List of observation dicts
        window_minutes: Time window size in minutes

    Returns:
        List of workflow pattern candidates
    """
    candidates = []

    # Group by session and sort by time
    sessions = defaultdict(list)
    for obs in observations:
        if obs.get('event_type') == 'pre':
            try:
                timestamp = datetime.fromisoformat(obs.get('timestamp', '').replace('Z', '+00:00'))
                sessions[obs.get('session_id', 'unknown')].append({
                    'tool': obs.get('tool_name', ''),
                    'timestamp': timestamp
                })
            except (ValueError, TypeError):
                continue

    # Analyze time windows in each session
    window_patterns = Counter()

    for session_id, session_obs in sessions.items():
        session_obs = sorted(session_obs, key=lambda x: x['timestamp'])

        # Sliding window
        for i in range(len(session_obs)):
            window_start = session_obs[i]['timestamp']
            window_end = window_start + timedelta(minutes=window_minutes)

            window_tools = []
            for j in range(i, len(session_obs)):
                if session_obs[j]['timestamp'] <= window_end:
                    window_tools.append(session_obs[j]['tool'])
                else:
                    break

            if len(window_tools) >= 2:
                pattern = tuple(window_tools)
                window_patterns[pattern] += 1

    # Convert to candidates
    for pattern, count in window_patterns.most_common(15):
        if count >= 2 and len(pattern) >= 2:
            candidates.append({
                'type': 'time-window-workflow',
                'trigger': f"within {window_minutes}-min workflow",
                'action': f"Typical sequence: {' → '.join(pattern)}",
                'evidence_count': count,
                'domain': 'time-based-workflow',
                'pattern': pattern,
            })

    return candidates


def detect_anomalies(observations: List[Dict[str, Any]],
                    threshold_std: float = 2.0) -> List[Dict[str, Any]]:
    """Detect unusual tool usage patterns using Z-score.

    Flags patterns that deviate significantly from normal usage.

    Args:
        observations: List of observation dicts
        threshold_std: Z-score threshold for anomaly detection

    Returns:
        List of anomaly pattern candidates
    """
    candidates = []

    # Count tool frequencies
    tool_counts = Counter()
    for obs in observations:
        if obs.get('event_type') == 'pre':
            tool_counts[obs.get('tool_name', '')] += 1

    if len(tool_counts) < 2:
        return candidates

    # Calculate mean and std
    counts = list(tool_counts.values())
    mean = sum(counts) / len(counts)
    variance = sum((x - mean) ** 2 for x in counts) / len(counts)
    std = math.sqrt(variance)

    if std == 0:
        return candidates

    # Find anomalies
    for tool, count in tool_counts.items():
        z_score = (count - mean) / std

        if abs(z_score) > threshold_std:
            if z_score > 0:
                candidates.append({
                    'type': 'anomaly-high-usage',
                    'trigger': f"when using {tool}",
                    'action': f"Unusually high usage detected ({count} times, z-score: {z_score:.2f})",
                    'evidence_count': count,
                    'domain': 'anomaly',
                })
            else:
                candidates.append({
                    'type': 'anomaly-low-usage',
                    'trigger': f"when considering {tool}",
                    'action': f"Rarely used ({count} times, z-score: {z_score:.2f})",
                    'evidence_count': count,
                    'domain': 'anomaly',
                })

    return candidates


def calculate_statistical_confidence(evidence_count: int,
                                    total_observations: int,
                                    pattern_frequency: float) -> float:
    """Calculate confidence using statistical significance.

    Uses Wilson score interval for binomial proportion confidence.

    Args:
        evidence_count: Number of times pattern observed
        total_observations: Total observation count
        pattern_frequency: Frequency of pattern (0.0-1.0)

    Returns:
        Confidence score (0.0-1.0)
    """
    if total_observations == 0:
        return 0.0

    p = pattern_frequency
    n = total_observations
    z = 1.96  # 95% confidence

    denominator = 1 + z**2 / n
    centre = p + z**2 / (2 * n)
    spread = z * math.sqrt((p * (1 - p) + z**2 / (4 * n)) / n)

    lower_bound = (centre - spread) / denominator
    return max(0.0, min(1.0, lower_bound))


def cluster_similar_patterns(patterns: List[Dict[str, Any]],
                            similarity_threshold: float = 0.7) -> List[List[Dict[str, Any]]]:
    """Cluster similar patterns using Jaccard similarity.

    Groups patterns that share common tool sequences.

    Args:
        patterns: List of pattern dicts
        similarity_threshold: Minimum similarity to cluster (0.0-1.0)

    Returns:
        List of pattern clusters
    """
    def jaccard_similarity(seq1: Tuple, seq2: Tuple) -> float:
        set1, set2 = set(seq1), set(seq2)
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        return intersection / union if union > 0 else 0.0

    # Simple greedy clustering
    clusters = []
    used = set()

    for i, p1 in enumerate(patterns):
        if i in used:
            continue
        cluster = [p1]
        used.add(i)

        pattern1 = p1.get('pattern', ())

        for j, p2 in enumerate(patterns):
            if j in used:
                continue
            pattern2 = p2.get('pattern', ())
            if jaccard_similarity(pattern1, pattern2) >= similarity_threshold:
                cluster.append(p2)
                used.add(j)

        clusters.append(cluster)

    return clusters


# =============================================================================
# Commands
# =============================================================================

def cmd_analyze(args):
    """Analyze observations and generate instinct candidates."""
    # Handle incremental mode
    if args.incremental and not args.full:
        observations = load_new_observations()
        if not observations:
            logger.info("No new observations since last analysis.")
            return 0
        logger.info(f"Analyzing {len(observations)} new observations (incremental mode)...\n")
    else:
        # Full analysis mode
        observations = list(load_observations())
        if not observations:
            logger.info("No observations found. Run some tool operations first.")
            return 1
        logger.info(f"Analyzing {len(observations)} observations (full mode)...\n")

    candidates = []

    # Detect patterns
    logger.info("Detecting tool sequences...")
    candidates.extend(detect_tool_sequences(observations))

    logger.info("Detecting error recovery patterns...")
    candidates.extend(detect_error_recovery(observations))

    logger.info("Detecting tool preferences...")
    candidates.extend(detect_tool_preferences(observations))

    logger.info("Detecting user correction patterns...")
    candidates.extend(detect_user_corrections(observations))

    # Advanced analysis if requested
    if args.advanced:
        logger.info("Running advanced pattern detection...")

        logger.info("  - Workflow patterns (time-window analysis)...")
        candidates.extend(detect_workflow_patterns(observations))

        logger.info("  - Anomaly detection...")
        candidates.extend(detect_anomalies(observations))

        # Apply TF-IDF scoring to existing sequences
        logger.info("  - Calculating TF-IDF scores...")
        sequences = []
        for c in candidates:
            if 'pattern' in c and isinstance(c['pattern'], tuple):
                sequences.append(c['pattern'])

        if sequences:
            tfidf_scores = calculate_tf_idf(sequences)
            for c in candidates:
                if 'pattern' in c and c['pattern'] in tfidf_scores:
                    c['tfidf_score'] = tfidf_scores[c['pattern']]

    if not candidates:
        logger.info("\nNo patterns detected yet. Continue working to build observation history.")
        return 0

    logger.info(f"\n{'=' * 60}")
    logger.info(f"Found {len(candidates)} instinct candidates")
    logger.info(f"{'=' * 60}\n")

    # Load existing index
    index = load_instincts_index()
    existing_ids = {i['id'] for i in index.get('instincts', [])}

    created = 0
    updated = 0

    for candidate in candidates:
        instinct_id = generate_instinct_id(candidate['trigger'])

        # Calculate confidence (use statistical if advanced mode and sufficient data)
        if args.advanced and len(observations) > 20:
            pattern_freq = candidate['evidence_count'] / len(observations)
            confidence = calculate_statistical_confidence(
                candidate['evidence_count'],
                len(observations),
                pattern_freq
            )
            # Fallback to simple calculation if statistical gives too low value
            if confidence < 0.2:
                confidence = calculate_confidence(candidate['evidence_count'])
        else:
            confidence = calculate_confidence(candidate['evidence_count'])

        instinct = {
            'id': instinct_id,
            'trigger': candidate['trigger'],
            'action': candidate['action'],
            'confidence': confidence,
            'evidence_count': candidate['evidence_count'],
            'domain': candidate.get('domain', 'workflow'),
            'source': 'session-observation',
            'last_observed': datetime.now(timezone.utc).strftime('%Y-%m-%d'),
            'created_at': datetime.now(timezone.utc).isoformat() + 'Z',
        }

        if instinct_id in existing_ids:
            # Update existing
            for i, existing in enumerate(index['instincts']):
                if existing['id'] == instinct_id:
                    existing['evidence_count'] = max(
                        existing.get('evidence_count', 0),
                        candidate['evidence_count']
                    )
                    existing['confidence'] = calculate_confidence(existing['evidence_count'])
                    existing['last_observed'] = datetime.now(timezone.utc).strftime('%Y-%m-%d')
                    index['instincts'][i] = existing
                    instinct = existing
                    updated += 1
                    break
        else:
            # Create new
            index['instincts'].append({
                'id': instinct_id,
                'trigger': instinct['trigger'],
                'confidence': instinct['confidence'],
                'evidence_count': instinct['evidence_count'],
                'domain': instinct['domain'],
            })
            created += 1

        # Create/update file
        create_instinct_file(instinct)

        status = "UPDATED" if instinct_id in existing_ids else "NEW"
        conf_bar = '█' * int(instinct['confidence'] * 10) + '░' * (10 - int(instinct['confidence'] * 10))
        logger.info(f"[{status}] {instinct_id}")
        logger.info(f"  Trigger: {instinct['trigger']}")
        logger.info(f"  Action: {instinct['action'][:60]}...")
        logger.info(f"  Confidence: [{conf_bar}] {instinct['confidence']:.2f}")
        logger.info("")

    save_instincts_index(index)

    # Update last analyzed marker (only if not incremental, or if we successfully analyzed)
    if args.incremental and not args.full:
        obs_file = get_observations_file()
        if obs_file.exists():
            file_size = obs_file.stat().st_size
            # Count total lines in file
            with open(obs_file, 'r', encoding='utf-8') as f:
                line_count = sum(1 for _ in f)
            save_analyzed_state(line_count, file_size)

    logger.info(f"{'=' * 60}")
    logger.info(f"Created: {created}, Updated: {updated}")
    logger.info(f"Total instincts: {len(index['instincts'])}")

    return 0


def cmd_list(args):
    """List all instincts."""
    index = load_instincts_index()
    instincts = index.get('instincts', [])

    if not instincts:
        logger.info("No instincts found. Run 'analyze' to generate from observations.")
        return 0

    # Sort by confidence
    instincts = sorted(instincts, key=lambda x: x.get('confidence', 0), reverse=True)

    logger.info(f"\n{'ID':<40} {'Confidence':<12} {'Evidence':<10} {'Domain':<15}")
    logger.info("=" * 80)

    for inst in instincts:
        conf = inst.get('confidence', 0)
        conf_bar = '█' * int(conf * 10) + '░' * (10 - int(conf * 10))
        logger.info(f"{inst['id'][:40]:<40} [{conf_bar}] {inst.get('evidence_count', 0):<10} {inst.get('domain', 'N/A'):<15}")

    logger.info(f"\nTotal: {len(instincts)} instincts")
    return 0


def cmd_show(args):
    """Show details of a specific instinct."""
    if not validate_instinct_id(args.id):
        logger.error(f"Invalid instinct ID: {args.id}")
        return 1

    instinct = load_instinct(args.id)

    if not instinct:
        logger.error(f"Instinct not found: {args.id}")
        return 1

    logger.info(f"\n{'=' * 60}")
    logger.info(f"Instinct: {instinct.get('id', 'N/A')}")
    logger.info(f"{'=' * 60}\n")

    conf = instinct.get('confidence', 0)
    conf_bar = '█' * int(conf * 10) + '░' * (10 - int(conf * 10))

    logger.info(f"Trigger:    {instinct.get('trigger', 'N/A')}")
    logger.info(f"Confidence: [{conf_bar}] {conf:.2f}")
    logger.info(f"Evidence:   {instinct.get('evidence_count', 0)} observations")
    logger.info(f"Domain:     {instinct.get('domain', 'N/A')}")
    logger.info(f"Source:     {instinct.get('source', 'N/A')}")
    logger.info(f"Last seen:  {instinct.get('last_observed', 'N/A')}")
    logger.info(f"Created:    {instinct.get('created_at', 'N/A')}")
    logger.info("")

    if instinct.get('body'):
        logger.info("Content:")
        logger.info("-" * 40)
        logger.info(instinct['body'][:500])

    return 0


def cmd_promote(args):
    """Increase confidence of an instinct."""
    if not validate_instinct_id(args.id):
        logger.error(f"Invalid instinct ID: {args.id}")
        return 1

    index = load_instincts_index()

    for inst in index.get('instincts', []):
        if inst['id'] == args.id:
            old_conf = inst.get('confidence', 0.5)
            inst['confidence'] = min(MAX_CONFIDENCE, old_conf + MIN_CONFIDENCE)
            inst['evidence_count'] = inst.get('evidence_count', 0) + 1
            save_instincts_index(index)

            # Update file
            instinct = load_instinct(args.id)
            if instinct:
                instinct['confidence'] = inst['confidence']
                instinct['evidence_count'] = inst['evidence_count']
                create_instinct_file(instinct)

            logger.info(f"Promoted {args.id}: {old_conf:.2f} → {inst['confidence']:.2f}")
            return 0

    print(f"Instinct not found: {args.id}")
    return 1


def cmd_demote(args):
    """Decrease confidence of an instinct."""
    if not validate_instinct_id(args.id):
        logger.error(f"Invalid instinct ID: {args.id}")
        return 1

    index = load_instincts_index()

    for inst in index.get('instincts', []):
        if inst['id'] == args.id:
            old_conf = inst.get('confidence', 0.5)
            inst['confidence'] = max(MIN_CONFIDENCE, old_conf - MIN_CONFIDENCE)
            save_instincts_index(index)

            # Update file
            instinct = load_instinct(args.id)
            if instinct:
                instinct['confidence'] = inst['confidence']
                create_instinct_file(instinct)

            logger.info(f"Demoted {args.id}: {old_conf:.2f} → {inst['confidence']:.2f}")
            return 0

    print(f"Instinct not found: {args.id}")
    return 1


def cmd_delete(args):
    """Delete an instinct."""
    if not validate_instinct_id(args.id):
        logger.error(f"Invalid instinct ID: {args.id}")
        return 1

    index = load_instincts_index()
    original_count = len(index.get('instincts', []))

    index['instincts'] = [i for i in index.get('instincts', []) if i['id'] != args.id]

    if len(index['instincts']) == original_count:
        logger.error(f"Instinct not found: {args.id}")
        return 1

    save_instincts_index(index)

    # Remove file
    instinct_file = get_instincts_dir() / f"{args.id}.md"
    if instinct_file.exists():
        instinct_file.unlink()

    logger.info(f"Deleted instinct: {args.id}")
    return 0


def cmd_decay(args):
    """Apply confidence decay to unused instincts."""
    index = load_instincts_index()

    cutoff = datetime.now(timezone.utc) - timedelta(days=7)
    decayed = 0

    for inst in index.get('instincts', []):
        last_observed = inst.get('last_observed', '')
        try:
            last_date = datetime.strptime(last_observed, '%Y-%m-%d')
            if last_date < cutoff:
                old_conf = inst.get('confidence', 0.5)
                inst['confidence'] = max(MIN_CONFIDENCE, old_conf - WEEKLY_DECAY_RATE)
                decayed += 1

                # Update file
                instinct = load_instinct(inst['id'])
                if instinct:
                    instinct['confidence'] = inst['confidence']
                    create_instinct_file(instinct)

        except (ValueError, TypeError):
            continue

    save_instincts_index(index)
    logger.info(f"Applied decay to {decayed} instincts (rate: -{WEEKLY_DECAY_RATE})")
    return 0


def cmd_stats(args):
    """Show observation and instinct statistics."""
    observations = list(load_observations())
    index = load_instincts_index()
    instincts = index.get('instincts', [])

    logger.info("\n" + "=" * 60)
    logger.info("OBSERVATION STATISTICS")
    logger.info("=" * 60)

    if observations:
        tool_counts = Counter(o.get('tool_name', '') for o in observations if o.get('event_type') == 'pre')
        session_counts = Counter(o.get('session_id', '') for o in observations)

        logger.info(f"\nTotal observations: {len(observations)}")
        logger.info(f"Unique sessions: {len(session_counts)}")
        logger.info(f"\nTop tools:")
        for tool, count in tool_counts.most_common(10):
            logger.info(f"  {tool}: {count}")
    else:
        logger.info("\nNo observations recorded yet.")

    logger.info("\n" + "=" * 60)
    logger.info("INSTINCT STATISTICS")
    logger.info("=" * 60)

    if instincts:
        confidences = [i.get('confidence', 0) for i in instincts]
        domains = Counter(i.get('domain', 'unknown') for i in instincts)

        logger.info(f"\nTotal instincts: {len(instincts)}")
        logger.info(f"Average confidence: {sum(confidences) / len(confidences):.2f}")
        logger.info(f"High confidence (>0.7): {sum(1 for c in confidences if c > 0.7)}")
        logger.info(f"\nBy domain:")
        for domain, count in domains.most_common():
            logger.info(f"  {domain}: {count}")
    else:
        logger.info("\nNo instincts generated yet.")

    return 0


def cmd_export(args):
    """Export instincts to JSON file."""
    index = load_instincts_index()
    instincts_data = []

    for inst_summary in index.get('instincts', []):
        full_instinct = load_instinct(inst_summary['id'])
        if full_instinct:
            instincts_data.append(full_instinct)

    output_file = Path(args.output)
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                'version': '1.0',
                'exported_at': datetime.now(timezone.utc).isoformat() + 'Z',
                'instincts': instincts_data,
            }, f, indent=2)
        logger.info(f"Exported {len(instincts_data)} instincts to {output_file}")
        return 0
    except IOError as e:
        logger.error(f"Export failed: {e}")
        return 1


def cmd_import_instincts(args):
    """Import instincts from JSON file."""
    input_file = Path(args.input)

    if not input_file.exists():
        logger.error(f"File not found: {input_file}")
        return 1

    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        logger.error(f"Failed to read file: {e}")
        return 1

    imported = 0
    index = load_instincts_index()
    existing_ids = {i['id'] for i in index.get('instincts', [])}

    for instinct in data.get('instincts', []):
        if instinct.get('id') not in existing_ids:
            # Add to index
            index['instincts'].append({
                'id': instinct['id'],
                'trigger': instinct.get('trigger', ''),
                'confidence': instinct.get('confidence', 0.5),
                'evidence_count': instinct.get('evidence_count', 1),
                'domain': instinct.get('domain', 'workflow'),
            })
            # Create file
            create_instinct_file(instinct)
            imported += 1

    save_instincts_index(index)
    logger.info(f"Imported {imported} new instincts")
    return 0


# =============================================================================
# Team Collaboration
# =============================================================================

def detect_conflicts(local: List[Dict[str, Any]], remote: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Detect conflicts between local and remote instincts.

    Returns:
        {
            'only_local': [...],
            'only_remote': [...],
            'conflicts': [
                {
                    'id': '...',
                    'local': {...},
                    'remote': {...},
                    'diff_fields': ['confidence', 'evidence_count']
                }
            ],
            'identical': [...]
        }
    """
    local_by_id = {inst['id']: inst for inst in local}
    remote_by_id = {inst['id']: inst for inst in remote}

    local_ids = set(local_by_id.keys())
    remote_ids = set(remote_by_id.keys())

    result = {
        'only_local': [local_by_id[iid] for iid in local_ids - remote_ids],
        'only_remote': [remote_by_id[iid] for iid in remote_ids - local_ids],
        'conflicts': [],
        'identical': []
    }

    # Check common IDs for conflicts
    common_ids = local_ids & remote_ids
    for iid in common_ids:
        local_inst = local_by_id[iid]
        remote_inst = remote_by_id[iid]

        diff_fields = []
        # Compare key fields
        for field in ['confidence', 'evidence_count', 'trigger', 'domain']:
            local_val = local_inst.get(field)
            remote_val = remote_inst.get(field)
            if local_val != remote_val:
                diff_fields.append(field)

        if diff_fields:
            result['conflicts'].append({
                'id': iid,
                'local': local_inst,
                'remote': remote_inst,
                'diff_fields': diff_fields
            })
        else:
            result['identical'].append(iid)

    return result


def resolve_conflict(local: Dict[str, Any], remote: Dict[str, Any], strategy: str) -> Dict[str, Any]:
    """Resolve a single conflict using the specified strategy."""
    if strategy == 'keep-local':
        return local
    elif strategy == 'keep-remote':
        return remote
    elif strategy == 'keep-higher':
        local_conf = local.get('confidence', 0)
        remote_conf = remote.get('confidence', 0)
        return local if local_conf >= remote_conf else remote
    else:
        raise ValueError(f"Unknown strategy: {strategy}")


def generate_merge_report(conflicts_data: Dict[str, Any], resolved: Dict[str, str], strategy: str) -> str:
    """Generate human-readable merge report."""
    lines = []
    lines.append("=" * 60)
    lines.append("                   MERGE REPORT")
    lines.append("=" * 60)
    lines.append("")
    lines.append(f"Strategy: {strategy}")
    lines.append("")

    # Added from remote
    added = conflicts_data['only_remote']
    if added:
        lines.append(f"Added from remote: {len(added)}")
        for inst in added[:5]:  # Show first 5
            conf = inst.get('confidence', 0)
            lines.append(f"  - {inst['id']} (confidence: {conf:.2f})")
        if len(added) > 5:
            lines.append(f"  ... and {len(added) - 5} more")
        lines.append("")

    # Conflicts resolved
    conflicts = conflicts_data['conflicts']
    if conflicts:
        lines.append(f"Conflicts resolved: {len(conflicts)}")
        for conflict in conflicts[:5]:  # Show first 5
            iid = conflict['id']
            choice = resolved.get(iid, 'unknown')
            local_conf = conflict['local'].get('confidence', 0)
            remote_conf = conflict['remote'].get('confidence', 0)

            if choice == 'local':
                lines.append(f"  - {iid}")
                lines.append(f"    Kept: LOCAL (confidence: {local_conf:.2f} >= {remote_conf:.2f})")
            elif choice == 'remote':
                lines.append(f"  - {iid}")
                lines.append(f"    Kept: REMOTE (confidence: {remote_conf:.2f} > {local_conf:.2f})")

        if len(conflicts) > 5:
            lines.append(f"  ... and {len(conflicts) - 5} more")
        lines.append("")

    # Unchanged
    unchanged = len(conflicts_data['only_local']) + len(conflicts_data['identical'])
    lines.append(f"Unchanged: {unchanged}")
    lines.append("")

    # Total after merge
    total = len(conflicts_data['only_local']) + len(conflicts_data['only_remote']) + len(conflicts_data['identical']) + len(conflicts_data['conflicts'])
    lines.append(f"Total instincts after merge: {total}")
    lines.append("=" * 60)

    return '\n'.join(lines)


def generate_diff_report(conflicts_data: Dict[str, Any], summary_only: bool = False) -> str:
    """Generate human-readable diff report."""
    lines = []
    lines.append("=" * 60)
    lines.append("                    INSTINCT DIFF")
    lines.append("=" * 60)
    lines.append("")

    only_local = conflicts_data['only_local']
    only_remote = conflicts_data['only_remote']
    conflicts = conflicts_data['conflicts']
    identical = conflicts_data['identical']

    if only_local:
        lines.append(f"Only in LOCAL ({len(only_local)}):")
        if not summary_only:
            for inst in only_local[:10]:
                lines.append(f"  - {inst['id']}")
            if len(only_local) > 10:
                lines.append(f"  ... and {len(only_local) - 10} more")
        lines.append("")

    if only_remote:
        lines.append(f"Only in REMOTE ({len(only_remote)}):")
        if not summary_only:
            for inst in only_remote[:10]:
                lines.append(f"  - {inst['id']}")
            if len(only_remote) > 10:
                lines.append(f"  ... and {len(only_remote) - 10} more")
        lines.append("")

    if conflicts:
        lines.append(f"CONFLICTS ({len(conflicts)}):")
        if not summary_only:
            for conflict in conflicts[:10]:
                iid = conflict['id']
                local_inst = conflict['local']
                remote_inst = conflict['remote']
                diff_fields = conflict['diff_fields']

                lines.append(f"  ID: {iid}")
                for field in diff_fields:
                    local_val = local_inst.get(field, 'N/A')
                    remote_val = remote_inst.get(field, 'N/A')
                    lines.append(f"    {field}: LOCAL={local_val}, REMOTE={remote_val}")
                lines.append("")

            if len(conflicts) > 10:
                lines.append(f"  ... and {len(conflicts) - 10} more")
        lines.append("")

    lines.append(f"IDENTICAL ({len(identical)}):")
    if not summary_only and identical:
        for iid in list(identical)[:10]:
            lines.append(f"  - {iid}")
        if len(identical) > 10:
            lines.append(f"  ... and {len(identical) - 10} more")

    lines.append("")
    lines.append("=" * 60)

    return '\n'.join(lines)


def cmd_diff(args):
    """Compare local instincts with another file.

    Shows:
    - Instincts only in local
    - Instincts only in remote
    - Instincts with differences (confidence, evidence_count, etc.)
    """
    input_file = Path(args.input)

    if not input_file.exists():
        logger.error(f"File not found: {input_file}")
        return 1

    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            remote_data = json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        logger.error(f"Failed to read remote file: {e}")
        return 1

    # Load local instincts
    local_index = load_instincts_index()
    local_instincts = []
    for inst_summary in local_index.get('instincts', []):
        full_instinct = load_instinct(inst_summary['id'])
        if full_instinct:
            local_instincts.append(full_instinct)

    # Load remote instincts
    remote_instincts = remote_data.get('instincts', [])

    # Detect conflicts
    conflicts_data = detect_conflicts(local_instincts, remote_instincts)

    # Generate report
    report = generate_diff_report(conflicts_data, summary_only=args.summary)
    logger.info("\n" + report)

    return 0


def cmd_merge(args):
    """Merge instincts from another file with conflict resolution.

    Strategies:
    - keep-local: Keep local version on conflict
    - keep-remote: Keep remote version on conflict
    - keep-higher: Keep version with higher confidence
    """
    input_file = Path(args.input)
    strategy = args.strategy

    if not input_file.exists():
        logger.error(f"File not found: {input_file}")
        return 1

    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            remote_data = json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        logger.error(f"Failed to read remote file: {e}")
        return 1

    # Load local instincts
    local_index = load_instincts_index()
    local_instincts = []
    for inst_summary in local_index.get('instincts', []):
        full_instinct = load_instinct(inst_summary['id'])
        if full_instinct:
            local_instincts.append(full_instinct)

    # Load remote instincts
    remote_instincts = remote_data.get('instincts', [])

    # Detect conflicts
    conflicts_data = detect_conflicts(local_instincts, remote_instincts)

    # Track resolution decisions
    resolved = {}

    # Dry run mode - just show what would happen
    if args.dry_run:
        logger.info("\n=== DRY RUN MODE ===\n")

        # Simulate resolution
        for conflict in conflicts_data['conflicts']:
            iid = conflict['id']
            chosen = resolve_conflict(conflict['local'], conflict['remote'], strategy)
            if chosen == conflict['local']:
                resolved[iid] = 'local'
            else:
                resolved[iid] = 'remote'

        report = generate_merge_report(conflicts_data, resolved, strategy)
        logger.info("\n" + report)
        logger.info("\nNo changes made (dry run mode)")
        return 0

    # Actual merge
    merged_instincts = {}

    # Keep all local-only instincts
    for inst in conflicts_data['only_local']:
        merged_instincts[inst['id']] = inst

    # Add all remote-only instincts
    for inst in conflicts_data['only_remote']:
        merged_instincts[inst['id']] = inst

    # Keep all identical instincts (from local)
    for iid in conflicts_data['identical']:
        local_inst = next(i for i in local_instincts if i['id'] == iid)
        merged_instincts[iid] = local_inst

    # Resolve conflicts
    for conflict in conflicts_data['conflicts']:
        iid = conflict['id']
        chosen = resolve_conflict(conflict['local'], conflict['remote'], strategy)
        merged_instincts[iid] = chosen

        if chosen == conflict['local']:
            resolved[iid] = 'local'
        else:
            resolved[iid] = 'remote'

    # Update index
    new_index = {'instincts': []}
    for iid, inst in merged_instincts.items():
        new_index['instincts'].append({
            'id': inst['id'],
            'trigger': inst.get('trigger', ''),
            'confidence': inst.get('confidence', 0.5),
            'evidence_count': inst.get('evidence_count', 1),
            'domain': inst.get('domain', 'workflow'),
        })

        # Create/update instinct file
        create_instinct_file(inst)

    save_instincts_index(new_index)

    # Generate report
    report = generate_merge_report(conflicts_data, resolved, strategy)
    logger.info("\n" + report)

    return 0


def cmd_insights(args):
    """Show advanced insights from pattern analysis."""
    observations = list(load_observations())

    if not observations:
        logger.info("No observations found. Run some tool operations first.")
        return 1

    logger.info("\n" + "=" * 60)
    logger.info("ADVANCED PATTERN INSIGHTS")
    logger.info("=" * 60)

    # Tool sequence TF-IDF
    logger.info("\n--- TF-IDF Analysis (Most Distinctive Patterns) ---")
    sequences = []
    sessions = defaultdict(list)
    for obs in observations:
        if obs.get('event_type') == 'pre':
            sessions[obs.get('session_id', 'unknown')].append(obs)

    for session_id, session_obs in sessions.items():
        tools = [o.get('tool_name', '') for o in session_obs]
        for seq_len in range(2, 5):
            for i in range(len(tools) - seq_len + 1):
                seq = tuple(tools[i:i + seq_len])
                if len(set(seq)) > 1:
                    sequences.append(seq)

    if sequences:
        tfidf_scores = calculate_tf_idf(sequences, min_doc_freq=2)
        sorted_tfidf = sorted(tfidf_scores.items(), key=lambda x: x[1], reverse=True)[:10]

        for seq, score in sorted_tfidf:
            logger.info(f"  {' → '.join(seq)}: {score:.4f}")
    else:
        logger.info("  No sequences found.")

    # Anomalies
    logger.info("\n--- Anomaly Detection (Unusual Usage Patterns) ---")
    anomalies = detect_anomalies(observations, threshold_std=1.5)
    if anomalies:
        for anomaly in anomalies[:10]:
            logger.info(f"  [{anomaly['type']}] {anomaly['trigger']}")
            logger.info(f"    {anomaly['action']}")
    else:
        logger.info("  No anomalies detected.")

    # Time-based workflows
    logger.info("\n--- Time-Window Workflow Patterns (30-min windows) ---")
    workflows = detect_workflow_patterns(observations, window_minutes=30)
    if workflows:
        for wf in workflows[:10]:
            logger.info(f"  {wf['action']} (observed {wf['evidence_count']} times)")
    else:
        logger.info("  No time-window patterns found.")

    # Pattern clustering
    logger.info("\n--- Pattern Clustering (Similar Workflows) ---")
    all_patterns = detect_tool_sequences(observations)
    patterns_with_seq = [p for p in all_patterns if 'pattern' in p]

    if patterns_with_seq:
        clusters = cluster_similar_patterns(patterns_with_seq, similarity_threshold=0.6)
        for i, cluster in enumerate(clusters[:5], 1):
            logger.info(f"  Cluster {i} ({len(cluster)} patterns):")
            for pattern in cluster[:3]:
                logger.info(f"    - {' → '.join(pattern['pattern'])}")
    else:
        logger.info("  No patterns to cluster.")

    # Statistical confidence example
    logger.info("\n--- Statistical Confidence (Wilson Score) ---")
    tool_counts = Counter()
    for obs in observations:
        if obs.get('event_type') == 'pre':
            tool_counts[obs.get('tool_name', '')] += 1

    total_obs = len(observations)
    for tool, count in tool_counts.most_common(5):
        freq = count / total_obs
        confidence = calculate_statistical_confidence(count, total_obs, freq)
        logger.info(f"  {tool}: {count} uses, frequency={freq:.3f}, confidence={confidence:.3f}")

    logger.info("\n" + "=" * 60)
    return 0


def cmd_dashboard(args):
    """Generate HTML analytics dashboard."""
    try:
        # Import dashboard module
        script_dir = Path(__file__).parent
        dashboard_script = script_dir / 'dashboard.py'

        if not dashboard_script.exists():
            logger.error(f"Dashboard script not found: {dashboard_script}")
            return 1

        # Import and call dashboard generation
        import subprocess
        cmd = [sys.executable, str(dashboard_script)]

        if args.output:
            cmd.extend(['-o', args.output])

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            logger.error(f"Dashboard generation failed: {result.stderr}")
            return 1

        logger.info(result.stdout)

        if args.open:
            # Open in browser
            import webbrowser
            output_path = args.output if args.output else str(get_caw_dir() / 'dashboard.html')
            webbrowser.open(f'file://{Path(output_path).absolute()}')
            logger.info("Opening dashboard in browser...")

        return 0

    except Exception as e:
        logger.error(f"Error generating dashboard: {e}")
        return 1


def main():
    parser = argparse.ArgumentParser(
        description='Instinct CLI - Manage learned instincts from observations'
    )
    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # analyze
    analyze_parser = subparsers.add_parser('analyze', help='Analyze observations and generate instincts')
    analyze_parser.add_argument(
        '--incremental', '-i',
        action='store_true',
        help='Only analyze observations since last run'
    )
    analyze_parser.add_argument(
        '--full',
        action='store_true',
        help='Force full analysis (ignore last analyzed state)'
    )
    analyze_parser.add_argument(
        '--advanced', '-a',
        action='store_true',
        help='Use advanced statistical pattern detection'
    )

    # list
    subparsers.add_parser('list', help='List all instincts')

    # show
    show_parser = subparsers.add_parser('show', help='Show instinct details')
    show_parser.add_argument('id', help='Instinct ID')

    # promote
    promote_parser = subparsers.add_parser('promote', help='Increase instinct confidence')
    promote_parser.add_argument('id', help='Instinct ID')

    # demote
    demote_parser = subparsers.add_parser('demote', help='Decrease instinct confidence')
    demote_parser.add_argument('id', help='Instinct ID')

    # delete
    delete_parser = subparsers.add_parser('delete', help='Delete an instinct')
    delete_parser.add_argument('id', help='Instinct ID')

    # decay
    subparsers.add_parser('decay', help='Apply confidence decay to unused instincts')

    # stats
    subparsers.add_parser('stats', help='Show statistics')

    # export
    export_parser = subparsers.add_parser('export', help='Export instincts to JSON')
    export_parser.add_argument('-o', '--output', default='instincts-export.json', help='Output file')

    # import
    import_parser = subparsers.add_parser('import', help='Import instincts from JSON')
    import_parser.add_argument('-i', '--input', required=True, help='Input file')

    # insights
    subparsers.add_parser('insights', help='Show advanced pattern insights')

    # dashboard
    dashboard_parser = subparsers.add_parser('dashboard', help='Generate HTML analytics dashboard')
    dashboard_parser.add_argument('-o', '--output', help='Output file path (default: .caw/dashboard.html)')
    dashboard_parser.add_argument('--open', action='store_true', help='Open in browser after generation')

    # diff
    diff_parser = subparsers.add_parser('diff', help='Compare with another instinct file')
    diff_parser.add_argument('-i', '--input', required=True, help='File to compare')
    diff_parser.add_argument('--summary', action='store_true', help='Show summary only')

    # merge
    merge_parser = subparsers.add_parser('merge', help='Merge instincts from file')
    merge_parser.add_argument('-i', '--input', required=True, help='Input file to merge')
    merge_parser.add_argument(
        '-s', '--strategy',
        choices=['keep-local', 'keep-remote', 'keep-higher'],
        default='keep-higher',
        help='Conflict resolution strategy'
    )
    merge_parser.add_argument('--dry-run', action='store_true', help='Show what would be merged')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    commands = {
        'analyze': cmd_analyze,
        'list': cmd_list,
        'show': cmd_show,
        'promote': cmd_promote,
        'demote': cmd_demote,
        'delete': cmd_delete,
        'decay': cmd_decay,
        'stats': cmd_stats,
        'export': cmd_export,
        'import': cmd_import_instincts,
        'insights': cmd_insights,
        'dashboard': cmd_dashboard,
        'diff': cmd_diff,
        'merge': cmd_merge,
    }

    return commands[args.command](args)


if __name__ == '__main__':
    sys.exit(main())
