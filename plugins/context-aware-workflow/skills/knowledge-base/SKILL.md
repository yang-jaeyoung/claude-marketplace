---
name: knowledge-base
description: Centralized knowledge repository for capturing, organizing, and retrieving project knowledge. Used by all agents for context and learning. Invoked when agents need project-specific knowledge or when capturing important information.
allowed-tools: Read, Write, Glob, Grep
---

# Knowledge Base

Centralized repository for capturing, organizing, and retrieving project-specific knowledge.

## Core Principle

**Knowledge Accumulation = Context Preservation**

Systematically store important information learned from the project to maintain the same context across new sessions.

## Triggers

This Skill activates in the following situations:

1. **Agent Questions**
   - "How does X work in this project?"
   - Search knowledge-base first before asking the user

2. **Session Completion**
   - Organize knowledge at workflow end
   - Auto-capture important information

3. **Explicit Requests**
   - "Save this information"
   - "Add to knowledge-base"

4. **Relevant Information Discovery**
   - When domain rules are discovered
   - When important technical details are identified

## Knowledge Categories

| Category | Description | Examples |
|----------|-------------|----------|
| **domain/** | Business logic, domain rules | Order processing rules, pricing policies |
| **technical/** | Technical implementation details | API integration methods, configuration values |
| **conventions/** | Project rules | Coding standards, branch strategy |
| **gotchas/** | Cautions, pitfalls | Known bugs, non-intuitive behaviors |
| **integrations/** | External service integrations | API key locations, endpoints |

## Behavior

### Step 1: Knowledge Detection

Identify information worth capturing:

```yaml
detection:
  high_value:
    - Domain rules: "When X, must do Y"
    - Configuration: "Environment variable Z required"
    - Gotchas: "Don't do it this way"
    - Integration details: "API is called like this"

  sources:
    - insight-collector: Captured insights
    - decision-logger: Recorded decisions
    - Information discovered during conversation
    - Code comments/documentation
```

### Step 2: Categorize

Assign appropriate category:

```yaml
categorization:
  domain:
    keywords: ["business", "rule", "policy", "when", "must"]
    examples: ["Orders $100+ get free shipping"]

  technical:
    keywords: ["implementation", "config", "setup", "api"]
    examples: ["Redis cache TTL is 1 hour"]

  conventions:
    keywords: ["standard", "convention", "always", "never"]
    examples: ["All APIs use JSON:API format"]

  gotchas:
    keywords: ["careful", "don't", "avoid", "bug", "issue"]
    examples: ["Date.now() is flaky in tests"]

  integrations:
    keywords: ["external", "third-party", "api", "service"]
    examples: ["Stripe webhook secret location"]
```

### Step 3: Create Entry

Create knowledge entry:

```yaml
action: Write tool
path: .caw/knowledge/{category}/{slug}.md
content: See Knowledge Entry Template
```

### Step 4: Update Index

Update index file:

```yaml
action: Write tool
path: .caw/knowledge/index.json
content:
  entries:
    - id: kb-{NNN}
      title: "..."
      category: ["technical", "architecture"]
      keywords: ["jwt", "auth"]
      path: "technical/jwt-implementation.md"
```

### Step 5: Confirm

Confirm save completion:

```
📚 Knowledge saved: {title}
   Category: {category}
   Path: .caw/knowledge/{path}
```

## Knowledge Entry Template

See [templates/knowledge-entry.md](templates/knowledge-entry.md) for the full template.

```markdown
# {Title}

## Metadata
| Field | Value |
|-------|-------|
| **ID** | kb-{NNN} |
| **Category** | {primary} > {sub} |
| **Created** | YYYY-MM-DD |
| **Updated** | YYYY-MM-DD |
| **Sources** | insight / decision / code / conversation |

## Summary
[1-2 sentence summary]

## Content
[Detailed knowledge content]

## Context
[When this knowledge applies]

## Related
- [Links to ADRs, insights, other entries]

## Keywords
#keyword1 #keyword2 #keyword3
```

## Directory Structure

```
.caw/
└── knowledge/
    ├── index.json                 # Master index
    │
    ├── domain/
    │   ├── order-processing.md
    │   └── pricing-rules.md
    │
    ├── technical/
    │   ├── architecture/
    │   │   └── service-layer.md
    │   └── integrations/
    │       └── stripe-webhook.md
    │
    ├── conventions/
    │   └── api-response-format.md
    │
    └── gotchas/
        ├── date-handling.md
        └── async-testing.md
```

## Index File Format

```json
{
  "version": "1.0",
  "last_updated": "2026-01-04T15:30:00Z",
  "entries": [
    {
      "id": "kb-001",
      "title": "JWT Token Refresh Strategy",
      "category": ["technical", "architecture"],
      "keywords": ["jwt", "auth", "token", "refresh"],
      "path": "technical/architecture/jwt-refresh.md",
      "related": ["ADR-001", "insight-20260104-jwt"],
      "created": "2026-01-04",
      "sources": ["decision", "insight"]
    }
  ],
  "categories": {
    "domain": {"count": 5},
    "technical": {"count": 12},
    "conventions": {"count": 3},
    "gotchas": {"count": 8}
  }
}
```

## Search Behavior

When agents search for knowledge:

```yaml
search:
  methods:
    keyword:
      - Match against keywords array
      - Match against title
      weight: 1.0

    category:
      - Filter by category path
      weight: 0.8

    full_text:
      - Search content body
      weight: 0.5

    related:
      - Follow relationship links
      weight: 0.6

  ranking:
    - Exact match: highest
    - Multiple keyword match: high
    - Category match: medium
    - Content match: lower
```

## Example Flow

### Capturing Knowledge

```
1. User: "Orders $100 or more get free shipping"

2. Model: Domain rule detected
   → This is a business rule

3. Model: Create knowledge entry
   📚 Knowledge saved: Order Free Shipping Rule
      Category: domain
      Path: .caw/knowledge/domain/order-free-shipping.md

4. Saved content:
   # Order Free Shipping Rule

   ## Summary
   Orders $100 or more qualify for free shipping.

   ## Content
   - Threshold: $100 (before tax)
   - Applies to: All shipping methods
   - Exclusions: None currently

   ## Keywords
   #order #shipping #pricing
```

### Retrieving Knowledge

```
1. Builder: "I need to implement shipping cost calculation logic..."

2. knowledge-base search:
   Query: "shipping", "order", "pricing"
   Result: kb-005 Order Free Shipping Rule

3. Provide context to Builder:
   📚 Related knowledge found:
   - Order Free Shipping Rule (domain)
     "Orders $100+ get free shipping"
```

## Integration with Agents

| Agent | Usage |
|-------|-------|
| **Planner** | Check domain rules for planning |
| **Builder** | Search related knowledge before implementation |
| **Reviewer** | Verify rule compliance |
| **Architect** | Reference existing architecture decisions |
| **All** | Search knowledge before asking user |

## Integration with Other Skills

| Skill | Integration |
|-------|-------------|
| **insight-collector** | Promote insights to knowledge |
| **decision-logger** | Link ADRs to knowledge |
| **context-helper** | Provide related knowledge as context |
| **session-persister** | Organize knowledge at session end |

## Knowledge Lifecycle

```yaml
lifecycle:
  creation:
    - Auto-capture from insights/decisions
    - Manual addition

  update:
    - Edit existing entry
    - Add related links
    - Update keywords

  archival:
    - Mark as outdated (don't delete)
    - Link to replacement entry

  deletion:
    - Only with user explicit request
    - Keep in archive folder
```

## Auto-Capture Rules

Information that should be auto-captured:

```yaml
auto_capture:
  from_insights:
    condition: Insight marked as "persistent"
    action: Create knowledge entry

  from_decisions:
    condition: All accepted ADRs
    action: Link in knowledge index

  from_conversation:
    patterns:
      - "Remember that..."
      - "Important: ..."
      - "Note: ..."
      - "Things to remember: ..."
    action: Prompt for knowledge capture
```

## Boundaries

**Will:**
- Systematically store project knowledge
- Organize and index by category
- Provide keyword-based search
- Maintain links between related entries

**Will Not:**
- Delete knowledge without user confirmation
- Store sensitive information (credentials, secrets)
- Automatically expire knowledge
- Sync with external systems
