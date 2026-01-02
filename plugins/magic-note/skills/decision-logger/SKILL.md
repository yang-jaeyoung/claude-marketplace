---
name: decision-logger
description: Records technical decisions and their rationale to Magic Note. Use when users make technology choices, architectural decisions, library selections, or any significant technical trade-off decisions during development.
---

# Decision Logger Skill

This skill captures important technical decisions and their context for future reference.

## When to Activate

Activate this skill when users:
- Choose between technologies (React vs Vue, PostgreSQL vs MongoDB)
- Select libraries or frameworks
- Make architectural decisions (monolith vs microservices)
- Decide on design patterns
- Choose between implementation approaches
- Make trade-off decisions (performance vs readability)
- Select deployment strategies

## Decision Detection Signals

Look for conversations that include:
- "I'll go with..." or "Let's use..."
- "We decided to..." or "The choice is..."
- Comparison discussions with a conclusion
- "vs" comparisons with a final selection
- Trade-off analysis with a decision

## How to Log Decisions

1. **Detect Decision Made**: Identify when a clear choice has been made

2. **Structure the Decision**:
   ```markdown
   ## Decision: [Brief title]

   **Date**: [Current date]
   **Context**: [What prompted this decision]

   ### Options Considered
   1. **[Option A]**: [Brief description]
      - Pros: [advantages]
      - Cons: [disadvantages]

   2. **[Option B]**: [Brief description]
      - Pros: [advantages]
      - Cons: [disadvantages]

   ### Decision
   **Chosen**: [Selected option]

   ### Rationale
   [Why this option was selected]

   ### Implications
   - [Future impact 1]
   - [Future impact 2]
   ```

3. **Offer to Save**:
   After a decision is made, ask:
   ```
   📝 Would you like to record this decision in Magic Note?
      This helps track why choices were made for future reference.
   ```

4. **Save if Confirmed**:
   Use `add_note` MCP tool with:
   ```
   type: "choice"
   title: "Decision: [brief title]"
   content: [structured decision content]
   tags: [relevant technology tags]
   project: [current project]
   ```

## Example Interaction

**User**: "Should I use Express or Fastify for this API?"

**Assistant**: [Provides comparison analysis]
"Based on your requirements for high performance and TypeScript support, I recommend Fastify..."

**User**: "OK, let's go with Fastify"

**Skill Action**:
```
📝 Would you like to record this decision?

   Decision: Use Fastify over Express for API Framework
   Context: High-performance API with TypeScript
   Chosen: Fastify
   Rationale: Better performance, native TypeScript support

   [Save to Magic Note?]
```

## Decision Categories

| Category | Example Decisions |
|----------|-------------------|
| Framework | React vs Vue vs Angular |
| Database | SQL vs NoSQL, specific DB choice |
| Architecture | Monolith vs Microservices |
| Hosting | AWS vs GCP vs Vercel |
| Testing | Jest vs Vitest, testing strategy |
| State Management | Redux vs Zustand vs Context |
| Styling | CSS-in-JS vs Tailwind vs CSS Modules |
| Build Tool | Webpack vs Vite vs esbuild |

## Non-Triggers

Do NOT activate for:
- Trivial decisions (variable naming, formatting)
- Temporary choices during exploration
- Questions without conclusions
- Decisions already documented elsewhere
