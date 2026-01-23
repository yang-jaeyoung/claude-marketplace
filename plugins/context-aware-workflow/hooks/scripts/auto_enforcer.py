#!/usr/bin/env python3
"""
Auto Mode Persistence Enforcer

This script runs on Stop events to check if auto mode is active
and enforce continuation if the expected phase signal was not detected.

Cross-platform compatible (macOS, Linux, Windows).
"""

import json
import os
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any, Tuple

# Signal patterns for detection
SIGNAL_PATTERNS = {
    'EXPANSION_COMPLETE': re.compile(r'SIGNAL:\s*EXPANSION_COMPLETE', re.IGNORECASE),
    'INIT_COMPLETE': re.compile(r'SIGNAL:\s*INIT_COMPLETE', re.IGNORECASE),
    'PLANNING_COMPLETE': re.compile(r'SIGNAL:\s*PLANNING_COMPLETE', re.IGNORECASE),
    'EXECUTION_COMPLETE': re.compile(r'SIGNAL:\s*EXECUTION_COMPLETE', re.IGNORECASE),
    'QA_COMPLETE': re.compile(r'SIGNAL:\s*QA_COMPLETE', re.IGNORECASE),
    'REVIEW_COMPLETE': re.compile(r'SIGNAL:\s*REVIEW_COMPLETE', re.IGNORECASE),
    'FIX_COMPLETE': re.compile(r'SIGNAL:\s*FIX_COMPLETE', re.IGNORECASE),
    'CHECK_COMPLETE': re.compile(r'SIGNAL:\s*CHECK_COMPLETE', re.IGNORECASE),
    'REFLECT_COMPLETE': re.compile(r'SIGNAL:\s*REFLECT_COMPLETE', re.IGNORECASE),
    'AUTO_COMPLETE': re.compile(r'SIGNAL:\s*AUTO_COMPLETE', re.IGNORECASE),
    'PHASE_ERROR': re.compile(r'SIGNAL:\s*PHASE_ERROR', re.IGNORECASE),
}

PHASE_TO_SIGNAL = {
    'expansion': 'EXPANSION_COMPLETE',
    'init': 'INIT_COMPLETE',
    'planning': 'PLANNING_COMPLETE',
    'execution': 'EXECUTION_COMPLETE',
    'qa': 'QA_COMPLETE',
    'review': 'REVIEW_COMPLETE',
    'fix': 'FIX_COMPLETE',
    'check': 'CHECK_COMPLETE',
    'reflect': 'REFLECT_COMPLETE',
}

PHASE_ORDER = [
    'expansion',
    'init',
    'planning',
    'execution',
    'qa',
    'review',
    'fix',
    'check',
    'reflect',
    'complete'
]


def get_project_dir() -> Path:
    """Get project directory from environment or current directory."""
    return Path(os.environ.get('CLAUDE_PROJECT_DIR', os.getcwd()))


def get_caw_dir() -> Path:
    """Get .caw directory path."""
    return get_project_dir() / '.caw'


