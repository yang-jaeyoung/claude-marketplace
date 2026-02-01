---
description: Evolve high-confidence instincts into reusable commands, skills, or agents
argument-hint: "[--preview|--create <type>] [--id <instinct-id>]"
allowed-tools: Read, Write, Glob, Bash
---

# /cw:evolve - Instinct Evolution System

Transform learned instincts into reusable commands, skills, or agents.

## Overview

The evolve command analyzes accumulated instincts and proposes evolution paths:
- **Command**: User-invoked workflows (3+ steps)
- **Skill**: Auto-applied patterns (behavioral rules)
- **Agent**: Complex multi-step processes (specialized reasoning)

## Usage

```bash
/cw:evolve                    # Interactive: preview and select
/cw:evolve --preview          # Preview candidates only
/cw:evolve --create command   # Create command from selected
/cw:evolve --create skill     # Create skill from selected
/cw:evolve --create agent     # Create agent from selected
/cw:evolve --id <instinct-id> # Evolve specific instinct
```

## Execution Protocol

### Phase 1: Load Evolution Candidates

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/insight-collector/scripts/instinct-cli.py" list
```

Extract instincts with confidence >= 0.6.

### Phase 2: Classify Candidates

| Pattern | Evolution Type |
|---------|---------------|
| User-triggered + 3+ steps | **Command** |
| Context-triggered + auto-apply | **Skill** |
| Complex reasoning + decision points | **Agent** |
| Simple preference | **None** (keep as instinct) |

**Classification Keywords:**
- Command: "when user asks", "on request"
- Skill: "when editing", "before commit", "after"
- Agent: "analyze", "diagnose", "investigate"

### Phase 3: Present Candidates

```
=== Instinct Evolution Candidates ===

## Command Candidates
1. [id-1] (0.85, 12 evidence) → /cw:safe-modify

## Skill Candidates
2. [id-2] (0.72, 15 evidence) → pre-commit-quality

## Agent Candidates
3. [id-3] (0.80, 10 evidence) → debug-detective

Select an instinct to evolve (ID) or 'q' to quit:
```

### Phase 4: Generate Scaffolding

Generates to `.caw/evolved/{type}/{name}.md` with:
- Origin metadata (source instinct, confidence, evidence)
- Workflow/behavioral rules from instinct
- Boundaries (will/will not)

**Output locations:**
- Commands: `.caw/evolved/commands/{name}.md`
- Skills: `.caw/evolved/skills/{name}/SKILL.md`
- Agents: `.caw/evolved/agents/{name}.md`

### Phase 5: Update Tracking

Adds evolution record to `.caw/instincts/index.json`:
```json
{
  "evolutions": [{
    "source_instinct": "id",
    "evolution_type": "command",
    "target_path": ".caw/evolved/commands/name.md"
  }]
}
```

## Classification Examples

| Instinct | Type | Rationale |
|----------|------|-----------|
| "Grep → Edit → Verify" on user request | Command | User-triggered, 3 steps |
| "Check debug statements before commit" | Skill | Context-triggered, auto |
| "Trace → Bisect → Analyze → Fix" | Agent | Complex reasoning |

## Flags

| Flag | Description |
|------|-------------|
| `--preview` | Show candidates without generating |
| `--create <type>` | Force creation type |
| `--id <id>` | Evolve specific instinct directly |

## Implementation Guidelines

1. Check `.caw/instincts/index.json` exists first
2. Use `python3` explicitly (cross-platform)
3. Confidence threshold: >= 0.6
4. Generate kebab-case names
5. Preserve instinct metadata in generated files

## Boundaries

**Will:**
- Analyze and classify instincts
- Generate scaffolding with metadata
- Track evolution history

**Will Not:**
- Evolve low-confidence instincts (< 0.6)
- Overwrite existing without confirmation
- Delete source instincts

## Error Handling

| Error | Resolution |
|-------|-----------|
| No instincts found | Run instinct analysis first |
| No high-confidence | Continue gathering observations |
| ID not found | List available IDs |
| Target exists | Ask to overwrite or rename |

## Related

- `instinct-cli.py analyze/list/show` - Manage instincts
- `/cw:status` - Shows evolved components
- `/cw:sync` - Sync to Serena memory
