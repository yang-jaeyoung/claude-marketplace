#!/usr/bin/env python3
"""Test script for evolution module."""

import sys
import os
from pathlib import Path

# Add skill root to path for imports
script_dir = Path(__file__).resolve().parent
skill_root = script_dir.parent
sys.path.insert(0, str(skill_root))

# Import evolution functions
try:
    from lib.evolution import (
        slugify,
        classify_instinct,
        extract_steps_from_action,
        generate_command_scaffold,
        generate_skill_scaffold,
        generate_agent_scaffold,
        EVOLUTION_TYPES,
        MIN_CONFIDENCE,
    )
    print("✓ Evolution module imports successfully")
except ImportError as e:
    print(f"✗ Import failed: {e}")
    sys.exit(1)

def test_slugify():
    """Test slugify function."""
    assert slugify('Safe Modify Pattern') == 'safe-modify-pattern'
    assert slugify('Pre-Commit Check') == 'pre-commit-check'
    assert slugify('Debug Detective') == 'debug-detective'
    assert slugify('multiple   spaces') == 'multiple-spaces'
    assert slugify('with_underscores') == 'with-underscores'
    print('✓ slugify works')

def test_classify_instinct():
    """Test instinct classification."""
    # Command
    test_instinct_cmd = {
        'trigger': 'when user asks to modify code',
        'action': 'Search with Grep → Edit file → Verify',
        'domain': 'workflow'
    }
    result = classify_instinct(test_instinct_cmd)
    assert result == 'command', f"Expected 'command', got '{result}'"

    # Skill
    test_instinct_skill = {
        'trigger': 'before git commit',
        'action': 'Check for debug statements',
        'domain': 'preference'
    }
    result = classify_instinct(test_instinct_skill)
    assert result == 'skill', f"Expected 'skill', got '{result}'"

    # Agent (complex reasoning)
    test_instinct_agent = {
        'trigger': 'when debugging complex error',
        'action': 'analyze stack → check dependencies → investigate → propose fix',
        'domain': 'debugging'
    }
    result = classify_instinct(test_instinct_agent)
    assert result == 'agent', f"Expected 'agent', got '{result}'"

    print('✓ classify_instinct works')

def test_extract_steps():
    """Test step extraction."""
    # Arrow-separated
    steps = extract_steps_from_action('Search → Edit → Verify')
    assert len(steps) == 3, f"Expected 3 steps, got {len(steps)}"
    assert steps == ['Search', 'Edit', 'Verify'], f"Unexpected steps: {steps}"

    # Numbered steps
    steps = extract_steps_from_action('Step 1: Search\nStep 2: Edit\nStep 3: Verify')
    assert len(steps) == 3, f"Expected 3 steps, got {len(steps)}"

    # Single step
    steps = extract_steps_from_action('Just do something')
    assert len(steps) == 1, f"Expected 1 step, got {len(steps)}"

    print('✓ extract_steps_from_action works')

def test_scaffolds():
    """Test scaffold generation."""
    test_instinct = {
        'id': 'test-123',
        'trigger': 'when user requests safe editing',
        'action': 'Search location → Edit file → Verify syntax',
        'confidence': 0.85,
        'evidence_count': 10,
        'domain': 'code-modification'
    }

    # Command scaffold
    cmd_scaffold = generate_command_scaffold(test_instinct, 'safe-edit')
    assert '/cw:safe-edit' in cmd_scaffold, "Command name not found in scaffold"
    assert 'test-123' in cmd_scaffold, "Instinct ID not found in scaffold"
    assert '0.85' in cmd_scaffold, "Confidence not found in scaffold"
    assert '## Workflow' in cmd_scaffold, "Workflow section not found"
    print('✓ generate_command_scaffold works')

    # Skill scaffold
    skill_scaffold = generate_skill_scaffold(test_instinct, 'safe-edit')
    assert 'name: safe-edit' in skill_scaffold, "Skill name not found"
    assert 'test-123' in skill_scaffold, "Instinct ID not found"
    assert '## Activation Trigger' in skill_scaffold, "Trigger section not found"
    print('✓ generate_skill_scaffold works')

    # Agent scaffold
    agent_scaffold = generate_agent_scaffold(test_instinct, 'safe-edit')
    assert 'name: safe-edit' in agent_scaffold, "Agent name not found"
    assert 'model: sonnet' in agent_scaffold, "Model not found"
    assert '## Workflow' in agent_scaffold, "Workflow section not found"
    print('✓ generate_agent_scaffold works')

def test_constants():
    """Test constants."""
    assert EVOLUTION_TYPES == ('command', 'skill', 'agent'), f"Unexpected types: {EVOLUTION_TYPES}"
    assert MIN_CONFIDENCE == 0.6, f"Unexpected min confidence: {MIN_CONFIDENCE}"
    print('✓ constants work')

if __name__ == '__main__':
    print('Testing evolution module...\n')

    try:
        test_slugify()
        test_classify_instinct()
        test_extract_steps()
        test_scaffolds()
        test_constants()

        print('\n✅ All evolution module tests passed!')
    except AssertionError as e:
        print(f'\n✗ Test failed: {e}')
        sys.exit(1)
    except Exception as e:
        print(f'\n✗ Unexpected error: {e}')
        import traceback
        traceback.print_exc()
        sys.exit(1)
