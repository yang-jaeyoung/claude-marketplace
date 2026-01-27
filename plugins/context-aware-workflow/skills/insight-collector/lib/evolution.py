#!/usr/bin/env python3
"""
Evolution scaffold generation module for insight-collector.

Transforms high-confidence instincts into reusable commands, skills, or agents.
"""

import json
import re
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from .common import get_caw_dir, ensure_dir
from .types import InstinctSummary

# =============================================================================
# Constants
# =============================================================================

EVOLUTION_TYPES = ('command', 'skill', 'agent')

# Classification keywords
COMMAND_TRIGGERS = ['when user', 'on request', 'user asks for', 'when requesting']
SKILL_TRIGGERS = ['when editing', 'before', 'after', 'during', 'automatically']
AGENT_TRIGGERS = ['analyze', 'diagnose', 'investigate', 'decide', 'complex', 'reasoning']

MIN_CONFIDENCE = 0.6  # Minimum confidence for evolution


# =============================================================================
# Directory Management
# =============================================================================

def get_evolved_dir(evolution_type: str) -> Path:
    """Get directory for evolved components.

    Args:
        evolution_type: Type of evolution ('command', 'skill', or 'agent')

    Returns:
        Path to evolved component directory

    Raises:
        ValueError: If evolution_type is invalid
    """
    if evolution_type not in EVOLUTION_TYPES:
        raise ValueError(f"Invalid evolution type: {evolution_type}. Must be one of {EVOLUTION_TYPES}")

    base = get_caw_dir() / 'evolved'

    if evolution_type == 'command':
        return base / 'commands'
    elif evolution_type == 'skill':
        return base / 'skills'
    elif evolution_type == 'agent':
        return base / 'agents'


def ensure_evolved_dirs() -> None:
    """Create all evolution directories if they don't exist."""
    for evo_type in EVOLUTION_TYPES:
        ensure_dir(get_evolved_dir(evo_type))


# =============================================================================
# Utility Functions
# =============================================================================

def slugify(text: str) -> str:
    """Convert text to kebab-case slug.

    Args:
        text: Input text

    Returns:
        kebab-case slug

    Example:
        >>> slugify("Safe Modify Pattern")
        'safe-modify-pattern'
    """
    # Convert to lowercase
    text = text.lower()
    # Replace spaces and underscores with hyphens
    text = re.sub(r'[\s_]+', '-', text)
    # Remove non-alphanumeric characters except hyphens
    text = re.sub(r'[^a-z0-9-]', '', text)
    # Remove duplicate hyphens
    text = re.sub(r'-+', '-', text)
    # Strip leading/trailing hyphens
    text = text.strip('-')
    return text


def classify_instinct(instinct: Dict[str, Any]) -> str:
    """Classify instinct into command/skill/agent based on patterns.

    Args:
        instinct: Instinct dictionary with trigger, action, domain fields

    Returns:
        Evolution type: 'command', 'skill', or 'agent'
    """
    trigger = instinct.get('trigger', '').lower()
    action = instinct.get('action', '').lower()
    domain = instinct.get('domain', '').lower()

    # Check for agent indicators (complex reasoning)
    if any(kw in trigger or kw in action for kw in AGENT_TRIGGERS):
        # Look for decision trees or multi-step reasoning
        if 'if' in action or 'then' in action or '→' in action and action.count('→') >= 3:
            return 'agent'

    # Check for command indicators (user-triggered workflows)
    if any(kw in trigger for kw in COMMAND_TRIGGERS):
        # Multi-step workflow
        if '→' in action or 'step' in action:
            return 'command'

    # Check for skill indicators (auto-applicable patterns)
    if any(kw in trigger for kw in SKILL_TRIGGERS):
        return 'skill'

    # Domain-based classification
    if 'workflow' in domain:
        return 'command'
    elif 'preference' in domain or 'error' in domain:
        return 'skill'

    # Default to skill for simple patterns
    return 'skill'


