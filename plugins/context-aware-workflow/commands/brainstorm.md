---
description: Interactive requirements discovery through Socratic dialogue and brainstorming
argument-hint: "[topic] [--reset]"
---

# /cw:brainstorm - Requirements Discovery

Start an interactive brainstorming session to transform vague ideas into structured requirements using the Ideator agent.

## Usage

```bash
/cw:brainstorm "your idea or feature description"
/cw:brainstorm                      # Resume or review existing
/cw:brainstorm --reset              # Start fresh, archive existing
```

## Workflow

1. **Check Existing**: Look for `.caw/brainstorm.md`
2. **Invoke Ideator**: Task tool with Ideator agent for Socratic dialogue
3. **Interactive Discovery**: Clarifying questions (max 5 at a time)
4. **Generate Output**: Create `.caw/brainstorm.md`

## Ideator Process

| Round | Focus | Sample Questions |
|-------|-------|------------------|
| 1 | Problem | "What types of notifications?" (Email/Push/In-app/SMS) |
| 2 | Scope | "What triggers? What volume?" (Low/Med/High) |
| 3 | Success | "How to measure success? Acceptable false positive rate?" |

## Output Format

`.caw/brainstorm.md` structure:
- Metadata (created, status, confidence)
- Problem Statement
- Target Users
- Requirements (P0/P1/P2)
- Constraints
- Open Questions
- Risks & Mitigations
- Recommended Direction

## Output

```
📝 Brainstorm Complete

Created: .caw/brainstorm.md
Confidence: [Low/Medium/High]

Summary:
- Problem: [1-2 sentence summary]
- Users: [target users]
- Must Have: [count] requirements

💡 Next: /cw:design --ui | /cw:design --arch | /cw:start
```

## Edge Cases

| Scenario | Behavior |
|----------|----------|
| No input, no existing | Prompt for idea or show examples |
| Skip brainstorming | Suggest /cw:design or /cw:start |
| Low confidence result | List open questions, recommend continued discovery |

## Integration

- **Creates**: `.caw/brainstorm.md`
- **Invokes**: Ideator agent via Task tool
- **Uses**: AskUserQuestion for interactive discovery
- **Suggests**: `/cw:design`, `/cw:start`
