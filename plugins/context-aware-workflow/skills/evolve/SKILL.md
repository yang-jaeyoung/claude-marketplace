---
name: evolve
description: Transform high-confidence instincts into reusable commands, skills, or agents
allowed-tools: Read, Write, Glob, Bash
---

# Evolve Skill

Transform learned instincts from observation patterns into production-ready commands, skills, or agents.

## Purpose

The evolve skill analyzes accumulated instincts and provides evolution paths:
- **Command**: User-invoked workflows (3+ steps, explicit user trigger)
- **Skill**: Auto-applied patterns (behavioral rules, context-based activation)
- **Agent**: Complex multi-step processes (specialized reasoning, decision trees)

## Invocation

```bash
/cw:evolve                           # Interactive preview and selection
/cw:evolve --preview                 # Show candidates only, no creation
/cw:evolve --create <type> <id> <name>  # Generate specific evolution
/cw:evolve --id <instinct-id>        # Show details and suggest evolution
```

## Skill Behavior

### Step 1: Load Evolution Candidates

Use the insight-collector integration API to load high-confidence instincts:

```python
# Execute via Python
python3 -c "
import sys
sys.path.insert(0, '${CLAUDE_PLUGIN_ROOT}/skills/insight-collector/lib')
from integration import list_instincts, get_evolution_candidates
from evolution import get_evolution_candidates_list

# Load instincts with minimum confidence 0.6
instincts = list_instincts(min_confidence=0.6)

# Categorize into commands/skills/agents
candidates = get_evolution_candidates_list(instincts)

print(f'Commands: {len(candidates[\"commands\"])}')
print(f'Skills: {len(candidates[\"skills\"])}')
print(f'Agents: {len(candidates[\"agents\"])}')
"
```

### Step 2: Display Candidates (Default/Preview Mode)

When called without arguments or with `--preview`, show categorized candidates:

```markdown
═══════════════════════════════════════════════════════════
                   EVOLUTION CANDIDATES
═══════════════════════════════════════════════════════════

Found N high-confidence instincts eligible for evolution.

📦 COMMANDS (User-triggered workflows)
──────────────────────────────────────────────────────────
ID: safe-modify-pattern-abc12345
   Trigger: "when user requests safe code modification"
   Action: Grep → Edit → Verify → Test
   Confidence: [████████░░] 0.85
   Evidence: 12 observations
   → Evolve to: /cw:safe-modify

ID: feature-explore-def67890
   Trigger: "when user asks to explore feature"
   Action: Read docs → Analyze usage → Propose approach
   Confidence: [███████░░░] 0.72
   Evidence: 8 observations
   → Evolve to: /cw:explore-feature

📋 SKILLS (Auto-applicable patterns)
──────────────────────────────────────────────────────────
ID: pre-commit-quality-ghi34567
   Trigger: "before git commit is executed"
   Action: Check console.log → Verify tests → Lint
   Confidence: [███████░░░] 0.72
   Evidence: 15 observations
   → Evolve to: pre-commit-quality skill

ID: component-sync-jkl78901
   Trigger: "after editing a component file"
   Action: Update test file → Check imports
   Confidence: [██████░░░░] 0.68
   Evidence: 9 observations
   → Evolve to: component-test-sync skill

🤖 AGENTS (Complex reasoning)
──────────────────────────────────────────────────────────
ID: debug-detective-mno23456
   Trigger: "when debugging complex failures"
   Action: Trace stack → Bisect history → Analyze deps → Propose fix
   Confidence: [████████░░] 0.80
   Evidence: 10 observations
   → Evolve to: debug-detective agent

══════════════════════════════════════════════════════════
To evolve an instinct, use:
  /cw:evolve --create <type> <instinct-id> <name>

Example:
  /cw:evolve --create command safe-modify-pattern-abc12345 safe-modify
══════════════════════════════════════════════════════════
```

### Step 3: Classification Logic

Instincts are automatically categorized based on these patterns:

```yaml
Command Indicators:
  trigger_keywords: ["when user", "on request", "user asks for", "when requesting"]
  action_structure: "step 1 → step 2 → step 3" (multi-step)
  min_steps: 3
  user_interaction: required

Skill Indicators:
  trigger_keywords: ["when editing", "before", "after", "during", "automatically"]
  action_structure: "automatically apply" (1+ steps)
  auto_activation: true
  user_interaction: optional

Agent Indicators:
  trigger_keywords: ["analyze", "diagnose", "investigate", "decide", "complex"]
  action_structure: "if/then decision tree"
  complexity: high
  reasoning_required: true
```