def extract_steps_from_action(action: str) -> list:
    """Extract workflow steps from action string.

    Args:
        action: Action description (may contain → separators or step numbers)

    Returns:
        List of step descriptions
    """
    # Try arrow-separated steps first
    if '→' in action:
        steps = [s.strip() for s in action.split('→')]
        return [s for s in steps if s]

    # Try numbered steps (Step 1: xxx or 1. xxx)
    step_pattern = r'(?:step\s+\d+[:.]\s*|\d+\.\s*)([^\n]+)'
    matches = re.findall(step_pattern, action, re.IGNORECASE)
    if matches:
        return [s.strip() for s in matches if s.strip()]

    # Fallback: return as single step
    return [action.strip()]


# =============================================================================
# Scaffold Generation Functions
# =============================================================================

def generate_command_scaffold(instinct: Dict[str, Any], name: str) -> str:
    """Generate command markdown from instinct.

    Args:
        instinct: Instinct dictionary
        name: Command name (kebab-case)

    Returns:
        Command markdown content
    """
    instinct_id = instinct.get('id', 'unknown')
    confidence = instinct.get('confidence', 0.0)
    evidence_count = instinct.get('evidence_count', 0)
    trigger = instinct.get('trigger', '')
    action = instinct.get('action', '')
    domain = instinct.get('domain', '')
    timestamp = datetime.now(timezone.utc).isoformat()

    # Extract workflow steps
    steps = extract_steps_from_action(action)

    # Generate step sections
    step_sections = []
    for i, step in enumerate(steps, 1):
        step_sections.append(f"""### Step {i}: {step}

(Details to be customized based on your specific requirements)
""")

    workflow_section = '\n'.join(step_sections)

    template = f"""---
description: Auto-generated from instinct {instinct_id}
argument-hint: "[args]"
allowed-tools: Read, Write, Glob, Bash
---

# /cw:{name} - Evolved Command

## Origin

**Source Instinct:** {instinct_id}
**Confidence:** {confidence:.2f}
**Evidence:** {evidence_count} observations
**Generated:** {timestamp}

## Purpose

{trigger}

## Workflow

{workflow_section}

## Usage Examples

```bash
/cw:{name} <args>
```

## Boundaries

**Will:**
- Execute the workflow steps as defined
- Validate inputs before processing
- Provide clear feedback on results

**Will Not:**
- Modify files outside the project scope
- Execute without user confirmation for destructive operations
- Skip validation steps

---

*This command was auto-generated from learned behavior patterns.*
*Edit `.caw/evolved/commands/{name}.md` to customize.*
"""

    return template


def generate_skill_scaffold(instinct: Dict[str, Any], name: str) -> str:
    """Generate SKILL.md from instinct.

    Args:
        instinct: Instinct dictionary
        name: Skill name (kebab-case)

    Returns:
        Skill markdown content
    """
    instinct_id = instinct.get('id', 'unknown')
    confidence = instinct.get('confidence', 0.0)
    evidence_count = instinct.get('evidence_count', 0)
    trigger = instinct.get('trigger', '')
    action = instinct.get('action', '')
    timestamp = datetime.now(timezone.utc).isoformat()

    # Extract action steps
    steps = extract_steps_from_action(action)

    # Generate action list
    action_list = '\n'.join([f"{i}. {step}" for i, step in enumerate(steps, 1)])

    template = f"""---
name: {name}
description: Auto-generated from instinct {instinct_id}
allowed-tools: Read, Write, Glob
---

# {name.replace('-', ' ').title()} - Evolved Skill

## Origin

**Source Instinct:** {instinct_id}
**Confidence:** {confidence:.2f}
**Evidence:** {evidence_count} observations
**Generated:** {timestamp}

## Activation Trigger

{trigger}

## Behavioral Rule

When activated, this skill:

{action_list}

## Confidence Threshold

This skill was generated with confidence: **{confidence:.2f}**

High confidence indicates reliable pattern observed across multiple sessions.

## Integration

This skill activates automatically when the trigger condition is met.
No user interaction required.

## Boundaries

**Will:**
- Apply pattern automatically when conditions are met
- Maintain consistency with observed behaviors
- Skip if conditions don't match exactly

**Will Not:**
- Execute without checking trigger conditions
- Override explicit user instructions
- Apply pattern outside learned context

---

*This skill was auto-generated from learned behavior patterns.*
*Edit `.caw/evolved/skills/{name}/SKILL.md` to customize.*
"""

    return template


