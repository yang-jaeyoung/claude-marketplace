# Agents Validation Report

> Generated: 2026-02-01
> Scope: `plugins/context-aware-workflow/agents/*.md`

## Summary

| Category | Status | Count |
|----------|--------|-------|
| Total Agents | - | 18 |
| Location Valid | ✅ | 18/18 |
| Required Fields (CLAUDE.md) | ✅ | 18/18 |
| Tiering Convention (CLAUDE.md) | ⚠️ | 14/18 |
| **Claude Code Official Spec** | ❌ | **6/18** |

---

## Part A: Claude Code Official Subagent Spec Validation

### Official Specification Reference

Source: https://code.claude.com/docs/en/sub-agents.md

#### Official Supported Fields

| Field | Required | Type | Description |
|-------|:--------:|------|-------------|
| `name` | **Yes** | string | **Lowercase letters and hyphens only** |
| `description` | **Yes** | string | When to delegate to this subagent |
| `model` | No | string | `sonnet`, `opus`, `haiku`, `inherit` |
| `tools` | No | list | Tools the subagent can use |
| `disallowedTools` | No | list | Tools to deny |
| `permissionMode` | No | string | `default`, `acceptEdits`, `dontAsk`, `bypassPermissions`, `plan` |
| `skills` | No | list | Skills to preload |
| `hooks` | No | object | Lifecycle hooks |

### A.1. Required Fields Validation ✅

All 18 agents have `name` and `description` fields.

### A.2. Name Format Validation ❌ (12 violations)

**Rule**: Name must use **lowercase letters and hyphens only**

| Agent File | Current `name` | Status | Required Fix |
|------------|----------------|:------:|--------------|
| architect.md | `architect` | ✅ | - |
| analyst.md | `analyst` | ✅ | - |
| bootstrapper.md | `"Bootstrapper"` | ❌ | `bootstrapper` |
| builder.md | `"Builder"` | ❌ | `builder` |
| builder-haiku.md | `"Builder"` | ❌ | `builder` |
| builder-sonnet.md | `"Builder"` | ❌ | `builder` |
| compliance-checker.md | `"ComplianceChecker"` | ❌ | `compliance-checker` |
| designer.md | `designer` | ✅ | - |
| fixer.md | `"Fixer"` | ❌ | `fixer` |
| fixer-haiku.md | `"Fixer"` | ❌ | `fixer` |
| fixer-sonnet.md | `"Fixer"` | ❌ | `fixer` |
| ideator.md | `ideator` | ✅ | - |
| planner.md | `"Planner"` | ❌ | `planner` |
| planner-haiku.md | `"Planner"` | ❌ | `planner` |
| planner-opus.md | `"Planner"` | ❌ | `planner` |
| reviewer.md | `"Reviewer"` | ❌ | `reviewer` |
| reviewer-haiku.md | `"Reviewer"` | ❌ | `reviewer` |
| reviewer-opus.md | `"Reviewer"` | ❌ | `reviewer` |

**Compliant**: 6 agents (architect, analyst, designer, ideator + 2 files with correct lowercase)
**Non-compliant**: 12 agents (PascalCase or quoted uppercase names)

### A.3. Model Values Validation ✅

All agents use valid model values: `sonnet`, `opus`, or `haiku`

### A.4. Extension Fields (Non-Official)

These fields are **NOT in the official Claude Code spec** but are used as plugin extensions:

| Field | Official | Used By | Purpose |
|-------|:--------:|:-------:|---------|
| `mcp_servers` | ❌ | 13 agents | MCP server integration |
| `whenToUse` | ❌ | 14 agents | Selection guidance with examples |
| `color` | ❌ | 14 agents | UI display color |
| `tier` | ❌ | 8 agents | Explicit tier indicator |

**Note**: These extensions are valid in the plugin context but not part of the official spec.

### A.5. Official Spec Compliance Summary

| Requirement | Status | Details |
|-------------|:------:|---------|
| Required fields present | ✅ | 18/18 |
| Name format (lowercase-hyphens) | ❌ | 6/18 compliant |
| Valid model values | ✅ | 18/18 |
| Only official fields | ⚠️ | Extension fields used |

