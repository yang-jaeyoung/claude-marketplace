---
description: Evolve high-confidence instincts into reusable commands, skills, or agents
argument-hint: "[--preview|--create <type>] [--id <instinct-id>]"
allowed-tools: Read, Write, Glob, Bash
---

# /cw:evolve - Instinct Evolution System

Transform learned instincts into reusable commands, skills, or agents.

## Overview

The evolve command analyzes accumulated instincts and proposes evolution paths:
- **Command**: User-invoked workflows (3+ steps)
- **Skill**: Auto-applied patterns (behavioral rules)
- **Agent**: Complex multi-step processes (specialized reasoning)

## Usage

```bash
/cw:evolve                    # Interactive: preview and select
/cw:evolve --preview          # Preview candidates only
/cw:evolve --create command   # Create command from selected instinct
/cw:evolve --create skill     # Create skill from selected instinct
/cw:evolve --create agent     # Create agent from selected instinct
/cw:evolve --id <instinct-id> # Evolve specific instinct
```

## Execution Protocol

### Phase 1: Load Evolution Candidates

```bash
# Step 1: List high-confidence instincts (>= 0.6)
python3 "${CLAUDE_PLUGIN_ROOT}/skills/insight-collector/scripts/instinct-cli.py" list
```

**Parse output and extract:**
- Instinct IDs with confidence >= 0.6
- Evidence count
- Domain classification

### Phase 2: Categorize Candidates

For each high-confidence instinct, analyze:

| Pattern | Evolution Type |
|---------|---------------|
| Trigger: "when user asks", "on request" + 3+ steps | **Command** |
| Trigger: context-based ("when editing", "before commit") + auto-apply | **Skill** |
| Complex multi-step reasoning + decision points | **Agent** |
| Simple preference or single action | **None** (keep as instinct) |

**Classification Logic:**

```yaml
Command Indicators:
  trigger_keywords: ["when user", "on request", "user asks for"]
  action_structure: "step 1 → step 2 → step 3"
  min_steps: 3
  user_interaction: true

Skill Indicators:
  trigger_keywords: ["when editing", "before", "after", "during"]
  action_structure: "automatically apply"
  min_steps: 1
  user_interaction: false

Agent Indicators:
  trigger_keywords: ["analyze", "diagnose", "investigate", "decide"]
  action_structure: "if/then decision tree"
  complexity: high
  reasoning_required: true
```

### Phase 3: Present Candidates

Display evolution candidates grouped by type:

```markdown
=== Instinct Evolution Candidates ===

Analyzing instincts with confidence >= 0.6...

Found N evolution candidates:

## Command Candidates (User-Triggered Workflows)

1. [instinct-id-1] (confidence: 0.85, evidence: 12)
   Trigger: when user asks to safely modify code
   Action: Search with Grep → Edit file → Verify syntax → Run tests
   → Evolve to: /cw:safe-modify

2. [instinct-id-2] (confidence: 0.78, evidence: 8)
   Trigger: when user requests feature exploration
   Action: Read docs → Analyze usage → Propose approach
   → Evolve to: /cw:explore-feature

## Skill Candidates (Auto-Applied Patterns)

3. [instinct-id-3] (confidence: 0.72, evidence: 15)
   Trigger: before committing code
   Action: Check for console.log, verify tests run, lint
   → Evolve to: pre-commit-quality skill

4. [instinct-id-4] (confidence: 0.68, evidence: 9)
   Trigger: after editing a component file
   Action: Update corresponding test file, check imports
   → Evolve to: component-test-sync skill

## Agent Candidates (Complex Reasoning)

5. [instinct-id-5] (confidence: 0.80, evidence: 10)
   Trigger: when debugging complex failures
   Action: Trace stack → Bisect history → Analyze dependencies → Propose fix
   → Evolve to: debug-detective agent

═══════════════════════════════════════════

Select an instinct to evolve (enter ID) or 'q' to quit:
```

### Phase 4: Interactive Selection

When user provides an instinct ID:

1. **Show details:**
   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/skills/insight-collector/scripts/instinct-cli.py" show <instinct-id>
   ```

2. **Confirm evolution type:**
   ```
   This instinct will evolve into: [Command|Skill|Agent]

   Rationale: [Why this type was chosen]

   Proceed? (y/n):
   ```

3. **If yes, proceed to Phase 5**

### Phase 5: Generate Scaffolding

#### For Command:

```bash
# Create directory
mkdir -p .caw/evolved/commands/

