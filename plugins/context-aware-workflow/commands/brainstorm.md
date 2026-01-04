---
description: Interactive requirements discovery through Socratic dialogue and brainstorming
---

# /caw:brainstorm - Requirements Discovery

Start an interactive brainstorming session to transform vague ideas into structured requirements using the Ideator agent.

## Usage

```bash
/caw:brainstorm "your idea or feature description"
/caw:brainstorm                      # Resume or review existing brainstorm
/caw:brainstorm --reset              # Start fresh, archive existing
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
[4] Proceed to design (/caw:design)
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
   • /caw:design --ui for UX/UI design
   • /caw:design --arch for architecture design
   • /caw:start to begin implementation planning
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

## Examples

### Example 1: New Feature Ideation

```bash
/caw:brainstorm "사용자 알림 시스템"
```

**Ideator Questions**:
```
📋 Requirements Discovery

I'd like to understand your notification system needs better.

1. What types of notifications are needed?
   □ Email  □ Push  □ In-app  □ SMS

2. Who receives notifications?
   - All users
   - Specific user roles
   - Based on user preferences

3. What triggers notifications?
   - System events
   - User actions
   - Scheduled tasks

4. What's the expected volume?
   - Low (< 100/day)
   - Medium (100-10K/day)
   - High (> 10K/day)
```

### Example 2: Resume Existing

```bash
/caw:brainstorm
```

```
📋 Existing Brainstorm Found

Project: User Notification System
Status: Draft
Confidence: Medium
Last Updated: 10분 전

Requirements discovered:
- ✅ P0: 3 items defined
- 🔄 P1: 2 items (needs refinement)
- ⏳ Open Questions: 4 items

[1] Continue refining  [2] View summary  [3] Proceed to design
```

### Example 3: Complex Project

```bash
/caw:brainstorm "AI 기반 코드 리뷰 시스템"
```

**Multi-round Discovery**:
```
Round 1: Problem Understanding
- "What specific code quality issues do you want to catch?"
- "Who will use this system? (developers, tech leads, CI/CD)"

Round 2: Scope Definition
- "Should this integrate with existing tools? (GitHub, GitLab)"
- "What languages need support?"

Round 3: Success Criteria
- "How will you measure if this is successful?"
- "What's the acceptable false positive rate?"
```

## Edge Cases

### No Input Provided (No Existing Brainstorm)

```
💡 Start Brainstorming

Provide an idea or feature to explore:

Example:
  /caw:brainstorm "사용자 인증 시스템 개선"
  /caw:brainstorm "실시간 협업 기능 추가"

Or describe what you're thinking about, and I'll help
structure your thoughts through guided questions.
```

### User Wants to Skip Brainstorming

```
ℹ️ Brainstorming is Optional

You can skip directly to:
  • /caw:design --ui for UX/UI design
  • /caw:design --arch for architecture design
  • /caw:start for implementation planning

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
  • Run /caw:brainstorm to continue discovery
  • Consider stakeholder interviews
```

## Integration

- **Creates**: `.caw/brainstorm.md`
- **Invokes**: Ideator agent via Task tool
- **Uses**: AskUserQuestion for interactive discovery
- **Suggests**: `/caw:design`, `/caw:start`
- **Standalone**: Can be used without other CAW commands
