---
description: Synchronize CAW workflow state with Serena memory for cross-session persistence
argument-hint: "[--to-serena | --from-serena | --status]"
---

# /caw:sync - Serena Memory Synchronization

Synchronize CAW workflow knowledge with Serena MCP memory system for cross-session persistence.

## Usage

```bash
# Bidirectional sync (default)
/caw:sync

# Upload CAW knowledge to Serena
/caw:sync --to-serena

# Restore knowledge from Serena
/caw:sync --from-serena

# Check current sync status
/caw:sync --status

# Force overwrite without merge
/caw:sync --to-serena --force
/caw:sync --from-serena --force

# Sync specific category only
/caw:sync --category domain_knowledge
/caw:sync --category lessons_learned
```

## Flags

| Flag | Description |
|------|-------------|
| `--to-serena` | Upload CAW knowledge to Serena memory |
| `--from-serena` | Download and restore from Serena memory |
| `--status` | Show current sync status without making changes |
| `--force` | Overwrite without merge (use with caution) |
| `--category <name>` | Sync only specified category |
| `--verbose` | Show detailed sync operations |

## Behavior

### Default Bidirectional Sync

When invoked without flags:

1. **Check both sources**:
   - Read CAW files timestamps (`.caw/knowledge/`, `.caw/insights/`, `.caw/learnings.md`)
   - Call `list_memories()` to get Serena memory list

2. **Compare and merge**:
   - Apply `newer_wins` strategy for each category
   - Merge content when both have unique entries

3. **Sync both directions**:
   - Upload newer CAW content to Serena
   - Download newer Serena content to CAW

### Upload to Serena (`--to-serena`)

1. Read all CAW knowledge files
2. Aggregate by category
3. Call Serena MCP tools:
   ```
   write_memory("domain_knowledge", aggregated_domain_content)
   write_memory("lessons_learned", aggregated_lessons)
   write_memory("workflow_patterns", aggregated_patterns)
   ```
4. Report upload summary

### Restore from Serena (`--from-serena`)

1. Call `list_memories()` to check available
2. For each relevant memory:
   ```
   read_memory("domain_knowledge") → .caw/knowledge/from_serena.md
   read_memory("lessons_learned") → .caw/learnings.md (merge)
   read_memory("workflow_patterns") → .caw/knowledge/patterns.md
   ```
3. Report restoration summary

### Status Check (`--status`)

1. Read CAW file timestamps
2. Call Serena `list_memories()` for metadata
3. Compare and report status table
4. Suggest actions if out of sync

## Memory Categories

| Category | CAW Source | Serena Memory |
|----------|------------|---------------|
| Domain Knowledge | `.caw/knowledge/**` | `domain_knowledge` |
| Lessons Learned | `.caw/learnings.md`, CLAUDE.md | `lessons_learned` |
| Workflow Patterns | `.caw/knowledge/patterns.md` | `workflow_patterns` |
| Project Context | `context_manifest.json` | `project_onboarding` |
| Insights | `.caw/insights/**` (persistent) | `caw_insights` |

## Output Examples

### Sync Status

```markdown
## Serena Sync Status

| Category | CAW Last Modified | Serena Last Modified | Status |
|----------|-------------------|----------------------|--------|
| domain_knowledge | 2024-01-15 14:30 | 2024-01-14 10:00 | CAW newer |
| lessons_learned | 2024-01-14 09:00 | 2024-01-15 16:00 | Serena newer |
| workflow_patterns | Not found | 2024-01-10 08:00 | Serena only |
| project_onboarding | 2024-01-15 08:00 | 2024-01-15 08:00 | In sync |

**Recommendation**:
- Run `/caw:sync` to synchronize all
- Or `/caw:sync --from-serena --category workflow_patterns` for specific
```

### Successful Sync

```markdown
## Serena Sync Complete

### Uploaded to Serena
| Memory | Size | Action |
|--------|------|--------|
| domain_knowledge | 2.1 KB | Updated |
| lessons_learned | 1.5 KB | Merged |

### Downloaded from Serena
| Memory | Size | Action |
|--------|------|--------|
| workflow_patterns | 3.2 KB | Restored |

**Summary**:
- 3 categories synchronized
- 2 uploads, 1 download
- Duration: 1.2s
```

### Sync with Errors

```markdown
## Serena Sync Partial

### Successful
| Category | Direction | Status |
|----------|-----------|--------|
| domain_knowledge | CAW → Serena | Updated |

### Failed
| Category | Error | Action |
|----------|-------|--------|
| lessons_learned | Parse error | Skipped |

**Recommendation**:
- Check `.caw/learnings.md` format
- Retry with `/caw:sync --category lessons_learned`
```

## When to Use

| Scenario | Command |
|----------|---------|
| End of work session | `/caw:sync --to-serena` |
| Start of new session | `/caw:sync --from-serena` |
| Regular sync check | `/caw:sync --status` |
| Full bidirectional sync | `/caw:sync` |
| After major discoveries | `/caw:sync --to-serena` |
| Team knowledge share | `/caw:sync --to-serena` |

## Integration

- **serena-sync skill**: This command invokes the serena-sync skill
- **/caw:init**: Automatically checks Serena for onboarding
- **/caw:reflect**: Can trigger sync after Ralph Loop completion
- **SessionEnd hook**: Can auto-sync on session end (if configured)

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| "Serena not available" | MCP server not running | Check Serena MCP configuration |
| "Memory not found" | First sync for this project | Content will be created |
| "Parse error" | Invalid CAW file format | Fix file format, retry |
| "Conflict detected" | Both sides modified | Use `--force` or manual merge |

## Best Practices

1. **Sync regularly**: Run `/caw:sync --status` to check sync state
2. **Before major changes**: Sync to Serena as backup
3. **After learning**: Sync lessons immediately
4. **New session**: Check for Serena context first
5. **Team projects**: Sync to share domain knowledge
