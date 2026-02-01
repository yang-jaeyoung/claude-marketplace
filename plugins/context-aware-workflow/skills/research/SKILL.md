---
name: research
description: Integrated research combining internal codebase analysis and external documentation
allowed-tools:
  - Read
  - Glob
  - Grep
  - WebSearch
  - WebFetch
  - Task
  - mcp__plugin_serena_serena__find_symbol
  - mcp__plugin_serena_serena__get_symbols_overview
  - mcp__plugin_serena_serena__find_referencing_symbols
  - mcp__plugin_serena_serena__search_for_pattern
  - mcp__plugin_serena_serena__read_file
  - mcp__plugin_serena_serena__list_dir
  - mcp__plugin_context7_context7__resolve-library-id
  - mcp__plugin_context7_context7__query-docs
forked-context: false
---

# Research Skill

Combines internal codebase exploration with external documentation research.

## Invocation

```bash
/cw:research "<topic>" [options]
```

## Workflow

### 1. Query Analysis
```yaml
Topic: [extracted]
Type: concept | implementation | comparison | troubleshooting
Scope: internal | external | both
Depth: shallow | normal | deep
```

### 2. Internal Research
```
[1] Symbol Search: Serena find_symbol with keywords
[2] Pattern Search: search_for_pattern for usage
[3] Reference Analysis: find_referencing_symbols
[4] Context: get_symbols_overview, read implementations
```

### 3. External Research
```
[1] Web Search: WebSearch for docs/articles
[2] Doc Fetch: WebFetch for detailed content
[3] Library Docs: Context7 for library-specific
```

### 4. Synthesis
```
[1] Compare: Internal vs recommended
[2] Recommendations: Priority-ordered
[3] Format: Structured markdown
```

## Output Format

```markdown
# Research: {Topic}

## Summary
Brief overview

## Internal Analysis
- File locations, key symbols, patterns
- Dependencies (external/internal)

## External Research
- Best practices
- Documentation sources

## Synthesis
| Aspect | Current | Recommended |
|--------|---------|-------------|

### Recommendations
1. 🔴 High: ...
2. 🟡 Medium: ...
3. 🟢 Nice to Have: ...
```

## Mode Integration

| Mode | Tools |
|------|-------|
| Standard | Task(Explore), Serena, Grep/Glob, WebSearch, Context7 |
| Deep | cw:planner-opus, comprehensive Serena, multi-source |

## Error Handling

| Error | Action |
|-------|--------|
| No internal results | Focus external, suggest terminology check |
| No external results | Try specific terms, check official docs |
| Rate limited | Wait 30s, use --depth shallow |

## Integration

```bash
/cw:research "auth patterns" --save auth-research
/cw:start "Implement OAuth" --research-context auth-research
```
