---
description: Advanced automated QA with intelligent diagnosis and targeted fixes
argument-hint: "[--target build|test|lint|all] [--max-cycles N] [--deep]"
---

# /cw:ultraqa - Ultra Quality Assurance

Advanced QA automation that intelligently diagnoses build/test/lint failures and applies targeted fixes.

## Usage

```bash
/cw:ultraqa                       # Auto-detect and fix all
/cw:ultraqa --target build        # Fix build errors
/cw:ultraqa --target test         # Fix failing tests
/cw:ultraqa --target lint         # Fix linting issues
/cw:ultraqa --max-cycles 5        # Custom max attempts
/cw:ultraqa --deep                # Use Opus for analysis
/cw:ultraqa --continue            # Resume from state
```

## Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `--target` | all | build, test, lint, or all |
| `--max-cycles` | 5 | Maximum fix attempts |
| `--deep` | false | Deep diagnosis (Opus) |
| `--continue` | false | Resume from saved state |

## Architecture

```
DETECT → DIAGNOSE → FIX → VERIFY → (loop or exit)
```

## Agent Selection

| Phase | Standard | Deep (--deep) |
|-------|----------|---------------|
| Diagnose | cw:reviewer-opus | cw:architect (Opus) |
| Fix | cw:Fixer (Opus) | cw:Fixer (Opus) |

## Detection

| Target | Command | Output |
|--------|---------|--------|
| Build | `npm run build`, `cargo build`, etc. | Error list with file/line |
| Test | `npm test`, `pytest`, etc. | Failure list with assertions |
| Lint | `eslint`, `pylint`, etc. | Issue list with rule/severity |

## Fix Strategy

| Type | Priority | Approach |
|------|----------|----------|
| Build errors | High | Type annotations, imports, syntax |
| Test failures | Medium | Fix implementation or update expectations |
| Lint issues | Low | Auto-fix first, then manual |

## Output

```
🔬 /cw:ultraqa --target all

Detecting issues...
  📦 Build:  ❌ 3 errors
  🧪 Tests:  ⚠️ 2 failures
  📝 Lint:   ⚠️ 5 issues

Cycle 1/5 ━━━━━━━━━━━━━━━━━━━━
  🔍 Diagnosing...
  🔧 Fixing: types.ts, auth.ts
  🔄 Verifying: Build ✅, Tests ⚠️

Cycle 2/5 ━━━━━━━━━━━━━━━━━━━━
  🔍 Diagnosing test failures...
  🔧 Fixing: handler.ts, handler.test.ts
  🔄 Verifying: Tests ✅

Cycle 3/5 ━━━━━━━━━━━━━━━━━━━━
  📝 Lint --fix: 4 auto-fixed, 1 manual

✅ UltraQA Complete
  Build: 3 → 0 ✅
  Tests: 2 → 0 ✅
  Lint: 5 → 1 ⚠️ (manual fix needed)
```

## State File

State saved in `.caw/ultraqa_state.json`:
- Target type and config
- Initial and final issue counts
- Per-cycle diagnosis and fixes

## Comparison

| Feature | /cw:ultraqa | /cw:qaloop |
|---------|-------------|------------|
| Focus | Build/Test/Lint | Code quality |
| Diagnosis | Deep root cause | Standard review |
| Best for | CI failures | Quality gates |

## Integration

```bash
/cw:next phase 1 && /cw:ultraqa --target build  # After implementation
/cw:ultraqa --target all --deep && /cw:review   # Before merge
```

## Related

- [Model Routing](../_shared/model-routing.md)
- [QA Loop](./qaloop.md)
- [Review Command](./review.md)