### Step 4: Show Instinct Details (--id mode)

When called with `--id <instinct-id>`, show detailed information:

```markdown
═══════════════════════════════════════════════════════════
                  INSTINCT DETAILS
═══════════════════════════════════════════════════════════

ID: safe-modify-pattern-abc12345
Domain: workflow
Confidence: 0.85 [████████░░]
Evidence: 12 observations

## Trigger
"when user requests safe code modification"

## Action
1. Use Grep to find exact location
2. Edit file with precise change
3. Grep again to verify change
4. Run tests to confirm functionality

## Suggested Evolution

Type: Command (/cw:safe-modify)
Rationale: User-triggered, multi-step workflow, high confidence

To generate:
  /cw:evolve --create command safe-modify-pattern-abc12345 safe-modify
══════════════════════════════════════════════════════════
```

### Step 5: Create Evolution (--create mode)

When called with `--create <type> <instinct-id> <name>`:

```python
# Execute creation
python3 -c "
import sys
sys.path.insert(0, '${CLAUDE_PLUGIN_ROOT}/skills/insight-collector/lib')
from integration import list_instincts
from evolution import create_evolution, track_evolution

# Load instinct
instincts = list_instincts()
instinct = next((i for i in instincts if i['id'] == '<instinct-id>'), None)

if not instinct:
    print('Error: Instinct not found')
    sys.exit(1)

# Validate confidence
if instinct.get('confidence', 0) < 0.6:
    print(f'Error: Confidence too low ({instinct[\"confidence\"]:.2f} < 0.6)')
    sys.exit(1)

# Create evolution
result = create_evolution(instinct, '<type>', '<name>')

if result['success']:
    # Track evolution
    track_evolution(
        instinct['id'],
        result['type'],
        result['path'],
        result['name'],
        instinct['confidence'],
        instinct.get('evidence_count', 0)
    )
    print(f'Success: {result[\"path\"]}')
else:
    print(f'Error: {result[\"error\"]}')
    sys.exit(1)
"
```

### Step 6: Success Output

After successful evolution:

```markdown
✅ Evolution Complete!
──────────────────────────────────────────────────────────
Type:       command
Name:       safe-modify
Source:     safe-modify-pattern-abc12345 (confidence: 0.85)
Created:    .caw/evolved/commands/safe-modify.md

To test:    /cw:safe-modify <args>
To customize: Edit .caw/evolved/commands/safe-modify.md

The evolved component includes:
  • Origin metadata (source instinct, confidence, evidence)
  • Workflow steps extracted from action patterns
  • Usage examples and boundaries
  • Integration guidelines
──────────────────────────────────────────────────────────

Next steps:
1. Review the generated file
2. Customize workflow steps if needed
3. Test with: /cw:safe-modify <args>
4. Share globally: Copy to plugin directory if desired
```

## Evolution Scaffolds

### Command Scaffold

Generated at `.caw/evolved/commands/{name}.md`:

```yaml
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

## Purpose
{trigger description}

## Workflow
### Step 1: {First Step}
{details}

### Step 2: {Second Step}
{details}

## Boundaries
**Will:** {capabilities}
**Will Not:** {limitations}
```

### Skill Scaffold

Generated at `.caw/evolved/skills/{name}/SKILL.md`:

```yaml
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

## Activation Trigger
{trigger description}

## Behavioral Rule
When activated, this skill:
1. {action step 1}
2. {action step 2}
3. {action step 3}

## Integration
This skill activates automatically when the trigger condition is met.
```

### Agent Scaffold

Generated at `.caw/evolved/agents/{name}.md`:

```yaml
---
name: {name}
description: Auto-generated from instinct {instinct-id}
model: sonnet
tier: sonnet
whenToUse: |
  {trigger description}
tools:
  - Read
  - Write
  - Glob
  - Grep
---

# {Name} - Evolved Agent

## Origin
**Source Instinct:** {instinct-id}
**Confidence:** {confidence}

## Specialization
{domain expertise}

## Decision Logic
{decision tree from action}

## Workflow
### Phase 1: Analysis
### Phase 2: Processing
### Phase 3: Delivery
```

## Error Handling

### No Instincts Found

