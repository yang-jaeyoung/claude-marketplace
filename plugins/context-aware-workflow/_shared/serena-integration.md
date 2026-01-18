# Serena MCP Integration Guide

This document defines how CAW integrates with Serena MCP for enhanced code analysis and cross-session knowledge persistence.

## Overview

CAW uses Serena MCP for two main purposes:

1. **Code Analysis**: Symbol-based navigation, precise code editing
2. **Knowledge Persistence**: Cross-session memory for project context

```
┌─────────────────────────────────────────────────────────────┐
│                     Serena MCP Layer                         │
│  ┌─────────────────┐  ┌─────────────────┐                   │
│  │  Memory System   │  │  Symbol Tools   │                   │
│  │  - write_memory  │  │  - find_symbol  │                   │
│  │  - read_memory   │  │  - replace_body │                   │
│  │  - list_memories │  │  - insert_*     │                   │
│  └────────┬────────┘  └────────┬────────┘                   │
│           │                    │                             │
└───────────┼────────────────────┼─────────────────────────────┘
            │                    │
┌───────────┼────────────────────┼─────────────────────────────┐
│           ▼                    ▼                             │
│  ┌─────────────────┐  ┌─────────────────┐                   │
│  │  Bootstrapper   │  │     Builder     │                   │
│  │  - onboarding   │  │  - symbol edit  │                   │
│  │  - context load │  │  - lessons save │                   │
│  └─────────────────┘  └─────────────────┘                   │
│                                                              │
│  ┌─────────────────┐  ┌─────────────────┐                   │
│  │    Planner      │  │   serena-sync   │                   │
│  │  - domain read  │  │  - bidirectional│                   │
│  │  - knowledge    │  │  - merge/sync   │                   │
│  └─────────────────┘  └─────────────────┘                   │
│                                                              │
│                      CAW Workflow Layer                      │
└──────────────────────────────────────────────────────────────┘
```

## Memory Naming Convention

### Standard Memory Names

| Memory Name | Content Type | Primary Writer | Readers |
|-------------|--------------|----------------|---------|
| `project_onboarding` | Project metadata | Bootstrapper | All agents |
| `domain_knowledge` | Business rules, patterns | Planner, Builder | All agents |
| `lessons_learned` | Debug insights, gotchas | Builder | All agents |
| `workflow_patterns` | Successful approaches | Reflect skill | Planner |
| `caw_insights` | Persistent insights | Insight Collector | All agents |
| `session_backup` | Session state backup | Session Persister | Bootstrapper |

### Memory Content Guidelines

1. **Keep it concise**: Each memory should be <50KB
2. **Use markdown format**: For readability and structure
3. **Include timestamps**: For conflict resolution
4. **Avoid secrets**: Never store API keys, passwords, tokens

### Memory Format Template

```markdown
# [Memory Name]

## Metadata
- **Last Updated**: YYYY-MM-DDTHH:MM:SSZ
- **Version**: 1.0
- **Source**: [Agent/Skill name]

## Content

[Structured content here]

## History
- YYYY-MM-DD: Initial creation
- YYYY-MM-DD: Updated by [agent]
```

## Symbol-Based Editing Guidelines

### When to Use Symbol Tools

| Scenario | Tool | Example |
|----------|------|---------|
| Find a function/class | `find_symbol` | Find `processPayment` method |
| Replace entire function | `replace_symbol_body` | Rewrite `validateInput` |
| Add new method to class | `insert_after_symbol` | Add method after constructor |
| Add import statement | `insert_before_symbol` | Add import before first symbol |
| Partial modification | `replace_content` (regex) | Change variable name in function |

### Symbol Editing Priority

Builder should prefer Serena tools in this order:

1. **`find_symbol`** - Locate the exact symbol to modify
   ```
   find_symbol("UserService/validateEmail", include_body=True)
   ```

2. **`replace_symbol_body`** - Replace entire function/method
   ```
   replace_symbol_body("validateEmail", "src/services/user.ts", new_body)
   ```

3. **`insert_after_symbol` / `insert_before_symbol`** - Add new code
   ```
   insert_after_symbol("constructor", "src/services/user.ts", new_method)
   ```

4. **`replace_content`** with regex - Partial modifications within symbol
   ```
   replace_content("src/services/user.ts", "oldVar", "newVar", mode="literal")
   ```

### Symbol Path Patterns

```
# Simple name (matches any symbol with that name)
"validateEmail"

# Relative path (matches suffix)
"UserService/validateEmail"

# Absolute path (exact match within file)
"/UserService/validateEmail"

# With overload index (for overloaded methods)
"UserService/process[0]"
```