# Generate command file
cat > .caw/evolved/commands/{name}.md << 'EOF'
---
description: Auto-generated from instinct {instinct-id}
argument-hint: "[args]"
allowed-tools: Read, Write, Glob, Bash
---

# /cw:{name} - Evolved Command

## Origin

**Source Instinct:** {instinct-id}
**Confidence:** {confidence}
**Evidence:** {evidence_count} observations
**Generated:** {timestamp}

## Purpose

{Derived from instinct trigger}

## Workflow

{Step-by-step workflow from instinct action}

### Step 1: {First Step}

{Details}

### Step 2: {Second Step}

{Details}

### Step 3: {Third Step}

{Details}

## Usage Examples

```bash
/cw:{name} {example-args}
```

## Boundaries

**Will:**
- {Action 1}
- {Action 2}

**Will Not:**
- {Limitation 1}
- {Limitation 2}

---

*This command was auto-generated from learned behavior patterns.*
*Edit `.caw/evolved/commands/{name}.md` to customize.*
EOF
```

#### For Skill:

```bash
# Create skill directory
mkdir -p .caw/evolved/skills/{name}/

# Generate SKILL.md
cat > .caw/evolved/skills/{name}/SKILL.md << 'EOF'
---
name: {name}
description: Auto-generated from instinct {instinct-id}
allowed-tools: Read, Write, Glob
---

# {Name} - Evolved Skill

## Origin

**Source Instinct:** {instinct-id}
**Confidence:** {confidence}
**Evidence:** {evidence_count} observations
**Generated:** {timestamp}

## Activation Trigger

{Derived from instinct trigger}

## Behavioral Rule

When activated, this skill:

1. {Action step 1}
2. {Action step 2}
3. {Action step 3}

## Confidence Threshold

This skill was generated with confidence: **{confidence}**

High confidence indicates reliable pattern observed across multiple sessions.

## Integration

This skill activates automatically when the trigger condition is met.
No user interaction required.

---

*This skill was auto-generated from learned behavior patterns.*
*Edit `.caw/evolved/skills/{name}/SKILL.md` to customize.*
EOF
```

#### For Agent:

```bash
# Create agents directory
mkdir -p .caw/evolved/agents/

# Generate agent file
cat > .caw/evolved/agents/{name}.md << 'EOF'
---
name: {name}
description: Auto-generated from instinct {instinct-id}
model: sonnet
tier: sonnet
tools:
  - Read
  - Write
  - Glob
  - Grep
whenToUse: |
  {Derived from instinct trigger}

  <example>
  {Usage example}
  </example>
---

# {Name} - Evolved Agent

## Origin

**Source Instinct:** {instinct-id}
**Confidence:** {confidence}
**Evidence:** {evidence_count} observations
**Generated:** {timestamp}

## Specialization

{Domain expertise from instinct}

## Decision Logic

```
{Decision tree derived from instinct actions}
```

## Workflow

### Phase 1: Analysis
{First phase actions}

### Phase 2: Processing
{Second phase actions}

### Phase 3: Delivery
{Final phase actions}

## Boundaries

**Will:**
- {Capability 1}
- {Capability 2}

**Will Not:**
- {Limitation 1}
- {Limitation 2}

## Model Routing

**Default:** Sonnet (balanced performance)
**Override:** Use Opus for complex cases via model parameter

---

*This agent was auto-generated from learned behavior patterns.*
*Edit `.caw/evolved/agents/{name}.md` to customize.*
EOF
```

### Phase 6: Update Tracking

After creating evolved component:

```json
// Update .caw/instincts/index.json
{
  "instincts": [...],
  "evolutions": [
    {
      "timestamp": "2026-01-27T20:00:00Z",
      "source_instinct": "{instinct-id}",
      "confidence": 0.85,
      "evidence_count": 12,
      "evolution_type": "command|skill|agent",
      "target_path": ".caw/evolved/{type}/{name}.md",
      "generated_name": "{name}"
    }
  ]
}
```

**Confirmation output:**

```
✅ Evolution Complete

Source: {instinct-id}
Type: {Command|Skill|Agent}
Generated: .caw/evolved/{type}/{name}.md

Next steps:
1. Review the generated file
2. Customize if needed
3. Test: /cw:{name} (for commands)

