# 04. Plan Mode Integration Specification

Feature specification for integrating Claude Code's existing Plan Mode output into the workflow plugin.

## 1. Overview

### 1.1 Purpose
- Utilize plans generated in Claude Code Plan Mode as input for the Discovery phase
- Maintain user experience consistency through seamless integration with existing tools
- Prevent duplicate planning and minimize workflow entry barriers

### 1.2 Operation Method
**Hybrid Approach**: Auto-detection + User confirmation
- Auto-detect existing Plan Mode plans at SessionStart
- Confirm import with user (Human-in-the-Loop)
- Convert to `task_plan.md` format upon approval

## 2. Detection Logic

### 2.1 Detection Conditions
| Condition | Description | Priority |
|-----------|-------------|----------|
| File exists | `.claude/plan.md` existence | Required |
| Recency | Modified within last 24 hours | Recommended |
| Branch association | Plan related to current Git branch | Optional |
| Completion status | Checkbox completion rate < 100% | Recommended |

### 2.2 Detection Script
```python
# skills/plan-importer/scripts/detect_plan.py

import os
import json
from datetime import datetime, timedelta
from pathlib import Path

def resolve_plans_directory() -> str:
    """
    Resolve plansDirectory setting by priority

    Priority:
    1. .claude/settings.local.json
    2. .claude/settings.json
    3. ~/.claude/settings.json
    4. Default: ".claude/plans/"
    """
    settings_files = [
        ".claude/settings.local.json",
        ".claude/settings.json",
        os.path.expanduser("~/.claude/settings.json")
    ]

    for settings_path in settings_files:
        if os.path.exists(settings_path):
            try:
                with open(settings_path) as f:
                    settings = json.load(f)
                if "plansDirectory" in settings:
                    return settings["plansDirectory"]
            except (json.JSONDecodeError, IOError):
                continue

    return ".claude/plans/"

def get_plan_paths() -> list:
    """
    Generate search paths based on plansDirectory setting
    """
    plans_dir = resolve_plans_directory()

    # Configured directory + legacy paths
    return [
        f"{plans_dir}/current.md",
        f"{plans_dir}/*.md",
        ".claude/plan.md",  # Legacy (always check)
        "docs/plan.md"
    ]

# Legacy constant for backward compatibility
DEFAULT_PLAN_PATHS = [
    ".claude/plan.md",
    ".claude/plans/current.md",
    "docs/plan.md"
]

def detect_existing_plan():
    """
    Detect plan files created by Plan Mode

    Returns:
        dict: {
            "found": bool,
            "path": str,
            "modified": datetime,
            "summary": str,
            "completion_rate": float,
            "plans_directory": str  # Resolved plansDirectory
        }
    """
    plans_directory = resolve_plans_directory()
    plan_paths = get_plan_paths()

    for plan_path in plan_paths:
        if os.path.exists(plan_path):
            stat = os.stat(plan_path)
            modified = datetime.fromtimestamp(stat.st_mtime)

            # Only files modified within 24 hours
            if datetime.now() - modified > timedelta(hours=24):
                continue

            content = Path(plan_path).read_text()
            summary = extract_summary(content)
            completion = calculate_completion(content)

            return {
                "found": True,
                "path": plan_path,
                "modified": modified,
                "summary": summary,
                "completion_rate": completion,
                "plans_directory": plans_directory
            }

    return {"found": False, "plans_directory": plans_directory}

def extract_summary(content: str) -> str:
    """Extract summary from first header or first line"""
    lines = content.strip().split('\n')
    for line in lines:
        if line.startswith('# '):
            return line[2:].strip()
        if line.startswith('## '):
            return line[3:].strip()
    return lines[0][:50] if lines else "Unknown Plan"

def calculate_completion(content: str) -> float:
    """Calculate checkbox completion rate"""
    total = content.count('- [ ]') + content.count('- [x]') + content.count('- [X]')
    if total == 0:
        return 0.0
    completed = content.count('- [x]') + content.count('- [X]')
    return completed / total
```

## 3. User Interaction Flow

