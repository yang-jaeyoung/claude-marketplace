---
description: Synchronize CAW workflow state with Serena memory for cross-session persistence
argument-hint: "[--to-serena | --from-serena | --status]"
---

# /cw:sync - Serena Memory Synchronization

Synchronize CAW workflow knowledge with Serena MCP memory for cross-session persistence.

## Usage

```bash
/cw:sync                        # Bidirectional (default)
/cw:sync --to-serena            # Upload to Serena
/cw:sync --from-serena          # Restore from Serena
/cw:sync --status               # Check sync status
/cw:sync --force                # Overwrite without merge
/cw:sync --category domain_knowledge  # Specific category
```

## Flags

| Flag | Description |
|------|-------------|
| `--to-serena` | Upload CAW knowledge |
| `--from-serena` | Download from Serena |
| `--status` | Show sync status |
| `--force` | Overwrite without merge |
| `--category <name>` | Sync specific category |

## Memory Categories

| Category | CAW Source | Serena Memory |
|----------|------------|---------------|
| Domain Knowledge | `.caw/knowledge/**` | `domain_knowledge` |
| Lessons Learned | `.caw/learnings.md` | `lessons_learned` |
| Workflow Patterns | `.caw/knowledge/patterns.md` | `workflow_patterns` |
| Project Context | `context_manifest.json` | `project_onboarding` |
| Insights | `.caw/insights/**` | `caw_insights` |

## Behavior

### Bidirectional (Default)

1. Compare timestamps (CAW files vs Serena memories)
2. Apply `newer_wins` strategy
3. Merge unique entries
4. Sync both directions

### Upload (`--to-serena`)

```
write_memory("domain_knowledge", content)
write_memory("lessons_learned", content)
```

### Restore (`--from-serena`)

```
read_memory("domain_knowledge") → .caw/knowledge/
read_memory("lessons_learned") → .caw/learnings.md
```

## Output

```
## Serena Sync Status

| Category | CAW Modified | Serena Modified | Status |
|----------|--------------|-----------------|--------|
| domain_knowledge | 2024-01-15 14:30 | 2024-01-14 10:00 | CAW newer |
| lessons_learned | 2024-01-14 09:00 | 2024-01-15 16:00 | Serena newer |

## Sync Complete
  Uploaded: 2 | Downloaded: 1 | Duration: 1.2s
```

## When to Use

| Scenario | Command |
|----------|---------|
| End of session | `--to-serena` |
| Start of session | `--from-serena` |
| Regular check | `--status` |
| After discoveries | `--to-serena` |

## Error Handling

| Error | Solution |
|-------|----------|
| Serena not available | Check MCP configuration |
| Memory not found | Will be created |
| Conflict detected | Use `--force` or manual merge |

## Integration

- `/cw:init` - Checks Serena for onboarding
- `/cw:reflect` - Can trigger sync after Ralph Loop
- SessionEnd hook - Auto-sync if configured