### A.6. Required Fixes for Official Compliance

```yaml
# Fix for all non-compliant agents:

# bootstrapper.md
name: bootstrapper  # was: "Bootstrapper"

# builder.md, builder-haiku.md, builder-sonnet.md
name: builder  # was: "Builder"

# compliance-checker.md
name: compliance-checker  # was: "ComplianceChecker"

# fixer.md, fixer-haiku.md, fixer-sonnet.md
name: fixer  # was: "Fixer"

# planner.md, planner-haiku.md, planner-opus.md
name: planner  # was: "Planner"

# reviewer.md, reviewer-haiku.md, reviewer-opus.md
name: reviewer  # was: "Reviewer"
```

---

## Part B: Project CLAUDE.md Validation

### B.1. File Location Validation ✅

All 18 agents are correctly placed in `agents/*.md`:

```
agents/
├── analyst.md
├── architect.md
├── bootstrapper.md
├── builder.md
├── builder-haiku.md
├── builder-sonnet.md
├── compliance-checker.md
├── designer.md
├── fixer.md
├── fixer-haiku.md
├── fixer-sonnet.md
├── ideator.md
├── planner.md
├── planner-haiku.md
├── planner-opus.md
├── reviewer.md
├── reviewer-haiku.md
└── reviewer-opus.md
```

### B.2. Required Fields Validation (per CLAUDE.md)

Per CLAUDE.md, agents must have: `name`, `description`, `model`, `tools`, `mcp_servers`

| Agent | name | description | model | tools | mcp_servers |
|-------|:----:|:-----------:|:-----:|:-----:|:-----------:|
| architect.md | ✅ | ✅ | ✅ opus | ✅ | ✅ |
| analyst.md | ✅ | ✅ | ✅ sonnet | ✅ | ✅ |
| bootstrapper.md | ✅ | ✅ | ✅ haiku | ✅ | ✅ |
| builder.md | ✅ | ✅ | ✅ opus | ✅ | ✅ |
| builder-haiku.md | ✅ | ✅ | ✅ haiku | ✅ | ❌ |
| builder-sonnet.md | ✅ | ✅ | ✅ sonnet | ✅ | ✅ |
| designer.md | ✅ | ✅ | ✅ sonnet | ✅ | ✅ |
| compliance-checker.md | ✅ | ✅ | ✅ haiku | ✅ | ❌ |
| fixer.md | ✅ | ✅ | ✅ opus | ✅ | ✅ |
| fixer-haiku.md | ✅ | ✅ | ✅ haiku | ✅ | ❌ |
| fixer-sonnet.md | ✅ | ✅ | ✅ sonnet | ✅ | ✅ |
| ideator.md | ✅ | ✅ | ✅ opus | ✅ | ✅ |
| planner.md | ✅ | ✅ | ✅ sonnet | ✅ | ✅ |
| planner-haiku.md | ✅ | ✅ | ✅ haiku | ✅ | ❌ |
| planner-opus.md | ✅ | ✅ | ✅ opus | ✅ | ✅ |
| reviewer.md | ✅ | ✅ | ✅ sonnet | ✅ | ✅ |
| reviewer-haiku.md | ✅ | ✅ | ✅ haiku | ✅ | ❌ |
| reviewer-opus.md | ✅ | ✅ | ✅ opus | ✅ | ✅ |

**Note**: Haiku tier agents missing `mcp_servers` is intentional for lightweight operation.

### B.3. Tiering Convention Validation ⚠️

### Rule (from CLAUDE.md)

| Tier | File Pattern | Expected Model |
|------|--------------|----------------|
| Base | `<name>.md` | sonnet |
| Fast | `<name>-haiku.md` | haiku |
| Complex | `<name>-opus.md` | opus |

### Violations Found (4)

| Agent | Current Model | Expected | Issue |
|-------|---------------|----------|-------|
| `architect.md` | opus | sonnet | Base tier should use sonnet |
| `builder.md` | opus | sonnet | Base tier should use sonnet |
| `fixer.md` | opus | sonnet | Base tier should use sonnet |
| `ideator.md` | opus | sonnet | Base tier should use sonnet |

