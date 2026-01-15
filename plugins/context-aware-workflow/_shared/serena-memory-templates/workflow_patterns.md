# Workflow Patterns Template

Template for `workflow_patterns` Serena memory.

## Structure

```markdown
# Workflow Patterns

## Metadata
- **Last Updated**: YYYY-MM-DDTHH:MM:SSZ
- **Source**: Ralph Loop / Reflect Skill
- **Total Patterns**: [N]

## Successful Approaches

### [Task Type]: [Pattern Name]

**Context**: When to use this pattern
- [Condition 1]
- [Condition 2]

**Approach**:
1. [Step 1]
2. [Step 2]
3. [Step 3]

**Expected Outcome**:
- [Result 1]
- [Result 2]

**Caveats**:
- [Warning 1]
- [Warning 2]

**Evidence**:
- Used in: [Task name], [Date]
- Result: [Success/Partial]

---

### Feature Development: TDD Approach

**Context**:
- New feature with clear requirements
- Testable functionality

**Approach**:
1. Write failing test for expected behavior
2. Implement minimum code to pass
3. Refactor for clarity
4. Add edge case tests
5. Document usage

**Expected Outcome**:
- High test coverage
- Confident refactoring ability
- Clear documentation

**Caveats**:
- May feel slower initially
- Requires upfront requirement clarity

---

### Bug Fixing: Reproduce First

**Context**:
- Bug report received
- Unclear reproduction steps

**Approach**:
1. Create minimal reproduction case
2. Write failing test for bug
3. Identify root cause with debugger
4. Fix with minimal change
5. Add regression test

**Expected Outcome**:
- Bug verified fixed
- No regression in future

**Caveats**:
- Some bugs hard to reproduce
- May need production data access

## Anti-patterns

### What to Avoid

1. **Skipping Tests for "Simple" Changes**
   - Why it fails: Simple changes often have hidden complexity
   - Better approach: Write at least one happy path test

2. **Large Refactors Without Incremental Commits**
   - Why it fails: Hard to identify breaking change
   - Better approach: Small, focused commits

3. **Ignoring TypeScript Errors with `any`**
   - Why it fails: Hides type bugs until runtime
   - Better approach: Properly type or use unknown

## Planning Patterns

### For Complex Features
1. Break into phases
2. Identify dependencies
3. Start with highest-risk item
4. Regular checkpoints

### For Refactoring
1. Ensure test coverage first
2. Make changes in small steps
3. Run tests after each change
4. Commit frequently

## Execution Patterns

### For Implementation
1. Read existing patterns first
2. Follow established conventions
3. Add tests alongside code
4. Update documentation

### For Debugging
1. Reproduce consistently
2. Isolate the problem
3. Form hypothesis
4. Test hypothesis
5. Document finding
```

## Usage

**Save (Reflect Skill)**:
```
write_memory("workflow_patterns", content)
```

**Load (Planner)**:
```
read_memory("workflow_patterns")
```

## When to Update

- Ralph Loop completes with insights
- New successful pattern discovered
- Anti-pattern identified
- Existing pattern refined

## Pattern Evolution

Patterns should evolve based on experience:
1. **Emerging**: New pattern, limited evidence
2. **Established**: Multiple successful uses
3. **Refined**: Updated based on learnings
4. **Deprecated**: No longer recommended
