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
    "plansDirectory": ".claude/plans/",
    "plansDirectorySource": "default",
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

## Environment Detection

Plugin availability and runtime environment information.

```json
{
  "environment": {
    "omc_available": false,
    "omc_version": null,
    "detection_method": "plugin_directory",
    "fallback_mode": true,
    "degraded_features": [
      "ultraqa:advanced_diagnosis",
      "research:specialized_agents",
      "qaloop:intelligent_fix"
    ],
    "detected_at": "2024-01-15T10:30:00Z"
  }
}
```

### Environment Fields

| Field | Type | Description |
|-------|------|-------------|
| `omc_available` | boolean | Whether oh-my-claudecode plugin is installed |
| `omc_version` | string\|null | OMC version if available |
| `detection_method` | string | How OMC was detected: `env_variable`, `plugin_directory`, `not_found` |
| `fallback_mode` | boolean | True when using CAW fallback agents |
| `degraded_features` | string[] | List of features with reduced functionality |
| `detected_at` | ISO8601 | Timestamp of last detection |

### Detection Methods

| Method | Priority | Description |
|--------|----------|-------------|
| `env_variable` | 1 | `OMC_ENABLED` environment variable set |
| `plugin_directory` | 2 | `~/.claude/plugins/oh-my-claudecode/` exists |
| `not_found` | - | OMC not detected |
