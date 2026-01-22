---
description: Integrated research mode combining internal codebase analysis and external documentation
argument-hint: "<topic> [--internal] [--external] [--depth shallow|normal|deep]"
---

# /cw:research - Integrated Research Mode

Comprehensive research combining internal codebase exploration (via Serena) and external documentation research (via web tools). Uses specialized agents when OMC is available.

## Usage

```bash
# Basic research (internal + external)
/cw:research "JWT authentication best practices"

# Internal only (codebase exploration)
/cw:research "how is auth handled" --internal

# External only (documentation/web)
/cw:research "React Server Components" --external

# Combined with depth control
/cw:research "database connection pooling" --depth deep

# Save research context for later use
/cw:research "GraphQL schema design" --save context-graphql
```

## Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `--internal` | false | Focus on internal codebase analysis |
| `--external` | false | Focus on external documentation |
| (neither) | - | Research both internal and external |
| `--depth` | normal | Research depth: shallow, normal, deep |
| `--save` | - | Save research to named context file |
| `--load` | - | Load previous research context |
| `--format` | markdown | Output format: markdown, json, summary |

## Research Modes

### Internal Research

Explores the existing codebase using Serena and symbolic tools:

```
┌─────────────────────────────────────────────────────────────────┐
│                    INTERNAL RESEARCH                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Tools Used:                                                     │
│    • Serena: find_symbol, get_symbols_overview                   │
│    • Serena: find_referencing_symbols                            │
│    • Serena: search_for_pattern                                  │
│    • Grep/Glob: Pattern matching                                 │
│                                                                  │
│  OMC Enhancement (when available):                               │
│    • omc:explore - Fast codebase navigation                      │
│                                                                  │
│  Output:                                                         │
│    • Relevant files and symbols                                  │
│    • Architecture understanding                                  │
│    • Usage patterns                                              │
│    • Dependencies                                                │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### External Research

Searches external documentation and resources:

```
┌─────────────────────────────────────────────────────────────────┐
│                    EXTERNAL RESEARCH                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Tools Used:                                                     │
│    • WebSearch: General web search                               │
│    • WebFetch: Documentation retrieval                           │
│    • Context7: Library documentation                             │
│                                                                  │
│  OMC Enhancement (when available):                               │
│    • omc:researcher - Specialized documentation research         │
│    • omc:scientist - Data analysis and experimentation           │
│                                                                  │
│  Output:                                                         │
│    • Best practices                                              │
│    • Official documentation                                      │
│    • Community solutions                                         │
│    • Code examples                                               │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Combined Research (Default)

```
┌─────────────────────────────────────────────────────────────────┐
│                    COMBINED RESEARCH                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   [1] Internal Analysis                                          │
│       • How is this currently handled in our codebase?           │
│       • What patterns/conventions exist?                         │
│       • What dependencies are involved?                          │
│                                                                  │
│   [2] External Research                                          │
│       • What are best practices?                                 │
│       • What do official docs recommend?                         │
│       • What solutions do others use?                            │
│                                                                  │
│   [3] Synthesis                                                  │
│       • Compare internal vs external approaches                  │
│       • Identify gaps                                            │
│       • Recommend improvements                                   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Agent Selection

### OMC Available

```
Internal Research:
  Agent: omc:explore (Haiku)
  Purpose: Fast codebase navigation
  
  Agent: omc:analyst (Opus) [for --depth deep]
  Purpose: Deep pattern analysis

External Research:
  Agent: omc:researcher (Sonnet)
  Purpose: Documentation research
  
  Agent: omc:scientist (Sonnet) [for data topics]
  Purpose: Data analysis, experiments

Synthesis:
  Agent: omc:analyst (Opus)
  Purpose: Combine findings, recommend
```

### OMC NOT Available (Fallback)

```
⚠️ Running Research in Basic Mode

Internal Research:
  Tools: Serena (direct), Grep, Glob
  Limitation: Manual navigation required

External Research:
  Tools: WebSearch, WebFetch, Context7
  Limitation: No specialized prompt

Synthesis:
  Agent: cw:planner-opus
  Limitation: Less focused synthesis
```

## Research Depth Levels

### Shallow (Quick Overview)

```
Time: ~1-2 minutes
Internal:
  • Search for direct keyword matches
  • List relevant files
  • Show symbol overview

External:
  • Top 3-5 search results
  • Summary snippets only

Output: Brief summary with key links
```

### Normal (Default)

```
Time: ~3-5 minutes
Internal:
  • Symbol search with body inspection
  • Reference chain analysis (1 level)
  • Pattern identification

External:
  • Top 10 search results
  • Fetch and summarize key pages
  • Code examples extraction

Output: Detailed report with recommendations
```

### Deep (Comprehensive)

```
Time: ~10-15 minutes
Internal:
  • Full symbol graph analysis
  • Multi-level reference chains
  • Architecture mapping
  • Dependency impact analysis

External:
  • Exhaustive search (multiple queries)
  • Deep page analysis
  • Cross-reference verification
  • Alternative approach exploration

Output: Comprehensive research document
```

## Execution Flow

### Phase 1: Query Analysis

```
[1] Parse research query
    topic = extract_topic(query)
    scope = determine_scope(flags)  # internal, external, both
    depth = determine_depth(flags)

[2] Generate search strategies
    internal_queries = generate_internal_queries(topic)
    external_queries = generate_external_queries(topic)
```

### Phase 2: Internal Research (if applicable)

```
[1] Symbol search
    FOR query IN internal_queries:
      results += Serena.find_symbol(query)
      results += Serena.search_for_pattern(query)