```markdown
⚠️ No instincts available

No instincts have been captured yet.

To start collecting instincts:
1. Run observations: Work normally, instincts are recorded
2. Analyze: /cw:analyze-instincts (if available)
3. Return here: /cw:evolve

Instincts accumulate over multiple sessions and represent
patterns that appear repeatedly in your workflow.
```

### Invalid Instinct ID

```markdown
⚠️ Instinct not found: {id}

Available instinct IDs:
  • safe-modify-pattern-abc12345 (confidence: 0.85)
  • pre-commit-check-def67890 (confidence: 0.72)
  • debug-detective-ghi34567 (confidence: 0.80)

Use: /cw:evolve --id <instinct-id>
```

### Confidence Too Low

```markdown
⚠️ Cannot evolve: Confidence too low

Instinct: {id}
Current confidence: 0.45
Minimum required: 0.60

This instinct needs more evidence before evolution.
Continue working with this pattern and the confidence
will increase as more observations accumulate.

Check again after: {estimated_observations} more observations
```

### File Already Exists

```markdown
⚠️ Evolution target already exists

Type: command
Name: safe-modify
Path: .caw/evolved/commands/safe-modify.md

Options:
1. Choose a different name
2. Delete existing file first
3. Edit existing file manually

Would you like to:
[1] Try different name
[2] Overwrite (requires --force flag)
[3] Cancel
```

### Invalid Evolution Type

```markdown
⚠️ Invalid evolution type: {type}

Valid types:
  • command  - User-triggered workflows (3+ steps)
  • skill    - Auto-applicable patterns (behavioral rules)
  • agent    - Complex reasoning (decision trees)

Usage: /cw:evolve --create <type> <instinct-id> <name>
Example: /cw:evolve --create command abc12345 safe-modify
```

## Integration with Insight Collector

This skill uses the insight-collector Python modules:

```python
from insight_collector.lib.evolution import (
    create_evolution,           # Generate scaffold
    classify_instinct,          # Categorize instinct
    get_evolution_candidates_list,  # Get all candidates
    track_evolution,            # Record in index
)

from insight_collector.lib.integration import (
    list_instincts,             # Load instincts
    get_evolution_candidates,   # Get high-confidence candidates
)
```

## State Management

### Evolution Tracking

Evolutions are tracked in `.caw/instincts/index.json`:

```json
{
  "instincts": [...],
  "evolutions": [
    {
      "timestamp": "2026-01-27T20:00:00Z",
      "source_instinct": "safe-modify-pattern-abc12345",
      "confidence": 0.85,
      "evidence_count": 12,
      "evolution_type": "command",
      "target_path": ".caw/evolved/commands/safe-modify.md",
      "generated_name": "safe-modify"
    }
  ]
}
```

### Evolution Directory Structure

```
.caw/
├── evolved/
│   ├── commands/
│   │   ├── safe-modify.md
│   │   └── explore-feature.md
│   ├── skills/
│   │   ├── pre-commit-quality/
│   │   │   └── SKILL.md
│   │   └── component-sync/
│   │       └── SKILL.md
│   └── agents/
│       └── debug-detective.md
└── instincts/
    └── index.json (evolution tracking)
```

## Related Commands

- **instinct-cli.py analyze** - Generate instincts from observations
- **instinct-cli.py list** - View all instincts
- **instinct-cli.py show** - View instinct details
- **/cw:status** - Shows evolved components
- **/cw:sync** - Sync evolved components to memory systems

## Boundaries

**Will:**
- Analyze all instincts and classify by evolution type
- Present clear categorization with confidence levels
- Generate well-structured scaffolding with metadata
- Track evolution history in index
- Preserve source instinct (mark as evolved, don't delete)
- Provide helpful error messages and guidance

**Will Not:**
- Evolve low-confidence instincts (< 0.6)
- Automatically overwrite existing evolved components
- Delete or modify source instincts
- Deploy to global plugin directory without user action
- Generate components with duplicate names
- Force evolution on unsuitable instincts

## Examples

### Example 1: Preview Candidates

```bash
/cw:evolve --preview
```

Shows all high-confidence instincts grouped by type, no interaction.

### Example 2: Interactive Evolution

```bash
/cw:evolve
```

Shows candidates, prompts for selection, confirms before generating.

### Example 3: Direct Evolution

```bash
/cw:evolve --create command safe-modify-pattern-abc12345 safe-modify
```

Generates command directly without preview.

### Example 4: Instinct Details

```bash
/cw:evolve --id safe-modify-pattern-abc12345
```

Shows detailed information about specific instinct and suggests evolution.
