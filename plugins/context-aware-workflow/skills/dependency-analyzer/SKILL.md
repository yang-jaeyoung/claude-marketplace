---
name: dependency-analyzer
description: Analyzes task_plan.md to build dependency graph and identify parallel execution opportunities
allowed-tools: Read, Glob
forked-context: false
---

# Dependency Analyzer Skill

Analyzes `.caw/task_plan.md` to identify which phases and steps can run in parallel and builds execution groups for optimal workflow.

## When to Use

- Before executing `--parallel` or `--worktree` modes in `/caw:next`
- When `/caw:status` needs to show parallel execution opportunities
- When planning worktree creation for isolated parallel execution
- **When analyzing Phase-level dependencies for multi-terminal parallel work**

## Core Functions

### 0. Parse Phase Dependencies (NEW)

Read `.caw/task_plan.md` and extract Phase-level dependencies:

```markdown
### Phase 1: Setup
**Phase Deps**: -

### Phase 2: Core Implementation
**Phase Deps**: phase 1

### Phase 3: API Layer
**Phase Deps**: phase 1

### Phase 4: Integration
**Phase Deps**: phase 2, phase 3
```

**Parsing Output**:
```json
{
  "phases": {
    "1": { "name": "Setup", "deps": [], "status": "complete" },
    "2": { "name": "Core Implementation", "deps": [1], "status": "pending" },
    "3": { "name": "API Layer", "deps": [1], "status": "pending" },
    "4": { "name": "Integration", "deps": [2, 3], "status": "pending" }
  }
}
```

### 1. Parse Step Dependencies

Read `.caw/task_plan.md` and extract:
- Step ID (e.g., `2.1`, `3.2`)
- Status (⏳, 🔄, ✅, ❌, ⏭️, 🌳)
- Deps column value
- Notes for parallel markers (⚡)

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

### 5. Identify Parallel Phases (NEW)

Phases that can run in parallel worktrees:
- Same Phase Deps (both depend on `phase 1`)
- All Phase Deps are complete

```
function findParallelPhases(plan):
  phases = parsePhaseDeps(plan)
  parallel_groups = []

  for each phase:
    if phase.deps_all_complete:
      group = phases.filter(p =>
        p.deps === phase.deps &&
        p.status === "pending"
      )
      if group.length > 1:
        parallel_groups.append(group)

  return parallel_groups

Example:
  Phase 2 (deps: phase 1) ─┐
                           ├─ Can run in parallel
  Phase 3 (deps: phase 1) ─┘

  Phase 4 (deps: phase 2, 3) → Must wait
```

### 6. Worktree Recommendations

For worktree isolation, recommend when:
- **Phases have same Phase Deps** (primary recommendation)
- Steps modify large portions of same subsystem
- Steps are complex enough to warrant full isolation

**Phase-Based Recommendation (PRIMARY)**:
```json
{
  "phase_worktrees": {
    "phase-2": {
      "branch": "caw/phase-2",
      "deps_satisfied": true,
      "can_parallel_with": ["phase-3"]
    },
    "phase-3": {
      "branch": "caw/phase-3",
      "deps_satisfied": true,
      "can_parallel_with": ["phase-2"]
    }
  },
  "merge_order": ["phase-2", "phase-3", "phase-4"]
}
```

**Step-Based Recommendation (Legacy)**:
```json
{
  "step_worktrees": {
    "caw-step-2.2": ["2.2"],
    "caw-step-2.3": ["2.3"]
  },
  "merge_point": "2.4"
}
```

## Output Format

### Summary Output (for /caw:status)

```
📊 Dependency Analysis

## Phase-Level Parallel (NEW)
Phases with same Phase Deps can run in parallel worktrees:

  Phase Deps: phase 1
    → Phase 2 ⏳ (5 steps)
    → Phase 3 ⏳ (4 steps)

  💡 /caw:worktree create phase 2,3

## Step-Level Parallel
Runnable Steps (can execute now):
  ⚡ 2.2 - Implement token generation
  ⚡ 2.3 - Implement token validation

  💡 /caw:next --parallel phase 2

Blocked:
  ❌ Phase 4 - waiting for: Phase 2, Phase 3
  ❌ 2.4 - waiting for: 2.2, 2.3
```

### JSON Output (for internal use)

```json
{
  "analysis_timestamp": "2026-01-16T14:30:00Z",
  "phase_analysis": {
    "total_phases": 4,
    "completed_phases": [1],
    "runnable_phases": [2, 3],
    "blocked_phases": {
      "4": [2, 3]
    },
    "parallel_phase_groups": [
      {
        "phases": [2, 3],
        "shared_deps": [1],
        "can_parallel_worktree": true
      }
    ]
  },
  "step_analysis": {
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
    ]
  },
  "worktree_suggestions": {
    "phase_based": [
      {
        "directory": ".worktrees/phase-2",
        "branch": "caw/phase-2",
        "phase": 2
      },
      {
        "directory": ".worktrees/phase-3",
        "branch": "caw/phase-3",
        "phase": 3
      }
    ],
    "step_based": []
  },
  "merge_order": ["phase-2", "phase-3", "phase-4"]
}
```

## Dependency Resolution Algorithm

### Phase-Level Analysis (NEW)

```
function parsePhaseDeps(plan):
  // Extract "**Phase Deps**: X" from each phase header
  phases = {}
  for each phase_section in plan:
    phase_num = extractPhaseNumber(phase_section)
    deps_line = findLine("**Phase Deps**:", phase_section)
    deps = parseDepsNotation(deps_line)  // "-" | "phase N" | "phase N, M"
    phases[phase_num] = {
      deps: deps,
      status: calculatePhaseStatus(phase_section)
    }
  return phases

function isPhaseComplete(phase_num, phases):
  phase = phases[phase_num]
  return phase.status === "complete"

function findRunnablePhases(phases):
  return phases.filter(p =>
    p.status === "pending" &&
    p.deps.every(d => isPhaseComplete(d, phases))
  )

function groupParallelPhases(runnablePhases):
  // Group phases with identical Phase Deps
  groups = {}
  for each phase in runnablePhases:
    key = phase.deps.sort().join(",")
    if key not in groups:
      groups[key] = []
    groups[key].append(phase)
  return groups.values().filter(g => g.length > 1)
```

### Step-Level Analysis

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

### Merge Order Calculation

```
function calculateMergeOrder(worktrees):
  // Topological sort based on Phase Deps
  graph = buildDependencyGraph(worktrees)
  return topologicalSort(graph)

Example:
  Input: [phase-2, phase-3, phase-4]
  Graph:
    phase-2 -> []
    phase-3 -> []
    phase-4 -> [phase-2, phase-3]
  Output: [phase-2, phase-3, phase-4]
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
