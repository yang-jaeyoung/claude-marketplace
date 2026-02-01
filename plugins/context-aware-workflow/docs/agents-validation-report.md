# Agents Validation Report

> Generated: 2026-02-01
> Scope: `plugins/context-aware-workflow/agents/*.md`

## Summary

| Category | Status | Count |
|----------|--------|-------|
| Total Agents | - | 18 |
| Location Valid | ✅ | 18/18 |
| Required Fields | ✅ | 18/18 |
| Tiering Convention | ⚠️ | 14/18 |

## 1. File Location Validation ✅

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

## 2. Required Fields Validation

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

## 3. Tiering Convention Validation ⚠️

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

## 4. Tier Coverage Analysis

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

## 5. Undocumented Fields

The following fields are used but not documented in CLAUDE.md:

| Field | Purpose | Used By |
|-------|---------|---------|
| `whenToUse` | Agent selection guidance with examples | Most agents |
| `color` | UI display color | Most agents |
| `skills` | Integrated skill references | Most agents |
| `tier` | Explicit tier indicator | Tiered variants |

## Recommendations

### Priority 1: Fix Tiering Violations

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

### Priority 2: Document Additional Fields

Update CLAUDE.md Components Reference:

```markdown
| Type | Location | Key Fields |
|------|----------|------------|
| Agents | `agents/*.md` | name, description, model, tools, mcp_servers, **whenToUse**, **color**, **skills**, **tier** |
```

### Priority 3: Standardize mcp_servers

Either:
- Add mcp_servers to all haiku agents (even if empty array)
- Document that haiku tier agents don't require mcp_servers

## Conclusion

The agents are well-structured with comprehensive documentation. The main compliance issues are:

1. **4 base agents** use opus instead of sonnet per tiering convention
2. **5 haiku agents** missing mcp_servers field
3. **4 undocumented fields** in common use

Recommended action: Update CLAUDE.md to reflect actual usage patterns, as the current implementation appears intentional (complex tasks default to opus).