def generate_agent_scaffold(instinct: Dict[str, Any], name: str) -> str:
    """Generate agent markdown from instinct.

    Args:
        instinct: Instinct dictionary
        name: Agent name (kebab-case)

    Returns:
        Agent markdown content
    """
    instinct_id = instinct.get('id', 'unknown')
    confidence = instinct.get('confidence', 0.0)
    evidence_count = instinct.get('evidence_count', 0)
    trigger = instinct.get('trigger', '')
    action = instinct.get('action', '')
    domain = instinct.get('domain', '')
    timestamp = datetime.now(timezone.utc).isoformat()

    # Extract workflow phases
    steps = extract_steps_from_action(action)

    # Organize into phases (max 3 phases)
    phases = []
    if len(steps) == 1:
        phases = [("Analysis", steps[0])]
    elif len(steps) == 2:
        phases = [("Analysis", steps[0]), ("Execution", steps[1])]
    else:
        # Split into 3 phases
        third = len(steps) // 3
        phases = [
            ("Analysis", ' → '.join(steps[:third])),
            ("Processing", ' → '.join(steps[third:2*third])),
            ("Delivery", ' → '.join(steps[2*third:]))
        ]

    phase_sections = []
    for phase_name, phase_desc in phases:
        phase_sections.append(f"""### Phase: {phase_name}

{phase_desc}
""")

    workflow_section = '\n'.join(phase_sections)

    template = f"""---
name: {name}
description: Auto-generated from instinct {instinct_id}
model: sonnet
tier: sonnet
tools:
  - Read
  - Write
  - Glob
  - Grep
whenToUse: |
  {trigger}

  <example>
  Use this agent when dealing with {domain} tasks that require systematic analysis and decision-making.
  </example>
---

# {name.replace('-', ' ').title()} - Evolved Agent

## Origin

**Source Instinct:** {instinct_id}
**Confidence:** {confidence:.2f}
**Evidence:** {evidence_count} observations
**Generated:** {timestamp}

## Specialization

This agent specializes in {domain} domain, providing structured analysis and execution.

## Decision Logic

```
{action}
```

## Workflow

{workflow_section}

## Boundaries

**Will:**
- Follow the systematic workflow as defined
- Provide clear reasoning for decisions
- Handle edge cases within the learned domain
- Report findings clearly

**Will Not:**
- Make decisions outside the specialized domain
- Skip analysis phases
- Execute without gathering sufficient context
- Proceed if preconditions aren't met

## Model Routing

**Default:** Sonnet (balanced performance)
**Override:** Use Opus for complex cases via model parameter

---

*This agent was auto-generated from learned behavior patterns.*
*Edit `.caw/evolved/agents/{name}.md` to customize.*
"""

    return template


# =============================================================================
# Evolution Execution
# =============================================================================

