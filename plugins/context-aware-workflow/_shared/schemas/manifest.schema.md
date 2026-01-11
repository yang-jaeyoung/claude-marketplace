# Context Manifest Schema

Location: `.caw/context_manifest.json`

## Structure

```json
{
  "version": "1.0",
  "initialized": "[ISO8601]",
  "project": {
    "type": "nodejs|python|rust|go|java|unknown",
    "root": ".",
    "detected_frameworks": [
      {"name": "React", "version": "18.x", "category": "frontend"}
    ]
  },
  "files": {
    "active": [],
    "project": [
      {"path": "package.json", "reason": "Dependencies", "auto_detected": true}
    ],
    "ignored": ["node_modules/**", "dist/**"]
  },
  "plans": {
    "detected": [".claude/plan.md"],
    "active": null
  },
  "settings": {
    "max_active_files": 10,
    "auto_prune_after_turns": 5,
    "auto_archive_completed": true
  }
}
```

## Framework Detection

| File | Type | Key Patterns |
|------|------|--------------|
| package.json | nodejs | react, vue, angular, typescript, jest |
| pyproject.toml | python | fastapi, django, flask, pytest |
| Cargo.toml | rust | tokio, actix-web, serde |
| go.mod | go | gin-gonic, labstack/echo |
