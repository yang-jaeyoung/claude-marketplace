---
description: Run automated Review-Fix cycles until quality criteria are met
argument-hint: "[--step N.M] [--max-cycles N] [--severity minor|major|critical]"
---

# /cw:qaloop - Quality Assurance Loop

Automated build → review → fix cycle that continues until quality criteria are satisfied or max cycles reached.

## Usage

```bash
/cw:qaloop                                 # QA current step
/cw:qaloop --step 2.3                      # QA specific step
/cw:qaloop --phase 2                       # QA entire phase
/cw:qaloop --max-cycles 5 --severity major # Custom settings
/cw:qaloop --continue                      # Resume from saved state
```

## Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `--step N.M` | Current | Target specific step |
| `--phase N` | - | Run QA on entire phase |
| `--max-cycles` | 3 | Maximum iterations |
| `--severity` | major | Minimum severity to fix |
| `--exit-on` | major | Exit when no issues at this level |
| `--no-build` | false | Skip build step |
| `--deep` | false | Use Opus for diagnosis |

## Architecture

```
BUILD → REVIEW → FIX → EXIT CHECK → (loop or exit)

Exit Conditions:
✅ No critical/major issues
⏱️ Max cycles reached
🔁 Same issues 3 times (stalled)
❌ Build failure persists
```

## Agent Selection

| Phase | Standard | Deep (--deep) |
|-------|----------|---------------|
| Build | cw:Builder (Sonnet) | cw:Builder (Sonnet) |
| Diagnose | cw:Reviewer (Sonnet) | cw:reviewer-opus |
| Fix | cw:Fixer (Sonnet) | cw:Fixer (Opus) |

## Execution Flow

1. **Initialize**: Load target step/phase, set config, select agents
2. **Build**: Execute step and run tests
3. **Review**: Analyze for issues (critical/major/minor)
4. **Exit Check**: Pass if no issues at threshold; stall if same issues 3x
5. **Fix**: Apply fixes for issues above severity threshold
6. **Record**: Log cycle results with issue hashes for stall detection
7. **Repeat**: Until exit condition met

## Stall Detection

Issues are hashed (`file_path + line_range + issue_type + severity`). If same hashes appear 3 cycles in a row, loop stalls requiring manual intervention.

## Output

```
🔄 /cw:qaloop --step 2.3

Cycle 1/3 ━━━━━━━━━━━━━━━━━━━━
  📦 Build...     ✅ Success
  🔍 Review...    ⚠️ 2 major, 1 minor
  🔧 Fixing...    ✅ 2 fixed

Cycle 2/3 ━━━━━━━━━━━━━━━━━━━━
  📦 Build...     ✅ Success
  🔍 Review...    ✅ 0 major, 1 minor

✅ QA Loop Complete
  Cycles: 2/3 | Fixed: 2/3 | Remaining: 1 minor
```

Stalled loops show persistent issue location and suggest `/cw:diagnose` or manual fix.

## State File

State saved in `.caw/qaloop_state.json`:
- Target step/phase and config
- Current cycle and stall count
- Per-cycle results with issue hashes

## Integration

```bash
/cw:loop "Task" --qa-each-step    # QA after each step
/cw:auto "Feature"                # Auto mode includes QA
/cw:next && /cw:qaloop            # QA after next step
```

## Comparison

| Feature | /cw:qaloop | /cw:loop | /cw:review |
|---------|------------|----------|------------|
| Purpose | Quality gates | Task completion | One-time review |
| Iteration | Review-Fix cycles | Build iterations | Single pass |
| Auto-fix | ✅ Yes | ✅ Optional | ❌ No |
| Best for | Quality assurance | Task execution | Manual review |

## Related

- [Model Routing](../_shared/model-routing.md)
- [Loop Command](./loop.md)
- [Review Command](./review.md)