def read_auto_state() -> Optional[Dict[str, Any]]:
    """Read auto-state.json if it exists."""
    state_file = get_caw_dir() / 'auto-state.json'
    if not state_file.exists():
        return None

    try:
        with open(state_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return None


def write_auto_state(state: Dict[str, Any]) -> bool:
    """Write auto-state.json."""
    state_file = get_caw_dir() / 'auto-state.json'

    try:
        # Ensure directory exists
        state_file.parent.mkdir(parents=True, exist_ok=True)

        with open(state_file, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2)
        return True
    except IOError:
        return False


def is_auto_active(state: Optional[Dict[str, Any]]) -> bool:
    """Check if auto mode is active."""
    if not state:
        return False
    return state.get('active', False)


def is_stale_state(state: Dict[str, Any], hours: int = 2) -> bool:
    """Check if state is stale (older than specified hours)."""
    started_at = state.get('started_at')
    if not started_at:
        return True

    try:
        start_time = datetime.fromisoformat(started_at.replace('Z', '+00:00'))
        now = datetime.now(start_time.tzinfo)
        return (now - start_time) > timedelta(hours=hours)
    except (ValueError, TypeError):
        return True


def get_expected_signal(phase: str) -> Optional[str]:
    """Get expected completion signal for current phase."""
    return PHASE_TO_SIGNAL.get(phase)


def get_next_phase(current_phase: str, config: Dict[str, Any]) -> str:
    """Get next phase based on current phase and config (skip flags)."""
    try:
        idx = PHASE_ORDER.index(current_phase)
    except ValueError:
        return 'complete'

    while idx < len(PHASE_ORDER) - 1:
        idx += 1
        next_phase = PHASE_ORDER[idx]

        # Check skip flags
        if next_phase == 'qa' and config.get('skip_qa'):
            continue
        if next_phase in ('review', 'fix', 'check') and config.get('skip_review'):
            continue
        if next_phase == 'reflect' and config.get('skip_reflect'):
            continue

        return next_phase

    return 'complete'


def detect_signal_in_transcript(signal: str) -> bool:
    """
    Check if a specific signal exists in recent conversation.

    Note: This is a simplified implementation.
    Full implementation would scan Claude's transcript files.
    For now, we rely on the signal being passed via stdin or environment.
    """
    pattern = SIGNAL_PATTERNS.get(signal)
    if not pattern:
        return False

    # Check stdin for recent transcript content
    transcript = os.environ.get('CLAUDE_TRANSCRIPT', '')
    if not transcript:
        # Try reading from stdin if available
        try:
            if not sys.stdin.isatty():
                transcript = sys.stdin.read()
        except Exception:
            pass

    return bool(pattern.search(transcript))


def generate_continuation_prompt(state: Dict[str, Any]) -> str:
    """Generate continuation prompt for blocked stop."""
    phase = state.get('phase', 'unknown')
    iteration = state.get('iteration', 0)
    max_iterations = state.get('max_iterations', 20)
    task = state.get('task_description', 'Unknown task')
    expected_signal = get_expected_signal(phase)
    config = state.get('config', {})
    next_phase = get_next_phase(phase, config)

    prompt = f"""## Auto Mode Continuation

The auto workflow is active but phase completion signal was not detected.

**Current State:**
- Phase: {phase}
- Iteration: {iteration}/{max_iterations}
- Task: {task}

**Expected Signal:** {expected_signal}

**Action Required:**
Continue working on the current phase. When complete, output:

```
---
SIGNAL: {expected_signal}
PHASE: {phase}
STATUS: complete
TIMESTAMP: {datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')}
NEXT: {next_phase}
---
```

If unable to complete, explain the blocker and output:

```
---
SIGNAL: PHASE_ERROR
PHASE: {phase}
STATUS: error
TIMESTAMP: {datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')}
ERROR: [brief description]
RECOVERABLE: true
---
```

Then request user guidance.
"""
    return prompt


def transition_to_next_phase(state: Dict[str, Any], detected_signal: str) -> Dict[str, Any]:
    """Transition state to next phase after signal detection."""
    current_phase = state.get('phase', 'expansion')
    config = state.get('config', {})
    next_phase = get_next_phase(current_phase, config)

    # Update phase data
    phase_data = state.get(current_phase, {})
    phase_data['signal_detected'] = True
    state[current_phase] = phase_data

    # Record signal detection
    signals = state.get('signals', {'detected_signals': []})
    signals['last_checked'] = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
    signals['detected_signals'].append({
        'signal': detected_signal,
        'detected_at': datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
    })
    state['signals'] = signals

    # Transition phase
    if next_phase == 'complete':
        state['phase'] = 'complete'
        state['active'] = False
        state['completed_at'] = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
        state['exit_reason'] = 'all_phases_complete'
    else:
        state['phase'] = next_phase
        state['iteration'] = 0  # Reset iteration for new phase

    return state


def check_auto_enforcement() -> Tuple[bool, str]:
    """
    Main enforcement check.

    Returns:
        (should_block, message)
        - should_block: True if stop should be blocked
        - message: Continuation prompt if blocked, empty otherwise
    """
    state = read_auto_state()

    # Not active - allow stop
    if not is_auto_active(state):
        return False, ''

    # Stale state - allow stop and deactivate
    if is_stale_state(state):
        state['active'] = False
        state['exit_reason'] = 'stale_state'
        write_auto_state(state)
        return False, ''

    # Already complete or failed - allow stop
    phase = state.get('phase', '')
    if phase in ('complete', 'failed'):
        return False, ''

    # Check iteration limit
    iteration = state.get('iteration', 0)
    max_iterations = state.get('max_iterations', 20)

    if iteration >= max_iterations:
        state['phase'] = 'failed'
        state['active'] = False
        state['exit_reason'] = 'max_iterations_reached'
        write_auto_state(state)
        return False, ''

    # Check for expected signal
    expected_signal = get_expected_signal(phase)

    if expected_signal and detect_signal_in_transcript(expected_signal):
        # Signal detected - transition to next phase
        state = transition_to_next_phase(state, expected_signal)
        write_auto_state(state)

        # If transitioned to complete, allow stop
        if state.get('phase') == 'complete':
            return False, ''

        # Otherwise, continue with next phase
        # Don't block, let next phase start naturally
        return False, ''

    # Check for AUTO_COMPLETE signal (final)
    if detect_signal_in_transcript('AUTO_COMPLETE'):
        state['phase'] = 'complete'
        state['active'] = False
        state['completed_at'] = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
        state['exit_reason'] = 'auto_complete_signal'
        write_auto_state(state)
        return False, ''

    # Check for error signal
    if detect_signal_in_transcript('PHASE_ERROR'):
        # Error detected - allow user to intervene
        return False, ''

    # No signal detected - block stop and inject continuation
    state['iteration'] = iteration + 1
    write_auto_state(state)

    continuation_prompt = generate_continuation_prompt(state)
    return True, continuation_prompt


def main():
    """Main entry point for Stop hook."""
    try:
        should_block, message = check_auto_enforcement()

        if should_block:
            # Output continuation prompt to stdout
            # The hook system will inject this as a prompt
            print(message)
            sys.exit(0)  # Exit 0 but with output means inject prompt
        else:
            # Allow stop - no output
            sys.exit(0)

    except Exception as e:
        # On error, allow stop rather than blocking indefinitely
        print(f"Auto enforcer error: {e}", file=sys.stderr)
        sys.exit(0)


if __name__ == '__main__':
    main()
