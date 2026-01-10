---
name: context-manager
description: Manage and optimize context window usage through file analysis, packing, and pruning
allowed-tools: Read, Glob, Grep, Bash
forked-context: false
---

# Context Manager Skill

Provides utilities for managing context window usage in long-running sessions.

## Capabilities

### Plan Detection (`detect_plan.py`)
- Extract titles from plan documents
- Calculate completion rates from checkbox items
- Extract file references from content
- Count completed/pending steps
- Format timestamps as human-readable "time ago"

### Context Packing (`pack_context.py`)
- Extract TypeScript/JavaScript interfaces and signatures
- Extract Python function/class signatures
- Generate compact context representations

### Context Pruning (`prune_context.py`)
- Analyze file staleness based on access patterns
- Determine which files to keep, pack, or prune
- Generate recommendations based on current task plan

## Usage

This skill provides Python utilities that can be used by other skills
or invoked directly for context optimization tasks.

```python
from detect_plan import extract_title, calculate_completion
from pack_context import extract_typescript_interfaces
from prune_context import analyze_files
```

## Integration

Used by:
- Session Persister skill for session state analysis
- Progress Tracker skill for completion tracking
- Quality Gate skill for context health checks