## Agent-Specific Integration

### Bootstrapper

**Serena Tools Used**:
- `check_onboarding_performed()` - Check for existing context
- `read_memory("project_onboarding")` - Restore context
- `write_memory("project_onboarding", ...)` - Save context
- `list_memories()` - Check available memories

**Workflow**:
```
1. check_onboarding_performed()
   ├─ Exists → read_memory("project_onboarding")
   │           → Pre-populate context_manifest.json
   │           → Skip redundant detection
   └─ Not exists → Full detection
                   → write_memory("project_onboarding", result)
```

### Planner

**Serena Tools Used**:
- `read_memory("domain_knowledge")` - Load business rules
- `read_memory("lessons_learned")` - Load known gotchas
- `find_symbol` - Understand code structure
- `get_symbols_overview` - File structure analysis
- `write_memory("domain_knowledge", ...)` - Save discovered rules

**Knowledge Retrieval Order**:
```
1. Serena Memory (read_memory)
2. CAW Knowledge Base (.caw/knowledge/)
3. Codebase Search (Grep/Glob)
4. User Question (AskUserQuestion)
```

### Builder

**Serena Tools Used**:
- `find_symbol` - Locate code to modify
- `replace_symbol_body` - Replace function/method
- `insert_after_symbol` - Add new code
- `find_referencing_symbols` - Check dependencies
- `write_memory("lessons_learned", ...)` - Save debug insights

**TDD with Symbols**:
```
1. find_symbol("existingTest") → Understand test pattern
2. Write new test using same pattern
3. find_symbol("targetFunction") → Get current implementation
4. replace_symbol_body → Update implementation
5. Run tests → Verify
6. If hard debugging → write_memory("lessons_learned", lesson)
```

## Sync Workflows

### Session Start
```
SessionStart Hook triggered
  │
  ├─ check_onboarding_performed()
  │   └─ If exists: read_memory("project_onboarding")
  │
  ├─ list_memories()
  │   └─ Report available: domain_knowledge, lessons_learned, etc.
  │
  └─ Offer to restore context
```

### Session End
```
Before session ends (or via /cw:sync)
  │
  ├─ Collect CAW knowledge
  │   ├─ .caw/knowledge/**
  │   ├─ .caw/insights/** (persistent)
  │   └─ .caw/learnings.md
  │
  ├─ write_memory for each category
  │
  └─ Report sync status
```

### On-Demand Sync
```
/cw:sync
  │
  ├─ Compare timestamps (CAW vs Serena)
  │
  ├─ Apply newer_wins strategy
  │
  ├─ Sync both directions
  │
  └─ Report changes
```

## Error Handling

### Serena Unavailable

When Serena MCP is not available:

```
1. Log warning: "Serena MCP not available, using local-only mode"
2. Fall back to .caw/ file-based operations
3. Continue workflow without Serena features
4. On next session, attempt reconnection
```

### Memory Not Found

```
1. If reading: Return empty/default, log info
2. If writing: Create new memory
3. Report to user in summary
```

### Symbol Not Found

```
1. Broaden search with substring_matching=True
2. Try search_for_pattern for regex-based search
3. If still not found, report and ask user
```

## Best Practices

### Do's
- Check Serena availability before critical operations
- Use memory for cross-session persistent knowledge only
- Prefer symbol tools over text-based search for code
- Save lessons immediately after debugging
- Keep memories organized and timestamped

### Don'ts
- Don't store large files in memory (>50KB)
- Don't store sensitive information (secrets, tokens)
- Don't rely solely on Serena (have fallback)
- Don't use memory for temporary/session-specific data
- Don't skip validation after symbol edits

## Configuration

### Enabling Serena for an Agent

In agent frontmatter:
```yaml
mcp_servers:
  - serena
```

### Memory Persistence Settings

In `.claude/caw.local.md`:
```yaml
serena:
  auto_sync: true          # Sync on session end
  sync_interval: 30        # Minutes between auto-syncs
  max_memory_size: 50000   # Bytes per memory
  backup_session: true     # Backup session state to Serena
```

## Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| "check_onboarding_performed failed" | Serena not configured | Check MCP server settings |
| "Memory too large" | Content exceeds limit | Summarize or split content |
| "Symbol not found" | Wrong path pattern | Use substring_matching, check file path |
| "Sync conflict" | Both sides modified | Use --force or manual merge |
| "Parse error" | Invalid memory format | Check markdown structure |