### 3.1 Prompt UI
```
┌─────────────────────────────────────────────────────────┐
│  📋 Existing Plan Mode plan detected.                   │
│                                                         │
│  File: .claude/plan.md                                  │
│  Modified: 2 hours ago                                  │
│  Progress: ████████░░ 80% (4/5 complete)               │
│  Summary: "Auth system refactoring - JWT → Session"     │
│                                                         │
│  ────────────────────────────────────────────────────   │
│                                                         │
│  [1] Start workflow with this plan                      │
│  [2] Preview plan                                       │
│  [3] Start new task (ignore plan)                       │
│  [4] Decide later (hide until next session)             │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 3.2 Option Actions
| Selection | Action | Next Step |
|-----------|--------|-----------|
| **[1] Start with plan** | Run `convert_plan.py` → Create `task_plan.md` | Enter Review Phase |
| **[2] Preview** | Display plan content + re-prompt | Re-display prompt |
| **[3] New task** | Ignore plan, start normal Discovery | Invoke Planner Agent |
| **[4] Later** | Create `.claude/plan_import_dismissed` | Continue normal session |

## 4. Plan Conversion

### 4.1 Input Format (Plan Mode Output)
```markdown
## Implementation Plan

Files to modify:
- `auth/jwt.ts`
- `auth/middleware.ts`
- `lib/session.ts`

Steps:
- [ ] 1. Review current JWT implementation in `auth/jwt.ts`
- [ ] 2. Create session store interface
- [x] 3. Implement Redis session adapter
- [ ] 4. Update middleware to use sessions
- [ ] 5. Add migration script for existing tokens

Considerations:
- Backward compatibility with existing tokens
- Session expiry handling
```

### 4.2 Output Format (task_plan.md)
```markdown
# Task Plan: Implementation Plan

## Metadata
| Field | Value |
|-------|-------|
| **Source** | Claude Code Plan Mode |
| **Original File** | `.claude/plan.md` |
| **Imported** | 2024-01-15 14:30:00 |
| **Completion** | 20% (1/5) |

## Context Files

### Active Context
| File | Reason | Status |
|------|--------|--------|
| `auth/jwt.ts` | Explicitly mentioned | 📖 Read |
| `auth/middleware.ts` | Explicitly mentioned | 📖 Read |
| `lib/session.ts` | Explicitly mentioned | 📝 Edit |

### Project Context (Read-Only)
- `GUIDELINES.md`
- `ARCHITECTURE.md`

## Execution Phases

### Phase 1: Analysis
| # | Step | Status | Agent | Notes |
|---|------|--------|-------|-------|
| 1.1 | Review current JWT implementation | ⏳ Pending | Planner | Analyze `auth/jwt.ts` |

### Phase 2: Implementation
| # | Step | Status | Agent | Notes |
|---|------|--------|-------|-------|
| 2.1 | Create session store interface | ⏳ Pending | Builder | |
| 2.2 | Implement Redis session adapter | ✅ Done | Builder | (imported as completed) |
| 2.3 | Update middleware to use sessions | ⏳ Pending | Builder | |

### Phase 3: Migration
| # | Step | Status | Agent | Notes |
|---|------|--------|-------|-------|
| 3.1 | Add migration script | ⏳ Pending | Builder | |

## Considerations (from original plan)
- Backward compatibility with existing tokens
- Session expiry handling

## Validation Checklist
- [ ] Existing tests pass
- [ ] New session-related tests added
- [ ] GUIDELINES.md compliance verified
- [ ] Reviewer Agent validation complete
```

### 4.3 Conversion Script
```python
# skills/plan-importer/scripts/convert_plan.py

import re
from datetime import datetime
from pathlib import Path
from typing import List, Dict

def convert_plan_to_task(plan_path: str) -> str:
    """
    Convert Plan Mode output to task_plan.md format
    """
    content = Path(plan_path).read_text()

    # Parse
    title = extract_title(content)
    files = extract_files(content)
    steps = extract_steps(content)
    considerations = extract_considerations(content)

    # Group steps into Phases
    phases = group_steps_into_phases(steps)

    # Generate task_plan.md
    return generate_task_plan(
        title=title,
        source_path=plan_path,
        files=files,
        phases=phases,
        considerations=considerations
    )

def extract_files(content: str) -> List[str]:
    """Extract file paths (inside backticks or in Files to modify section)"""
    files = set()

    # File paths in backticks
    backtick_pattern = r'`([^`]+\.[a-z]+)`'
    files.update(re.findall(backtick_pattern, content))

    # Files to modify section
    files_section = re.search(r'Files to modify:\n((?:- .+\n)+)', content)
    if files_section:
        for line in files_section.group(1).split('\n'):
            match = re.search(r'`([^`]+)`', line)
            if match:
                files.add(match.group(1))

    return list(files)

