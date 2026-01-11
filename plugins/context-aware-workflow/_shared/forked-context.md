# Forked Context Pattern

Skills with `forked-context: true` run in an isolated context.

## Behavior

- Skill executes in separate context from main conversation
- Cannot see prior conversation history
- Must return structured output for main context to use

## Return Format

Skill must return structured data that main context can consume:

```yaml
result:
  success: true|false
  data: [skill output]
  summary: [brief description]
```

## Usage in Skills

```yaml
---
forked-context: true
---
```

When forked:
1. Skill receives only the invocation prompt
2. Performs isolated analysis/action
3. Returns structured result
4. Main context processes result