def create_evolution(
    instinct: Dict[str, Any],
    evolution_type: str,
    name: str
) -> Dict[str, Any]:
    """Create evolved component from instinct.

    Args:
        instinct: Instinct dictionary
        evolution_type: Type of evolution ('command', 'skill', or 'agent')
        name: Component name (will be slugified)

    Returns:
        Dictionary with:
            - success: bool
            - path: str (absolute path to created file)
            - type: str (evolution type)
            - name: str (final name used)
            - error: Optional[str] (error message if failed)
    """
    # Validate evolution type
    if evolution_type not in EVOLUTION_TYPES:
        return {
            'success': False,
            'path': '',
            'type': evolution_type,
            'name': name,
            'error': f"Invalid evolution type: {evolution_type}"
        }

    # Slugify name
    slug = slugify(name)
    if not slug:
        return {
            'success': False,
            'path': '',
            'type': evolution_type,
            'name': name,
            'error': "Invalid name: could not generate valid slug"
        }

    # Ensure directories exist
    ensure_evolved_dirs()

    # Generate scaffold
    try:
        if evolution_type == 'command':
            content = generate_command_scaffold(instinct, slug)
            target_dir = get_evolved_dir('command')
            target_file = target_dir / f"{slug}.md"
        elif evolution_type == 'skill':
            content = generate_skill_scaffold(instinct, slug)
            target_dir = get_evolved_dir('skill') / slug
            ensure_dir(target_dir)
            target_file = target_dir / "SKILL.md"
        elif evolution_type == 'agent':
            content = generate_agent_scaffold(instinct, slug)
            target_dir = get_evolved_dir('agent')
            target_file = target_dir / f"{slug}.md"
    except Exception as e:
        return {
            'success': False,
            'path': '',
            'type': evolution_type,
            'name': slug,
            'error': f"Failed to generate scaffold: {str(e)}"
        }

    # Check if file already exists
    if target_file.exists():
        return {
            'success': False,
            'path': str(target_file),
            'type': evolution_type,
            'name': slug,
            'error': f"File already exists: {target_file}"
        }

    # Write file atomically
    try:
        with tempfile.NamedTemporaryFile(
            mode='w',
            dir=target_file.parent,
            delete=False,
            encoding='utf-8'
        ) as tmp:
            tmp.write(content)
            tmp_path = Path(tmp.name)

        tmp_path.replace(target_file)

        return {
            'success': True,
            'path': str(target_file),
            'type': evolution_type,
            'name': slug,
            'error': None
        }
    except Exception as e:
        return {
            'success': False,
            'path': str(target_file),
            'type': evolution_type,
            'name': slug,
            'error': f"Failed to write file: {str(e)}"
        }


def track_evolution(
    instinct_id: str,
    evolution_type: str,
    target_path: str,
    generated_name: str,
    confidence: float,
    evidence_count: int
) -> bool:
    """Add evolution record to instincts/index.json.

    Args:
        instinct_id: Source instinct ID
        evolution_type: Type of evolution
        target_path: Path to evolved component
        generated_name: Final name used
        confidence: Instinct confidence score
        evidence_count: Number of evidence observations

    Returns:
        True if tracking succeeded, False otherwise
    """
    index_file = get_caw_dir() / 'instincts' / 'index.json'

    if not index_file.exists():
        return False

    try:
        # Read existing index
        with open(index_file, 'r', encoding='utf-8') as f:
            index = json.load(f)
    except (json.JSONDecodeError, IOError):
        return False

    # Ensure evolutions array exists
    if 'evolutions' not in index:
        index['evolutions'] = []

    # Add evolution record
    evolution_record = {
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'source_instinct': instinct_id,
        'confidence': confidence,
        'evidence_count': evidence_count,
        'evolution_type': evolution_type,
        'target_path': target_path,
        'generated_name': generated_name
    }

    index['evolutions'].append(evolution_record)
    index['last_updated'] = datetime.now(timezone.utc).isoformat()

    # Write atomically
    try:
        with tempfile.NamedTemporaryFile(
            mode='w',
            dir=index_file.parent,
            delete=False,
            encoding='utf-8'
        ) as tmp:
            json.dump(index, tmp, indent=2, ensure_ascii=False)
            tmp_path = Path(tmp.name)

        tmp_path.replace(index_file)
        return True
    except Exception:
        return False


# =============================================================================
# Evolution Candidates
# =============================================================================

def get_evolution_candidates_list(instincts: list) -> Dict[str, list]:
    """Categorize instincts into evolution candidates.

    Args:
        instincts: List of instinct dictionaries

    Returns:
        Dictionary with 'commands', 'skills', 'agents' lists
    """
    result = {
        'commands': [],
        'skills': [],
        'agents': []
    }

    for instinct in instincts:
        # Skip low-confidence instincts
        if instinct.get('confidence', 0.0) < MIN_CONFIDENCE:
            continue

        # Classify and categorize
        category = classify_instinct(instinct)
        if category == 'command':
            result['commands'].append(instinct)
        elif category == 'skill':
            result['skills'].append(instinct)
        elif category == 'agent':
            result['agents'].append(instinct)

    return result
