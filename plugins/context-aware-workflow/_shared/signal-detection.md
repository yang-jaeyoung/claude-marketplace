# Signal Detection System

Signal-based phase detection for `/cw:auto` workflow. Signals enable automatic phase transitions and persistence enforcement.

## Signal Patterns

Each phase outputs a completion signal when finished. The Stop hook enforcer detects these signals in the transcript to determine workflow state.

### Signal Definitions

| Phase | Signal | Description |
|-------|--------|-------------|
| Expansion | `EXPANSION_COMPLETE` | Requirements analysis finished |
| Init | `INIT_COMPLETE` | .caw/ environment initialized |
| Planning | `PLANNING_COMPLETE` | task_plan.md generated |
| Execution | `EXECUTION_COMPLETE` | All steps executed |
| QA | `QA_COMPLETE` | QA loop passed |
| Review | `REVIEW_COMPLETE` | Code review finished |
| Fix | `FIX_COMPLETE` | Auto-fixes applied |
| Check | `CHECK_COMPLETE` | Compliance validated |
| Reflect | `REFLECT_COMPLETE` | Ralph Loop completed |
| Final | `AUTO_COMPLETE` | Full workflow finished |

### Transition Signals

| Signal | Description |
|--------|-------------|
| `TRANSITION_TO_QA` | Execution done, start QA |
| `TRANSITION_TO_VALIDATION` | QA done, start parallel validation |
| `TRANSITION_TO_FIX` | Review done, start fixing |

## Signal Format

Agents MUST output signals in this exact format:

```
---
SIGNAL: [SIGNAL_NAME]
PHASE: [current_phase]
STATUS: complete
TIMESTAMP: [ISO8601]
NEXT: [next_phase or 'none']
---
```

### Example

```
---
SIGNAL: PLANNING_COMPLETE
PHASE: planning
STATUS: complete
TIMESTAMP: 2024-01-15T10:30:00Z
NEXT: execution
---
```

## Detection Logic

### Python Implementation (for hooks)

```python
import re
from typing import Optional, Dict
from pathlib import Path
from datetime import datetime

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

def get_next_phase(current_phase: str, config: Dict) -> Optional[str]:
    """Get next phase based on current phase and config (skip flags)."""
    idx = PHASE_ORDER.index(current_phase)

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

def detect_signal(transcript: str, signal: str) -> bool:
    """Check if a specific signal exists in transcript."""
    pattern = SIGNAL_PATTERNS.get(signal)
    if not pattern:
        return False
    return bool(pattern.search(transcript))

def detect_any_signal(transcript: str) -> Optional[str]:
    """Scan transcript for any completion signal."""
    for signal, pattern in SIGNAL_PATTERNS.items():
        if pattern.search(transcript):
            return signal
    return None

def get_expected_signal(phase: str) -> Optional[str]:
    """Get the expected completion signal for current phase."""
    return PHASE_TO_SIGNAL.get(phase)
```

## Agent Instructions

### Required Output

All CAW agents invoked during `/cw:auto` MUST include the signal block when completing their work:

```markdown
## Agent Completion Requirement

When you have successfully completed your phase work:

1. Output the completion signal block
2. Ensure SIGNAL field matches expected signal for your phase
3. Include accurate TIMESTAMP in ISO8601 format
4. Specify NEXT phase (or 'none' for final)

Example for Builder completing execution:
\`\`\`
---
SIGNAL: EXECUTION_COMPLETE
PHASE: execution
STATUS: complete
TIMESTAMP: 2024-01-15T10:45:00Z
NEXT: qa
---
\`\`\`
```

### Error Handling

If a phase cannot complete:

```
---
SIGNAL: PHASE_ERROR
PHASE: [current_phase]
STATUS: error
TIMESTAMP: [ISO8601]
ERROR: [brief error description]
RECOVERABLE: [true/false]
---
```

## Persistence Enforcement

When Stop hook detects auto mode is active but expected signal not found:

1. Increment iteration counter
2. Check max_iterations limit
3. If under limit: inject continuation prompt
4. If over limit: transition to 'failed' state

### Continuation Prompt Template

```markdown
## Auto Mode Continuation

The auto workflow is active but phase completion signal was not detected.

**Current State:**
- Phase: {phase}
- Iteration: {iteration}/{max_iterations}
- Task: {task_description}

**Expected Signal:** {expected_signal}

**Action Required:**
Continue working on the current phase. When complete, output:

\`\`\`
---
SIGNAL: {expected_signal}
PHASE: {phase}
STATUS: complete
TIMESTAMP: [current time ISO8601]
NEXT: {next_phase}
---
\`\`\`

If unable to complete, explain the blocker and request user guidance.
```

## State File Integration

Signal detection updates `.caw/auto-state.json`:

```json
{
  "signals": {
    "last_checked": "2024-01-15T10:30:00Z",
    "detected_signals": [
      {
        "signal": "EXPANSION_COMPLETE",
        "detected_at": "2024-01-15T10:15:00Z"
      },
      {
        "signal": "INIT_COMPLETE",
        "detected_at": "2024-01-15T10:20:00Z"
      }
    ]
  }
}
```

