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

Comprehensive research skill that combines internal codebase exploration with external documentation research.

## Purpose

This skill enables thorough research by:
1. Analyzing the existing codebase for relevant patterns and implementations
2. Searching external documentation and best practices
3. Synthesizing findings into actionable recommendations

## Invocation

```bash
/cw:research "<topic>" [options]
```

## Skill Behavior

### 1. Query Understanding

First, understand what the user is researching:

```markdown
## Query Analysis

Topic: [extracted from user input]
Type: [concept | implementation | comparison | troubleshooting]
Scope: [internal | external | both]
Depth: [shallow | normal | deep]
```

### 2. Internal Research Phase

When internal research is requested or default:

```markdown
## Internal Research Steps

[1] Symbol Search
    Use Serena find_symbol with topic keywords
    Search for classes, functions, types related to topic

[2] Pattern Search
    Use search_for_pattern for usage patterns
    Look for configuration files

[3] Reference Analysis
    Use find_referencing_symbols to understand usage
    Map the dependency chain

[4] Context Gathering
    Use get_symbols_overview for relevant files
    Read key implementations

Output: Organized findings about current codebase state
```

### 3. External Research Phase

When external research is requested or default:

```markdown
## External Research Steps

[1] Web Search
    Use WebSearch for documentation and articles
    Focus on official docs, reputable sources

[2] Documentation Fetch
    Use WebFetch for detailed page content
    Extract relevant sections

[3] Library Docs (if applicable)
    Use Context7 for library-specific documentation
    Get code examples

Output: Best practices, examples, recommendations
```

### 4. Synthesis Phase

Combine findings:

```markdown
## Synthesis Steps

[1] Compare Internal vs External
    What does our code do vs what's recommended?
    Identify gaps and discrepancies

[2] Generate Recommendations
    Priority-ordered improvements
    Code examples for implementation

[3] Format Report
    Structured markdown output
    Save to .caw/research/ if requested
```

## Agent Integration

### With OMC Available

When OMC plugin is detected, delegate to specialized agents:

```markdown
## OMC Agent Delegation

Internal Research:
  Agent: omc:explore
  Task: "Explore codebase for: {topic}"
  Output: File list, symbol map, patterns

External Research:
  Agent: omc:researcher
  Task: "Research documentation for: {topic}"
  Output: Best practices, official recommendations

Synthesis:
  Agent: omc:analyst
  Task: "Synthesize research findings"
  Output: Comparative analysis, recommendations
```

### Without OMC (Fallback)

Use direct tools:

```markdown
## Fallback Research

Internal:
  - Direct Serena tool calls
  - Grep/Glob for pattern matching

External:
  - WebSearch + WebFetch
  - Context7 for libraries

Synthesis:
  - Direct LLM analysis
  - Manual comparison
```

## Output Format

### Research Report Structure

```markdown
# Research: {Topic}

## Summary
Brief overview of findings

## Internal Analysis

### Current Implementation
- File locations
- Key symbols
- Patterns used

### Dependencies
- External packages
- Internal modules

## External Research

### Best Practices
1. Practice 1
2. Practice 2

### Documentation Sources
- [Source 1](url)
- [Source 2](url)

## Synthesis

### Gap Analysis
| Aspect | Current | Recommended |
|--------|---------|-------------|
| ... | ... | ... |

### Recommendations
1. 🔴 High Priority: ...
2. 🟡 Medium Priority: ...
3. 🟢 Nice to Have: ...

## Context File
Location: .caw/research/{topic}-{date}.md
```

## State Management

### Research Context File

Location: `.caw/research/{name}.md`

```markdown
# Research Context: {Name}

## Metadata
- Created: {timestamp}
- Topic: {topic}
- Depth: {depth}
- Duration: {time}

## Findings
{research content}

## Usage
Reference this in workflow:
  /cw:start "task" --research-context {name}
```

## Error Handling

### No Internal Results

```markdown
⚠️ No matching symbols found in codebase

This topic may be:
- Not yet implemented
- Using different terminology
- In external dependencies only

Suggestion: Focus on external research
  /cw:research "{topic}" --external
```

### No External Results

```markdown
⚠️ Limited external documentation found

Try:
- More specific search terms
- Different topic phrasing
- Check official library docs directly
```

### Rate Limiting

```markdown
⚠️ Search rate limited

Waiting 30 seconds before retry...
Consider using --depth shallow for faster results
```

## Integration Points

### With Planning

Research can inform planning:

```bash
/cw:research "authentication patterns" --save auth-research
/cw:start "Implement OAuth" --research-context auth-research
```

### With Review

Research can support code review:

```bash
/cw:research "security best practices" --external
/cw:review --focus security
```

### With QA

Research can guide quality improvements:

```bash
/cw:research "testing patterns"
/cw:ultraqa --target test
```

## Metrics

After research completion, record:

```json
{
  "research_id": "res_20240115_103045",
  "topic": "JWT authentication",
  "duration_seconds": 180,
  "internal_results": 12,
  "external_sources": 5,
  "recommendations": 3,
  "saved_to": ".caw/research/jwt-auth.md"
}
```
