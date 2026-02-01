---
name: knowledge-base
description: Centralized knowledge repository for capturing, organizing, and retrieving project knowledge
allowed-tools: Read, Write, Glob, Grep
---

# Knowledge Base

Centralized repository for project-specific knowledge.

## Triggers

1. Agent questions ("How does X work?") → search first
2. Session completion → organize and auto-capture
3. Explicit request ("Save this information")
4. Relevant domain rules discovered

## Knowledge Categories

| Category | Description | Examples |
|----------|-------------|----------|
| domain/ | Business logic, rules | Order rules, pricing policies |
| technical/ | Implementation details | API methods, config values |
| conventions/ | Project rules | Coding standards, branch strategy |
| gotchas/ | Pitfalls, cautions | Known bugs, non-intuitive behavior |
| integrations/ | External services | API endpoints, key locations |

## Workflow

### 1. Detect Knowledge
```yaml
high_value:
  - Domain rules: "When X, must do Y"
  - Configuration: "Env var Z required"
  - Gotchas: "Don't do it this way"
  - Integration: "API called like this"
```

### 2. Categorize
```yaml
domain: ["business", "rule", "policy", "when", "must"]
technical: ["implementation", "config", "setup", "api"]
conventions: ["standard", "always", "never"]
gotchas: ["careful", "don't", "avoid", "bug"]
integrations: ["external", "third-party", "service"]
```

### 3. Save Entry
```
Path: .caw/knowledge/{category}/{slug}.md
Confirm: 📚 Knowledge saved: {title}
```

## Entry Template

```markdown
# {Title}

| Field | Value |
|-------|-------|
| **ID** | kb-{NNN} |
| **Category** | {primary} > {sub} |
| **Created** | YYYY-MM-DD |

## Summary
[1-2 sentences]

## Content
[Detailed knowledge]

## Keywords
#keyword1 #keyword2
```

## Directory Structure

```
.caw/knowledge/
├── index.json       # Master index
├── domain/
├── technical/
├── conventions/
└── gotchas/
```

## Search Behavior

| Method | Weight |
|--------|--------|
| Keyword match | 1.0 |
| Category filter | 0.8 |
| Full-text search | 0.5 |
| Related links | 0.6 |

## Agent Integration

| Agent | Usage |
|-------|-------|
| Planner | Check domain rules |
| Builder | Search before implementation |
| Reviewer | Verify compliance |
| All | Search before asking user |

## Auto-Capture Rules

```yaml
from_insights: Insight marked "persistent" → create entry
from_decisions: All ADRs → link in index
from_conversation: "Remember that...", "Important:..." → prompt capture
```

## Boundaries

**Will:** Store systematically, organize by category, keyword search, maintain links
**Won't:** Delete without confirmation, store credentials, auto-expire, sync externally
