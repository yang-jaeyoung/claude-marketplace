---
description: Interactive requirements discovery through Socratic dialogue and brainstorming
argument-hint: "[topic] [--reset]"
---

# /cw:brainstorm - Requirements Discovery

Start an interactive brainstorming session to transform vague ideas into structured requirements using the Ideator agent.

## Usage

```bash
/cw:brainstorm "your idea or feature description"
/cw:brainstorm                      # Resume or review existing brainstorm
/cw:brainstorm --reset              # Start fresh, archive existing
```

## Behavior

### Step 1: Check Existing Brainstorm

1. Look for `.caw/brainstorm.md`
2. If found and no new input:

```
📋 Existing Brainstorm Found

Project: [Title from brainstorm.md]
Status: Draft / Refined / Approved
Last Updated: [timestamp]

[1] Continue refining
[2] View summary
[3] Start fresh (archive existing)
[4] Proceed to design (/cw:design)
```

### Step 2: Invoke Ideator Agent

Call the Ideator agent via Task tool:

```markdown
## Ideator Agent Invocation

**Input**: [User's idea/description]

**Existing Context**:
- Brainstorm: [path if exists]
- Codebase patterns: [detected from project]

**Instructions**:
1. Engage in Socratic dialogue to understand requirements
2. Use AskUserQuestion for interactive discovery
3. Explore problem space, solution space, and edge cases
4. Document findings in .caw/brainstorm.md
```

### Step 3: Interactive Discovery

The Ideator agent will:

1. **Ask clarifying questions** (max 5 at a time)
2. **Explore systematically**:
   - Who are the users?
   - What problem does this solve?
   - What are the constraints?
3. **Synthesize discoveries** into structured format

### Step 4: Generate Output

Create `.caw/brainstorm.md`:

```
📝 Brainstorm Complete

Created: .caw/brainstorm.md

## Summary
- Problem: [1-2 sentence summary]
- Users: [target users]
- Must Have: [count] requirements
- Open Questions: [count] items

## Confidence: [Low/Medium/High]

💡 Next Steps:
   • /cw:design --ui for UX/UI design
   • /cw:design --arch for architecture design
   • /cw:start to begin implementation planning
```

## Output Format

### `.caw/brainstorm.md` Structure

```
.caw/
└── brainstorm.md
    ├── Metadata (created, status, confidence)
    ├── Problem Statement
    ├── Target Users
    ├── Requirements (P0/P1/P2)
    ├── Constraints
    ├── Open Questions
    ├── Risks & Mitigations
    ├── Ideas Explored
    └── Recommended Direction
```

## Example

```bash
/cw:brainstorm "사용자 알림 시스템"
```

**Ideator Process**: Problem Understanding → Scope Definition → Success Criteria

**Question Categories**:
| Round | Focus | Sample Questions |
|-------|-------|------------------|
| 1 | Problem | "What types of notifications?" (Email/Push/In-app/SMS) |
| 2 | Scope | "What triggers? What volume?" (Low/Med/High) |
| 3 | Success | "How to measure success? Acceptable false positive rate?" |

**Variants:**
- `(no args)` - Resume existing brainstorm or view summary
- `--reset` - Archive existing and start fresh

## Edge Cases

### No Input Provided (No Existing Brainstorm)

```
💡 Start Brainstorming

Provide an idea or feature to explore:

Example:
  /cw:brainstorm "사용자 인증 시스템 개선"
  /cw:brainstorm "실시간 협업 기능 추가"

Or describe what you're thinking about, and I'll help
structure your thoughts through guided questions.
```

### User Wants to Skip Brainstorming

```
ℹ️ Brainstorming is Optional

You can skip directly to:
  • /cw:design --ui for UX/UI design
  • /cw:design --arch for architecture design
  • /cw:start for implementation planning

Brainstorming is recommended for:
  - Vague or complex requirements
  - New features without clear scope
  - Projects needing stakeholder alignment
```

### Low Confidence Result

```
⚠️ Brainstorm Complete (Low Confidence)

Several areas need more clarity:

Open Questions (High Priority):
1. Target user group not defined
2. Success metrics unclear
3. Technical constraints unknown

Recommendations:
  • Answer open questions before proceeding
  • Run /cw:brainstorm to continue discovery
  • Consider stakeholder interviews
```

## Integration

- **Creates**: `.caw/brainstorm.md`
- **Invokes**: Ideator agent via Task tool
- **Uses**: AskUserQuestion for interactive discovery
- **Suggests**: `/cw:design`, `/cw:start`
- **Standalone**: Can be used without other CAW commands