[2] Context gathering
    FOR symbol IN relevant_symbols:
      context += Serena.get_symbols_overview(symbol.file)
      references += Serena.find_referencing_symbols(symbol)

[3] Pattern analysis
    patterns = analyze_usage_patterns(context, references)
```

### Phase 3: External Research (if applicable)

```
[1] Web search
    FOR query IN external_queries:
      results += WebSearch(query)

[2] Documentation fetch
    FOR result IN top_results:
      IF is_documentation(result):
        content += WebFetch(result.url)

[3] Context7 lookup (for libraries)
    IF library_detected:
      docs += Context7.query_docs(library, topic)
```

### Phase 4: Synthesis

```
[1] Organize findings
    internal_findings = organize(internal_results)
    external_findings = organize(external_results)

[2] Compare and analyze
    gaps = identify_gaps(internal_findings, external_findings)
    recommendations = generate_recommendations(gaps)

[3] Generate report
    report = format_report(findings, recommendations)
```

## Output Formats

### Markdown (Default)

```markdown
# Research: JWT Authentication Best Practices

## Internal Analysis

### Current Implementation
- `src/auth/jwt.ts`: Token generation and validation
- `src/middleware/auth.ts`: Request authentication

### Patterns Found
- Using HS256 algorithm
- 24-hour token expiry
- Refresh token in HTTP-only cookie

### Dependencies
- jsonwebtoken: ^9.0.0

## External Research

### Best Practices
1. Use RS256 for production (asymmetric)
2. Short-lived access tokens (15-60 min)
3. Secure refresh token rotation

### Official Recommendations
- [JWT.io Best Practices](https://jwt.io/...)
- [OWASP JWT Cheat Sheet](https://owasp.org/...)

## Synthesis

### Current vs Recommended
| Aspect | Current | Recommended |
|--------|---------|-------------|
| Algorithm | HS256 | RS256 |
| Expiry | 24h | 15-60m |
| Refresh | Cookie | Rotation |

### Recommendations
1. 🔴 **Migrate to RS256** - Security improvement
2. 🟡 **Reduce token expiry** - Better security posture
3. 🟢 **Add refresh rotation** - Prevent token reuse

## Context File
Saved to: `.caw/research/jwt-auth.md`
```

### JSON Format

```json
{
  "query": "JWT authentication best practices",
  "timestamp": "2024-01-15T10:30:45Z",
  "internal": {
    "files": [...],
    "symbols": [...],
    "patterns": [...],
    "dependencies": [...]
  },
  "external": {
    "sources": [...],
    "best_practices": [...],
    "examples": [...]
  },
  "synthesis": {
    "gaps": [...],
    "recommendations": [...]
  }
}
```

### Summary Format

```
📚 Research Summary: JWT Authentication

🔍 Internal: 3 files, 12 symbols found
📖 External: 8 sources reviewed

Key Findings:
• Current: HS256, 24h expiry
• Recommended: RS256, 15-60m expiry

Top Recommendations:
1. Migrate to RS256 algorithm
2. Implement refresh token rotation

Full report: /cw:research "JWT" --load
```

## Progress Display

```
🔬 /cw:research "JWT authentication" --depth normal

Analyzing query...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[1/4] Internal Research
      🔍 Searching symbols...    Found 12 matches
      📁 Analyzing files...      3 relevant files
      🔗 Tracing references...   8 usages found
      ✅ Internal analysis complete

[2/4] External Research
      🌐 Web searching...        15 results
      📖 Fetching docs...        5 pages analyzed
      📚 Context7 lookup...      Library docs loaded
      ✅ External research complete

[3/4] Synthesis
      🔄 Comparing findings...
      📊 Identifying gaps...
      💡 Generating recommendations...
      ✅ Synthesis complete

[4/4] Generating Report
      📝 Formatting markdown...
      💾 Saving context...
      ✅ Report ready

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 Research Complete

Time: 3m 45s
Internal: 3 files, 12 symbols
External: 5 sources
Recommendations: 3

📁 Saved to: .caw/research/jwt-auth-20240115.md

💡 Use this research:
   /cw:start "Implement JWT best practices" --context jwt-auth
```

## Context Persistence

### Saving Research

```bash
/cw:research "GraphQL schema" --save graphql-schema
# Saves to: .caw/research/graphql-schema.md
```

### Loading Research

```bash
/cw:research "GraphQL" --load graphql-schema
# Loads previous context, adds new findings
```

### Using in Workflow

```bash
/cw:start "Implement GraphQL API" --research-context graphql-schema
# Planner receives research as additional context
```

## Best Practices

1. **Start broad, then narrow**
   - Initial research with default depth
   - Deep dive on specific areas

2. **Combine modes effectively**
   - Internal first to understand current state
   - External to find improvements

3. **Save valuable research**
   - Use `--save` for reusable findings
   - Reference in planning

4. **Use appropriate depth**
   - Shallow for quick checks
   - Deep for architecture decisions

## Comparison

| Feature | /cw:research | Task(Explore) | WebSearch |
|---------|--------------|---------------|-----------|
| Scope | Integrated | Internal only | External only |
| Intelligence | High | Medium | Low |
| Synthesis | Yes | No | No |
| Persistence | Yes | No | No |
| Best for | Planning | Navigation | Quick lookup |

## Related Documentation

- [Agent Resolver](../_shared/agent-resolver.md) - Agent selection
- [Agent Registry](../_shared/agent-registry.md) - Available agents
- [Serena Integration](../_shared/serena-integration.md) - Code analysis
