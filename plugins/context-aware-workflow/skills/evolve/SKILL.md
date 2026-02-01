---
name: evolve
description: Transform high-confidence instincts into reusable commands, skills, or agents
allowed-tools: Read, Write, Glob, Bash
---

# Evolve Skill

Transform instincts (confidence ≥0.6) into production-ready components.

## Usage

```bash
/cw:evolve                              # Interactive preview and selection
/cw:evolve --preview                    # Show candidates only
/cw:evolve --id <instinct-id>           # Show details
/cw:evolve --create <type> <id> <name>  # Generate evolution
```

## Evolution Types

| Type | Trigger | Use Case |
|------|---------|----------|
| `command` | User-invoked | Multi-step workflows (3+ steps) |
| `skill` | Auto-activated | Behavioral rules, context-based |
| `agent` | Complex reasoning | Decision trees, specialized analysis |

## Workflow

### 1. Load Candidates

```python
from integration import list_instincts
from evolution import get_evolution_candidates_list

instincts = list_instincts(min_confidence=0.6)
candidates = get_evolution_candidates_list(instincts)
```

### 2. Classification Logic

```yaml
Command: trigger_keywords: ["when user", "on request"], min_steps: 3
Skill: trigger_keywords: ["before", "after", "automatically"], auto_activation: true
Agent: trigger_keywords: ["analyze", "diagnose"], reasoning_required: true
```

### 3. Display Candidates

```
📦 COMMANDS
ID: safe-modify-abc12345
   Trigger: "when user requests safe modification"
   Confidence: 0.85 | Evidence: 12
   → /cw:safe-modify

📋 SKILLS
ID: pre-commit-quality-def67890
   Trigger: "before git commit"
   Confidence: 0.72 | Evidence: 15
   → pre-commit-quality skill

🤖 AGENTS
ID: debug-detective-ghi34567
   Trigger: "complex debugging"
   Confidence: 0.80 | Evidence: 10
   → debug-detective agent
```

### 4. Create Evolution

```python
from evolution import create_evolution, track_evolution

result = create_evolution(instinct, '<type>', '<name>')
if result['success']:
    track_evolution(instinct['id'], result['type'], result['path'], ...)
```

## Generated Scaffolds

Output locations:
- Commands: `.caw/evolved/commands/{name}.md`
- Skills: `.caw/evolved/skills/{name}/SKILL.md`
- Agents: `.caw/evolved/agents/{name}.md`

Each scaffold includes:
- Origin metadata (source instinct, confidence, evidence)
- Workflow steps from action patterns
- Usage examples and boundaries

## State Management

Tracked in `.caw/instincts/index.json`:
```json
{
  "evolutions": [{
    "timestamp": "2026-01-27T20:00:00Z",
    "source_instinct": "safe-modify-abc12345",
    "confidence": 0.85,
    "evolution_type": "command",
    "target_path": ".caw/evolved/commands/safe-modify.md"
  }]
}
```

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| No instincts | None captured yet | Work normally, run `/cw:evolve` later |
| Invalid ID | ID not found | Use `/cw:evolve --preview` for valid IDs |
| Low confidence | < 0.6 | Continue working to build evidence |
| File exists | Target path occupied | Use different name or `--force` |
| Invalid type | Not command/skill/agent | Check valid types above |

## Boundaries

**Will:** Analyze instincts, classify by type, generate scaffolds, track history, preserve source
**Won't:** Evolve low-confidence (<0.6), auto-overwrite, delete sources, deploy globally