def extract_steps(content: str) -> List[Dict]:
    """Extract checkbox items"""
    steps = []
    pattern = r'- \[([ xX])\] (?:\d+\. )?(.+)'

    for match in re.finditer(pattern, content):
        completed = match.group(1).lower() == 'x'
        description = match.group(2).strip()
        steps.append({
            "description": description,
            "completed": completed,
            "files": extract_files(description)
        })

    return steps

def group_steps_into_phases(steps: List[Dict]) -> List[Dict]:
    """
    Group steps into logical Phases
    - Analysis/review keywords → Phase 1 (Analysis)
    - Implementation/creation keywords → Phase 2 (Implementation)
    - Migration/deploy keywords → Phase 3 (Migration/Deploy)
    """
    phases = {
        "Analysis": [],
        "Implementation": [],
        "Migration": []
    }

    analysis_keywords = ['review', 'analyze', 'check', 'investigate', 'understand']
    migration_keywords = ['migrate', 'deploy', 'script', 'migration']

    for step in steps:
        desc_lower = step["description"].lower()

        if any(kw in desc_lower for kw in analysis_keywords):
            phases["Analysis"].append(step)
        elif any(kw in desc_lower for kw in migration_keywords):
            phases["Migration"].append(step)
        else:
            phases["Implementation"].append(step)

    # Remove empty Phases
    return {k: v for k, v in phases.items() if v}

def generate_task_plan(title, source_path, files, phases, considerations) -> str:
    """Generate task_plan.md markdown"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # ... template-based generation logic ...
    pass
```

## 5. Hook Configuration

### 5.1 hooks.json Update
```json
{
  "hooks": [
    {
      "event": "SessionStart",
      "script": "skills/plan-importer/scripts/detect_plan.py",
      "timeout": 5000,
      "description": "Auto-detect Plan Mode plans",
      "on_result": {
        "found": "prompt_plan_import",
        "not_found": "continue"
      }
    }
  ]
}
```

### 5.2 SessionStart Hook Integration
```
Existing SessionStart Hook:
  1. init_session.py (plugin version check, GUIDELINES.md load)

Added:
  2. detect_plan.py (Plan Mode plan detection)
     └─ If found: Trigger prompt_plan_import
     └─ If not found: Continue normal session
```

## 6. Skill Definition

### 6.1 SKILL.md
```markdown
# plan-importer

Import plans created in Claude Code Plan Mode into the workflow system.

## Capabilities
- Auto-detect Plan Mode output files
- Convert plans to task_plan.md format
- Auto-extract file references → Set Active Context
- Preserve completed step status

## Usage
Automatically runs at SessionStart.
Manual invocation: `/workflow:start --from-plan`

## Configuration
```yaml
plan_paths:
  - ".claude/plan.md"
  - ".claude/plans/current.md"
detection:
  max_age_hours: 24
  min_completion_rate: 0.0
  max_completion_rate: 1.0
```
```

## 7. Command Updates

### 7.1 /workflow:start Extension
```markdown
| Command | Arguments | Description |
|---------|-----------|-------------|
| `/workflow:start` | `[task description]` | Default: Start new task |
| `/workflow:start` | `--from-plan` | Import detected Plan Mode plan |
| `/workflow:start` | `--plan-file <path>` | Specify plan file path |
| `/workflow:start` | `--ignore-plan` | Ignore existing plan, start fresh |
```

## 8. File Structure

```
skills/
└── plan-importer/
    ├── SKILL.md                    # Skill definition
    ├── config.yaml                 # Configuration (paths, detection conditions)
    └── scripts/
        ├── detect_plan.py          # Plan file detection
        ├── parse_plan.py           # Plan Mode format parsing
        ├── convert_plan.py         # task_plan.md conversion
        └── prompt_templates/
            └── import_prompt.md    # User prompt template
```

## 9. Edge Cases

| Situation | Handling |
|-----------|----------|
| Multiple plan files exist | Prioritize most recently modified, provide selection UI |
| Plan 100% complete | Suggest import but show "already completed" |
| Parse failure | Display raw content + suggest manual editing |
| Plan file deleted | Ignore `.claude/plan_import_dismissed`, normal session |
| Git branch switch | Consider branch-specific plan separation (future) |

## 10. Future Enhancements

- [ ] Branch-specific plan auto-linking
- [ ] Multiple plan file merge capability
- [ ] Plan Mode ↔ task_plan.md bidirectional sync
- [ ] Plan version history management
