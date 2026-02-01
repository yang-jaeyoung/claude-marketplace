---
name: serena-sync
description: Bidirectional sync between CAW workflow state and Serena memory for cross-session persistence
allowed-tools: Read, Write, Glob
mcp_servers:
  - serena
---

# Serena Sync Skill

Bidirectional synchronization between CAW and Serena MCP memory.

## Purpose

1. **Persist**: Save insights, knowledge, lessons to Serena
2. **Restore**: Load saved knowledge in new sessions
3. **Merge**: Handle conflicts when both have updates

## Memory Schema

| Memory | Content | Updated By |
|--------|---------|------------|
| project_onboarding | Frameworks, conventions, key files | Bootstrapper |
| domain_knowledge | Business rules, patterns | Planner, Builder |
| lessons_learned | Debug insights, gotchas | Builder |
| workflow_patterns | Best practices | Reflect skill |
| session_backup | Session state backup | Session Persister |

## Operations

### To Serena (`--to-serena`)
```
.caw/knowledge/** → domain_knowledge
.caw/insights/** → caw_insights (persistent only)
.caw/learnings.md → lessons_learned
CLAUDE.md (Lessons) → lessons_learned (append)
```

### From Serena (`--from-serena`)
```
project_onboarding → context_manifest.json
domain_knowledge → .caw/knowledge/from_serena.md
lessons_learned → .caw/learnings.md (merge)
workflow_patterns → .caw/knowledge/patterns.md
```

### Bidirectional (default)
```
1. Compare timestamps
2. Apply newer_wins strategy
3. Sync both directions
```

### Status (`--status`)
```
| Category | CAW | Serena | State |
|----------|-----|--------|-------|
| Domain | 01-15 14:30 | 01-14 10:00 | CAW newer |
| Lessons | 01-14 09:00 | 01-15 16:00 | Serena newer |
```

## Conflict Resolution

| Strategy | Behavior |
|----------|----------|
| newer_wins | Most recent timestamp wins (default) |
| merge | Combine unique entries from both |
| manual | Ask user to resolve |

## Usage

```bash
/cw:sync                    # Bidirectional
/cw:sync --to-serena        # Upload to Serena
/cw:sync --from-serena      # Restore from Serena
/cw:sync --status           # Check state
/cw:sync --to-serena --force # Overwrite
```

## Output

```
## Serena Sync Complete

Uploaded: domain_knowledge (2.1KB), lessons_learned (1.5KB)
Downloaded: workflow_patterns (3.2KB)

Total: 3 memories | Duration: 1.2s
```

## Error Handling

| Scenario | Action |
|----------|--------|
| Serena unavailable | Local-only mode, warn user |
| Memory not found | Create new |
| Parse error | Skip, continue |
| Write failure | Retry once |
