# Review Output Schema

Location: `.caw/last_review.json`

## JSON Structure

```json
{
  "version": "1.0",
  "timestamp": "[ISO8601]",
  "scope": {
    "files": ["path/file.ts"],
    "phase": 2,
    "step": "2.3"
  },
  "summary": {
    "overall_status": "APPROVED|APPROVED_WITH_SUGGESTIONS|NEEDS_WORK|BLOCKED",
    "scores": {
      "correctness": { "score": "good|fair|poor", "issues": 0 },
      "code_quality": { "score": "...", "issues": 0 },
      "best_practices": { "score": "...", "issues": 0 },
      "security": { "score": "...", "issues": 0 },
      "performance": { "score": "...", "issues": 0 }
    },
    "total_issues": 0,
    "auto_fixable": 0,
    "agent_required": 0
  },
  "issues": [
    {
      "id": "issue_001",
      "file": "path/file.ts",
      "line": 45,
      "category": "constants|docs|style|imports|naming|logic|performance|security|architecture",
      "severity": "critical|major|minor|suggestion",
      "auto_fixable": true,
      "title": "Issue title",
      "description": "Detailed description",
      "current_code": "code snippet",
      "suggested_fix": { "type": "fix_type", "details": "..." }
    }
  ],
  "action_items": [
    { "priority": "high|medium|low", "category": "...", "item": "...", "file": "...", "line": 0, "auto_fixable": true }
  ],
  "test_coverage": {
    "files": [{ "file": "...", "coverage": 85, "status": "good|fair|poor" }],
    "missing_tests": ["description"]
  }
}
```

## Issue Categories

| Category | Auto-Fixable | Description |
|----------|--------------|-------------|
| constants | ✅ Yes | Magic numbers → named constants |
| docs | ✅ Yes | Missing JSDoc/docstrings |
| style | ✅ Yes | Lint/formatting violations |
| imports | ✅ Yes | Import organization |
| naming | ❌ No | Variable/function naming (semantic) |
| logic | ❌ No | Logic improvements/bug fixes |
| performance | ❌ No | Performance optimizations |
| security | ❌ No | Security vulnerability fixes |
| architecture | ❌ No | Architectural improvements |

## Severity Levels

| Severity | Icon | Action Required |
|----------|------|-----------------|
| critical | 🔴 | Must fix before merge |
| major | 🟠 | Should fix |
| minor | 🟡 | Consider fixing |
| suggestion | 🟢 | Optional |

## Score Ratings

| Rating | Icon | Meaning |
|--------|------|---------|
| excellent | 🟢🟢 | Exceeds expectations |
| good | 🟢 | Meets standards |
| fair | 🟡 | Minor improvements needed |
| poor | 🟠 | Significant issues |
| critical | 🔴 | Blocking issues |
