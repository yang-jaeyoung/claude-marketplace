# Auto Mode Signal Instructions

When invoked during `/cw:auto` workflow, agents MUST output completion signals to enable automatic phase transitions.

## Signal Format

Output this exact block when your phase work is complete:

```
---
SIGNAL: [SIGNAL_NAME]
PHASE: [current_phase]
STATUS: complete
TIMESTAMP: [ISO8601 format: YYYY-MM-DDTHH:MM:SSZ]
NEXT: [next_phase]
---
```

## Agent-Specific Signals

### Analyst Agent (Expansion Phase)
```
---
SIGNAL: EXPANSION_COMPLETE
PHASE: expansion
STATUS: complete
TIMESTAMP: 2024-01-15T10:15:00Z
NEXT: init
---
```

### Bootstrapper Agent (Init Phase)
```
---
SIGNAL: INIT_COMPLETE
PHASE: init
STATUS: complete
TIMESTAMP: 2024-01-15T10:20:00Z
NEXT: planning
---
```

### Planner Agent (Planning Phase)
```
---
SIGNAL: PLANNING_COMPLETE
PHASE: planning
STATUS: complete
TIMESTAMP: 2024-01-15T10:25:00Z
NEXT: execution
---
```

### Builder Agent (Execution Phase)
When ALL steps are complete:
```
---
SIGNAL: EXECUTION_COMPLETE
PHASE: execution
STATUS: complete
TIMESTAMP: 2024-01-15T10:45:00Z
NEXT: qa
---
```

### QA Loop (QA Phase)
When tests pass:
```
---
SIGNAL: QA_COMPLETE
PHASE: qa
STATUS: complete
TIMESTAMP: 2024-01-15T10:50:00Z
NEXT: review
---
```

### Reviewer Agent (Review Phase)
```
---
SIGNAL: REVIEW_COMPLETE
PHASE: review
STATUS: complete
TIMESTAMP: 2024-01-15T10:55:00Z
NEXT: fix
---
```

### Fixer Agent (Fix Phase)
```
---
SIGNAL: FIX_COMPLETE
PHASE: fix
STATUS: complete
TIMESTAMP: 2024-01-15T11:00:00Z
NEXT: check
---
```

### ComplianceChecker Agent (Check Phase)
```
---
SIGNAL: CHECK_COMPLETE
PHASE: check
STATUS: complete
TIMESTAMP: 2024-01-15T11:05:00Z
NEXT: reflect
---
```

### Ralph Loop (Reflect Phase)
```
---
SIGNAL: REFLECT_COMPLETE
PHASE: reflect
STATUS: complete
TIMESTAMP: 2024-01-15T11:10:00Z
NEXT: complete
---
```

### Final Completion
After all phases:
```
---
SIGNAL: AUTO_COMPLETE
PHASE: complete
STATUS: complete
TIMESTAMP: 2024-01-15T11:10:00Z
NEXT: none
---
```

## When to Output

1. **Output signal ONLY when phase work is genuinely complete**
2. **Output signal as the LAST thing in your response**
3. **Include accurate timestamp in ISO8601 format**
4. **Specify correct NEXT phase based on workflow**

## Error Signal

If unable to complete phase:

```
---
SIGNAL: PHASE_ERROR
PHASE: [current_phase]
STATUS: error
TIMESTAMP: [ISO8601]
ERROR: [brief description]
RECOVERABLE: true/false
---
```

## Detection Context

The Stop hook enforcer scans for these signals to:
1. Determine if current phase is complete
2. Transition to next phase automatically
3. Inject continuation prompt if signal not found
4. Track progress in `.caw/auto-state.json`

## Important Notes

1. **Signal is case-sensitive** - Use exact SIGNAL names
2. **Block format required** - Use `---` delimiters
3. **Don't output mid-phase** - Only at genuine completion
4. **Include all fields** - Missing fields may cause detection failure