Note: Evolved components are local to this project.
To share globally, copy to plugin directory.
```

## Classification Examples

### Example 1: Command Evolution

**Instinct:**
```yaml
id: search-modify-verify
trigger: "when user requests code modification"
action: "Use Grep to find location → Edit file → Grep again to verify"
confidence: 0.85
evidence_count: 12
```

**Evolution:** Command → `/cw:safe-edit`

**Rationale:** User-triggered, 3-step workflow, high confidence

---

### Example 2: Skill Evolution

**Instinct:**
```yaml
id: pre-commit-check
trigger: "before git commit is executed"
action: "Check for debug statements, verify tests pass, run linter"
confidence: 0.72
evidence_count: 15
```

**Evolution:** Skill → `pre-commit-quality`

**Rationale:** Context-triggered, automatic application, no user interaction

---

### Example 3: Agent Evolution

**Instinct:**
```yaml
id: debug-complex-error
trigger: "when encountering multi-layer error"
action: "Trace stack → Analyze dependencies → Check recent changes → Bisect if needed → Propose fix"
confidence: 0.80
evidence_count: 10
```

**Evolution:** Agent → `debug-detective`

**Rationale:** Multi-step reasoning, decision tree, complex domain knowledge

## Implementation Guidelines

### When executing /cw:evolve:

1. **Always check for .caw/instincts/index.json first**
   - If missing, inform user to run instinct analysis first

2. **Use python3 explicitly (not python)**
   - Cross-platform compatibility (macOS requires python3)

3. **Parse instinct-cli.py output carefully**
   - Extract confidence scores
   - Match threshold (>= 0.6)
   - Group by domain

4. **Interactive mode is default**
   - Show candidates
   - Let user select
   - Confirm before generating

5. **Generate meaningful names**
   - Commands: kebab-case (e.g., safe-edit, explore-feature)
   - Skills: kebab-case (e.g., pre-commit-quality)
   - Agents: kebab-case (e.g., debug-detective)

6. **Preserve instinct metadata**
   - Track confidence score
   - Track evidence count
   - Link back to source instinct

7. **Write to correct locations**
   - Commands: `.caw/evolved/commands/{name}.md`
   - Skills: `.caw/evolved/skills/{name}/SKILL.md`
   - Agents: `.caw/evolved/agents/{name}.md`

8. **Update evolution tracking**
   - Add to instincts/index.json evolutions array
   - Preserve full audit trail

## Preview Mode (--preview)

When `--preview` flag is used, show candidates but don't proceed to generation:

```
=== Evolution Preview ===

8 high-confidence instincts found

Command Candidates: 2
Skill Candidates: 3
Agent Candidates: 1

Not eligible: 2 (confidence < 0.6)

Run without --preview to select and evolve.
```

## Specific Instinct Evolution (--id)

When `--id <instinct-id>` is provided:

1. Load specific instinct
2. Verify confidence >= 0.6
3. Classify evolution type
4. Skip candidate list
5. Proceed directly to generation with confirmation

## Boundaries

**Will:**
- Analyze all instincts and classify by evolution type
- Present clear categorization and rationale
- Generate well-structured scaffolding with metadata
- Track evolution history in index
- Preserve source instinct (mark as evolved, don't delete)

**Will Not:**
- Evolve low-confidence instincts (< 0.6)
- Automatically overwrite existing evolved components
- Delete or modify source instincts
- Deploy to global plugin directory without user action
- Generate components with duplicate names

## Error Handling

| Error | Resolution |
|-------|-----------|
| No instincts found | Guide user to run observations and analysis |
| No high-confidence candidates | Suggest continuing to gather observations |
| Instinct ID not found | List available IDs |
| Evolution target already exists | Ask to overwrite or rename |
| Invalid evolution type | Show valid types: command, skill, agent |

## Related Commands

- **instinct-cli.py analyze** - Generate instincts from observations
- **instinct-cli.py list** - View all instincts
- **instinct-cli.py show** - View instinct details
- **/cw:status** - Shows evolved components
- **/cw:sync** - Sync evolved components to Serena memory

## Example Session

```bash
# User runs evolve
/cw:evolve

# System lists candidates
=== 3 Command Candidates, 2 Skill Candidates ===
...

# User selects instinct
> safe-modify-pattern-a1b2c3

# System shows details and confirms
Evolving to: Command (/cw:safe-modify)
Proceed? (y/n): y

# System generates
✅ Created: .caw/evolved/commands/safe-modify.md
Test with: /cw:safe-modify

# User tests
/cw:safe-modify src/auth.ts
```
