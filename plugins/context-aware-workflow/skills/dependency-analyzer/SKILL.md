---
name: dependency-analyzer
description: Analyzes task_plan.md to build dependency graph and identify parallel execution opportunities
allowed-tools: Read, Glob
forked-context: false
---

# Dependency Analyzer

Identifies phases/steps that can run in parallel and builds execution groups.

## When to Use

- Before `--parallel` or `--worktree` modes in `/cw:next`
- When `/cw:status` shows parallel opportunities
- When planning multi-terminal parallel work

## Core Functions

### 1. Parse Phase Dependencies

```markdown
### Phase 2: Core Implementation
**Phase Deps**: phase 1

### Phase 3: API Layer
**Phase Deps**: phase 1
```

→ Phases 2 & 3 can run in parallel (same Phase Deps)

### 2. Parse Step Dependencies

```
| 2.1 | Task A | ⏳ | 1.* |  → depends on all Phase 1 steps
| 2.2 | Task B | ⏳ | 2.1 |  → depends on 2.1
| 2.3 | Task C | ⏳ | 2.1 |  → depends on 2.1
```

→ Steps 2.2 & 2.3 can run in parallel

### 3. Runnable Detection

Step is **runnable** if: Status = ⏳ AND all deps are ✅

### 4. Parallel Grouping

Parallel if: Same dependency set, no mutual exclusion, different target files

## Output Format

```
📊 Dependency Analysis

Phase-Level Parallel:
  Phase Deps: phase 1
    → Phase 2 ⏳ (5 steps)
    → Phase 3 ⏳ (4 steps)
  💡 /cw:worktree create phase 2,3

Step-Level Parallel:
  ⚡ 2.2, 2.3 - both depend on 2.1
  💡 /cw:next --parallel phase 2

Blocked:
  ❌ Phase 4 - waiting for: Phase 2, 3
  ❌ 2.4 - waiting for: 2.2, 2.3
```

## Algorithms

```python
# Phase parallel: same deps, all deps complete
parallel_phases = [p for p in phases if p.deps == target.deps and all_complete(p.deps)]

# Step parallel: same deps, no conflict
can_parallel = (s1.deps == s2.deps) and (s1.target != s2.target) and no_exclusion(s1, s2)

# Merge order: topological sort
merge_order = topological_sort(dependency_graph)
```

## Integration

- `/cw:next --parallel`: Uses runnable steps
- `/cw:next --worktree`: Uses worktree suggestions
- `/cw:status`: Displays dependency summary
- `/cw:merge`: Uses merge order

## Error Handling

| Error | Message |
|-------|---------|
| Circular | ⚠️ 2.1 → 2.3 → 2.1 circular |
| Missing | ⚠️ Step 2.4 depends on "2.9" (doesn't exist) |
| Orphaned | ℹ️ Step has no deps and no dependents |