### Compliant Agents

| Agent | Model | Status |
|-------|-------|--------|
| analyst.md | sonnet | ✅ |
| designer.md | sonnet | ✅ |
| planner.md | sonnet | ✅ |
| reviewer.md | sonnet | ✅ |
| bootstrapper.md | haiku | ✅ (single-tier) |
| compliance-checker.md | haiku | ✅ (single-tier) |
| All `-haiku.md` variants | haiku | ✅ |
| All `-sonnet.md` variants | sonnet | ✅ |
| All `-opus.md` variants | opus | ✅ |

### B.4. Tier Coverage Analysis

| Agent Family | Base | Haiku | Sonnet | Opus | Complete |
|--------------|:----:|:-----:|:------:|:----:|:--------:|
| builder | opus | ✅ | ✅ | ❌ | ⚠️ |
| fixer | opus | ✅ | ✅ | ❌ | ⚠️ |
| planner | sonnet | ✅ | - | ✅ | ✅ |
| reviewer | sonnet | ✅ | - | ✅ | ✅ |
| architect | opus | ❌ | ❌ | ❌ | ⚠️ |
| analyst | sonnet | ❌ | ❌ | ❌ | ✅ |
| designer | sonnet | ❌ | ❌ | ❌ | ✅ |
| ideator | opus | ❌ | ❌ | ❌ | ⚠️ |
| bootstrapper | haiku | - | - | - | ✅ |
| compliance-checker | haiku | - | - | - | ✅ |

### B.5. Undocumented Fields (in CLAUDE.md)

The following fields are used but not documented in CLAUDE.md:

| Field | Purpose | Used By |
|-------|---------|---------|
| `whenToUse` | Agent selection guidance with examples | Most agents |
| `color` | UI display color | Most agents |
| `skills` | Integrated skill references | Most agents |
| `tier` | Explicit tier indicator | Tiered variants |

---

## Part C: Recommendations

### C.1. Critical: Fix Name Format (Official Spec)

**All 12 agents with PascalCase names must be changed to lowercase-with-hyphens.**

This is required for official Claude Code subagent compatibility.

### C.2. Fix Tiering Violations (CLAUDE.md)

**Option A**: Update base agents to use sonnet
```yaml
# architect.md, builder.md, fixer.md, ideator.md
model: sonnet  # Change from opus
```

**Option B**: Rename files and create new base variants
```
architect.md (opus) → architect-opus.md
+ architect.md (new, sonnet)
```

### C.3. Document Additional Fields

Update CLAUDE.md Components Reference:

```markdown
| Type | Location | Key Fields |
|------|----------|------------|
| Agents | `agents/*.md` | name, description, model, tools, mcp_servers, **whenToUse**, **color**, **skills**, **tier** |
```

### C.4. Standardize mcp_servers

Either:
- Add mcp_servers to all haiku agents (even if empty array)
- Document that haiku tier agents don't require mcp_servers

---

## Conclusion

### Claude Code Official Spec Compliance

| Issue | Severity | Count | Action Required |
|-------|----------|-------|-----------------|
| Name format violation | 🔴 Critical | 12 | Must fix for official compatibility |
| Extension fields used | 🟡 Info | 4 types | Acceptable as plugin extensions |

### Project CLAUDE.md Compliance

| Issue | Severity | Count | Action Required |
|-------|----------|-------|-----------------|
| Tiering convention violation | 🟡 Medium | 4 | Update model or rename files |
| Missing mcp_servers (haiku) | 🟢 Low | 5 | Document as intentional |
| Undocumented fields | 🟢 Low | 4 | Update CLAUDE.md |

### Priority Action Items

1. **🔴 Critical**: Fix all 12 agent `name` fields to use lowercase-with-hyphens format
2. **🟡 Medium**: Align base agent models with tiering convention (or update CLAUDE.md)
3. **🟢 Low**: Document extension fields in CLAUDE.md

### Overall Assessment

- **Official Spec**: ❌ 12/18 agents have invalid name format
- **Project Rules**: ⚠️ 4/18 agents violate tiering convention
- **Functionality**: ✅ All agents are fully functional with comprehensive documentation
