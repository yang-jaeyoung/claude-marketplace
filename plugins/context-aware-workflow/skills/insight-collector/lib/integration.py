#!/usr/bin/env python3
"""
Integration API for Insight Collector

Provides programmatic access to insights and instincts for other CAW skills.
"""

import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from .common import get_project_dir, get_caw_dir
from .types import (
    Insight,
    InstinctSummary,
    EvolutionCandidates,
    Metrics,
)


# =============================================================================
# Insights API (for context-helper, knowledge-base)
# =============================================================================

def list_insights(limit: int = 20) -> List[Insight]:
    """List recent insights with metadata."""
    insights_dir = get_caw_dir() / 'insights'
    if not insights_dir.exists():
        return []

    insights = []
    for file in sorted(insights_dir.glob('*.md'), reverse=True)[:limit]:
        insight = parse_insight_file(file)
        if insight:
            insights.append(insight)

    return insights


def parse_insight_file(file_path: Path) -> Optional[Insight]:
    """Parse an insight markdown file."""
    try:
        content = file_path.read_text(encoding='utf-8')

        result = {
            'file': str(file_path),
            'filename': file_path.name,
        }

        # Extract title
        title_match = re.search(r'^# Insight: (.+)$', content, re.MULTILINE)
        if title_match:
            result['title'] = title_match.group(1).strip()

        # Extract tags
        tags_match = re.search(r'## Tags\s*\n(.+?)(?:\n##|\Z)', content, re.DOTALL)
        if tags_match:
            tags = re.findall(r'#(\S+)', tags_match.group(1))
            result['tags'] = tags

        # Extract content
        content_match = re.search(r'## Content\s*\n(.+?)(?:\n##|\Z)', content, re.DOTALL)
        if content_match:
            result['content'] = content_match.group(1).strip()

        return result
    except IOError:
        return None


def search_insights(query: str, tags: Optional[List[str]] = None) -> List[Insight]:
    """Search insights by query string and/or tags."""
    all_insights = list_insights(limit=100)
    results = []

    query_lower = query.lower() if query else ''

    for insight in all_insights:
        # Tag filter
        if tags:
            insight_tags = insight.get('tags', [])
            if not any(t in insight_tags for t in tags):
                continue

        # Query filter
        if query_lower:
            title = insight.get('title', '').lower()
            content = insight.get('content', '').lower()
            if query_lower not in title and query_lower not in content:
                continue

        results.append(insight)

    return results


def get_relevant_insights(context: str, limit: int = 5) -> List[Insight]:
    """Get insights relevant to the given context (for context-helper)."""
    # Simple keyword extraction
    keywords = re.findall(r'\b[a-zA-Z]{4,}\b', context.lower())
    keyword_set = set(keywords)

    all_insights = list_insights(limit=50)
    scored = []

    for insight in all_insights:
        title = insight.get('title', '').lower()
        content = insight.get('content', '').lower()
        tags = insight.get('tags', [])

        score = 0
        for kw in keyword_set:
            if kw in title:
                score += 3
            if kw in content:
                score += 1
            if kw in tags:
                score += 2

        if score > 0:
            scored.append((score, insight))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [s[1] for s in scored[:limit]]


# =============================================================================
# Instincts API (for pattern-learner, evolve command)
# =============================================================================

def list_instincts(min_confidence: float = 0.0) -> List[InstinctSummary]:
    """List instincts with optional confidence filter."""
    index_file = get_caw_dir() / 'instincts' / 'index.json'
    if not index_file.exists():
        return []

    try:
        with open(index_file, 'r', encoding='utf-8') as f:
            index = json.load(f)
    except (json.JSONDecodeError, IOError):
        return []

    instincts = index.get('instincts', [])
    if min_confidence > 0:
        instincts = [i for i in instincts if i.get('confidence', 0) >= min_confidence]

    return sorted(instincts, key=lambda x: x.get('confidence', 0), reverse=True)


def get_evolution_candidates() -> EvolutionCandidates:
    """Get instincts eligible for evolution (confidence >= 0.6), categorized."""
    candidates = list_instincts(min_confidence=0.6)

    result = {
        'commands': [],  # User-triggered workflows
        'skills': [],    # Auto-applicable patterns
        'agents': [],    # Complex reasoning
    }

    for inst in candidates:
        domain = inst.get('domain', '')
        trigger = inst.get('trigger', '')

        if 'workflow' in domain or '→' in trigger:
            result['commands'].append(inst)
        elif 'preference' in domain or 'error' in domain:
            result['skills'].append(inst)
        else:
            result['agents'].append(inst)

    return result


# =============================================================================
# Metrics API (for session-persister)
# =============================================================================

def get_insight_count() -> int:
    """Get total count of insights."""
    insights_dir = get_caw_dir() / 'insights'
    if not insights_dir.exists():
        return 0
    return len(list(insights_dir.glob('*.md')))


def get_instinct_count() -> int:
    """Get total count of instincts."""
    instincts = list_instincts()
    return len(instincts)


def get_observation_count() -> int:
    """Get total count of observations."""
    obs_file = get_caw_dir() / 'observations' / 'observations.jsonl'
    if not obs_file.exists():
        return 0

    try:
        with open(obs_file, 'r') as f:
            return sum(1 for _ in f)
    except IOError:
        return 0


def get_metrics() -> Metrics:
    """Get all metrics for session-persister."""
    return {
        'insights_captured': get_insight_count(),
        'instincts_generated': get_instinct_count(),
        'observations_recorded': get_observation_count(),
    }
