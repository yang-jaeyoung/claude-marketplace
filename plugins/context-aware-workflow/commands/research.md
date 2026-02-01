---
description: Integrated research mode combining internal codebase analysis and external documentation
argument-hint: "<topic> [--internal] [--external] [--depth shallow|normal|deep]"
---

# /cw:research - Integrated Research Mode

Comprehensive research combining internal codebase exploration (via Serena) and external documentation research (via web tools).

## Usage

```bash
/cw:research "JWT authentication best practices"      # Both internal + external
/cw:research "how is auth handled" --internal         # Codebase only
/cw:research "React Server Components" --external     # Documentation only
/cw:research "database pooling" --depth deep          # Comprehensive
/cw:research "GraphQL schema" --save context-graphql  # Save for later
```

## Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `--internal` | false | Codebase analysis only |
| `--external` | false | Documentation only |
| `--depth` | normal | shallow, normal, deep |
| `--save` | - | Save to named context file |
| `--load` | - | Load previous research |
| `--format` | markdown | markdown, json, summary |

## Research Modes

| Mode | Tools | Output |
|------|-------|--------|
| **Internal** | Serena (find_symbol, get_symbols_overview), Grep/Glob, Task(Explore) | Files, symbols, patterns, dependencies |
| **External** | WebSearch, WebFetch, Context7 | Best practices, docs, examples |
| **Combined** | All tools | Internal analysis → External research → Synthesis with gap analysis |

## Agent Selection

| Mode | Standard | Deep (--depth deep) |
|------|----------|---------------------|
| Internal | Task(Explore) Haiku | cw:planner-opus |
| Synthesis | cw:Planner Sonnet | cw:planner-opus |

## Depth Levels

| Level | Internal | External | Output |
|-------|----------|----------|--------|
| **shallow** | Keyword matches, file list, symbol overview | Top 3-5 results, snippets | Brief summary |
| **normal** | Symbol search with body, 1-level references, patterns | Top 10 results, page summaries, examples | Detailed report |
| **deep** | Full symbol graph, multi-level chains, architecture mapping | Exhaustive search, deep analysis, cross-reference | Comprehensive document |

## Execution Flow

```
Query Analysis → Internal Research (symbols, context, patterns)
             → External Research (search, docs, Context7)
             → Synthesis (organize, compare, recommend)
```

## Output Example

```markdown
# Research: JWT Authentication

## Internal Analysis
- `src/auth/jwt.ts`: Token generation/validation
- Pattern: HS256, 24h expiry, refresh in HTTP-only cookie

## External Research
- Best: RS256 for production, 15-60m tokens, secure rotation
- Sources: jwt.io, OWASP JWT Cheat Sheet

## Synthesis
| Aspect | Current | Recommended |
|--------|---------|-------------|
| Algorithm | HS256 | RS256 |
| Expiry | 24h | 15-60m |

Recommendations:
1. 🔴 Migrate to RS256
2. 🟡 Reduce token expiry
```

## Context Persistence

```bash
/cw:research "GraphQL" --save graphql-schema    # Save to .caw/research/
/cw:research "GraphQL" --load graphql-schema    # Load and extend
/cw:start "Implement GraphQL" --research-context graphql-schema  # Use in planning
```

## Comparison

| Feature | /cw:research | Task(Explore) | WebSearch |
|---------|--------------|---------------|-----------|
| Scope | Integrated | Internal only | External only |
| Synthesis | Yes | No | No |
| Persistence | Yes | No | No |

## Related

- [Model Routing](../_shared/model-routing.md)
- [Serena Integration](../_shared/serena-integration.md)
