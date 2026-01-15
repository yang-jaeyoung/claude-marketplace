---
name: dependency-analyzer
description: Analyzes task_plan.md to build dependency graph and identify parallel execution opportunities
allowed-tools: Read, Glob
forked-context: false
---

# Dependency Analyzer Skill

Analyzes `.caw/task_plan.md` to identify which steps can run in parallel and builds execution groups for optimal workflow.

## When to Use

- Before executing `--parallel` or `--worktree` modes in `/caw:next`
- When `/caw:status` needs to show parallel execution opportunities
- When planning worktree creation for isolated parallel execution

## Core Functions

### 1. Parse Dependencies

Read `.caw/task_plan.md` and extract:
- Step ID (e.g., `2.1`, `3.2`)
- Status (⏳, 🔄, ✅, ❌, ⏭️)
- Deps column value
- Notes for parallel markers (⚡병렬가능)

### 2. Build Dependency Graph

Transform Deps notation into execution order:

```
Input:
| 2.1 | Task A | ⏳ | 1.* |
| 2.2 | Task B | ⏳ | 2.1 |
| 2.3 | Task C | ⏳ | 2.1 |

Output Graph:
{
  "2.1": { "deps": ["1.*"], "dependents": ["2.2", "2.3"] },
  "2.2": { "deps": ["2.1"], "dependents": [] },
  "2.3": { "deps": ["2.1"], "dependents": [] }
}
```

### 3. Identify Runnable Steps

A step is **runnable** if:
- Status is ⏳ (Pending)
- All dependencies are ✅ (Complete)

```
Runnable = steps.filter(s =>
  s.status === "⏳" &&
  s.deps.every(d => isComplete(d))
)
```

### 4. Group Parallel Opportunities

Steps that can run simultaneously:
- Same dependency set (both depend on `2.1`)
- No mutual exclusion (`!` notation)
- Different target files (avoid conflicts)

```
Parallel Groups:
[
  { "group": 1, "steps": ["2.2", "2.3"], "reason": "both depend on 2.1, different files" },
  { "group": 2, "steps": ["3.2", "3.3"], "reason": "both depend on 3.1, marked ⚡" }
]
```

### 5. Worktree Recommendations

For worktree isolation, recommend when:
- Steps modify large portions of same subsystem
- Steps are complex enough to warrant full isolation
- Multiple phases can progress independently

```
Worktree Suggestion:
{
  "worktree_1": ["2.2", "2.4"],   // Auth branch
  "worktree_2": ["2.3", "2.5"],   // API branch
  "merge_point": "3.1"            // Requires both complete
}
```

## Output Format

### Summary Output (for /caw:status)

```
📊 Dependency Analysis

Runnable Steps (can execute now):
  ⚡ 2.2 - Implement token generation
  ⚡ 2.3 - Implement token validation

Parallel Groups:
  Group 1: [2.2, 2.3] - same deps, different files

Blocked Steps:
  ❌ 2.4 - waiting for: 2.2, 2.3
  ❌ 3.1 - waiting for: Phase 2

Worktree Suggestion:
  💡 Steps 2.2 and 2.3 can run in separate worktrees
     /caw:worktree create --steps 2.2,2.3
```

### JSON Output (for internal use)

```json
{
  "analysis_timestamp": "2024-01-15T14:30:00Z",
  "total_steps": 12,
  "completed": 4,
  "runnable": ["2.2", "2.3"],
  "blocked": {
    "2.4": ["2.2", "2.3"],
    "3.1": ["2.*"]
  },
  "parallel_groups": [
    {
      "steps": ["2.2", "2.3"],
      "can_worktree": true,
      "conflict_risk": "low"
    }
  ],
  "worktree_suggestions": [
    {
      "branch_name": "caw/step-2.2",
      "steps": ["2.2"],
      "merge_into": "main"
    }
  ]
}
```

## Dependency Resolution Algorithm

```
function resolvePhaseWildcard(dep):
  // "1.*" -> all steps in Phase 1
  if dep matches "N.*":
    return allStepsInPhase(N)
  return [dep]

function isComplete(dep):
  resolved = resolvePhaseWildcard(dep)
  return resolved.every(step => step.status === "✅")

function findRunnableSteps(plan):
  return plan.steps.filter(step =>
    step.status === "⏳" &&
    step.deps.every(d => isComplete(d))
  )

function groupParallel(runnableSteps):
  groups = []
  for each pair of steps:
    if canRunParallel(step1, step2):
      addToGroup(groups, step1, step2)
  return groups

function canRunParallel(s1, s2):
  // Same dependencies
  if s1.deps !== s2.deps: return false
  // No mutual exclusion
  if s1.deps.includes("!" + s2.id): return false
  // Different files (check Notes column)
  if s1.targetFile === s2.targetFile: return false
  return true
```

## Integration Points

- **`/caw:next --parallel`**: Uses runnable steps and parallel groups
- **`/caw:next --worktree`**: Uses worktree suggestions
- **`/caw:status`**: Displays dependency summary
- **`/caw:merge`**: Uses merge points for ordering

## Error Handling

### Circular Dependencies
```
⚠️ Circular dependency detected:
  2.1 → 2.3 → 2.1

Please fix task_plan.md:
  Step 2.1 depends on 2.3, but 2.3 depends on 2.1
```

### Missing Dependencies
```
⚠️ Missing dependency reference:
  Step 2.4 depends on "2.9" which doesn't exist

Available steps: 2.1, 2.2, 2.3
```

### Orphaned Steps
```
ℹ️ Orphaned steps (no dependencies, not depended on):
  - 1.1: Consider if this should be "-" (independent)
```
