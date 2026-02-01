# Agent Registry

Comprehensive catalog of all available agents for CAW workflows.

## Overview

This registry documents all agents available in the CAW ecosystem with their tiers, capabilities, and use cases.

## CAW Agents

### Core Agents (Tiered)

#### Planner
Plans and structures tasks into executable steps.

| Variant | File | Model | Complexity Range |
|---------|------|-------|------------------|
| `cw:Planner` | `planner.md` | Sonnet | 0.3 - 0.7 (default) |
| `cw:planner-haiku` | `planner-haiku.md` | Haiku | ≤ 0.3 |
| `cw:planner-opus` | `planner-opus.md` | Opus | > 0.7 |

**Capabilities**:
- Task decomposition
- Phase structuring
- Dependency analysis
- Effort estimation

---

#### Builder
Implements code following TDD approach.

| Variant | File | Model | Complexity Range |
|---------|------|-------|------------------|
| `cw:Builder` | `builder.md` | Opus | > 0.7 (default) |
| `cw:builder-haiku` | `builder-haiku.md` | Haiku | ≤ 0.3 |
| `cw:builder-sonnet` | `builder-sonnet.md` | Sonnet | 0.3 - 0.7 |

**Capabilities**:
- TDD implementation
- Test-first development
- Code generation
- Pattern following

---

#### Reviewer
Reviews code for quality, bugs, and best practices.

| Variant | File | Model | Complexity Range |
|---------|------|-------|------------------|
| `cw:Reviewer` | `reviewer.md` | Sonnet | 0.3 - 0.7 (default) |
| `cw:reviewer-haiku` | `reviewer-haiku.md` | Haiku | ≤ 0.3 |
| `cw:reviewer-opus` | `reviewer-opus.md` | Opus | > 0.7 |

**Capabilities**:
- Code quality analysis
- Bug detection
- Security scanning
- Performance review

**Special Flags**:
- `--deep`: Thorough analysis (uses Opus tier)
- `--security`: Security-focused review
- `--quick`: Fast style check only (uses Haiku tier)

---

#### Fixer
Applies fixes based on review feedback.

| Variant | File | Model | Complexity Range |
|---------|------|-------|------------------|
| `cw:Fixer` | `fixer.md` | Opus | > 0.7 (default) |
| `cw:fixer-haiku` | `fixer-haiku.md` | Haiku | ≤ 0.3 |
| `cw:fixer-sonnet` | `fixer-sonnet.md` | Sonnet | 0.3 - 0.7 |

**Capabilities**:
- Auto-fixing lint issues
- Refactoring
- Pattern extraction
- Security patching

---

### Specialized Agents (Single Tier)

#### Bootstrapper
| ID | File | Model |
|----|------|-------|
| `cw:Bootstrapper` | `bootstrapper.md` | Haiku |

**Purpose**: Environment initialization, project detection, `.caw/` setup

**Capabilities**:
- Project type detection
- Framework identification
- Directory structure setup
- Context manifest creation

---

#### Architect
| ID | File | Model |
|----|------|-------|
| `cw:architect` | `architect.md` | Opus |

**Purpose**: System design, component architecture, technical decisions

**Capabilities**:
- Architecture design
- Component diagrams
- Data model design
- Technical trade-offs

---

#### Designer
| ID | File | Model |
|----|------|-------|
| `cw:designer` | `designer.md` | Sonnet |

**Purpose**: UX/UI design, wireframes, user flows

**Capabilities**:
- Wireframe creation
- User flow mapping
- Interaction design
- UI specifications

---

#### Ideator
| ID | File | Model |
|----|------|-------|
| `cw:ideator` | `ideator.md` | Sonnet |

**Purpose**: Requirements discovery, Socratic dialogue, brainstorming

**Capabilities**:
- Requirement gathering
- Brainstorming facilitation
- Clarifying questions
- Scope definition

---

#### ComplianceChecker
| ID | File | Model |
|----|------|-------|
| `cw:ComplianceChecker` | `compliance-checker.md` | Sonnet |

**Purpose**: Guideline validation, convention checking

**Capabilities**:
- Rule validation
- Convention checking
- Style enforcement
- Compliance reporting

---

## Agent Selection Matrix

### By Task Type

| Task Type | Recommended Agent |
|-----------|-------------------|
| Planning | `cw:Planner` |
| Implementation | `cw:Builder` |
| Code Review | `cw:Reviewer` |
| Bug Fixing | `cw:Fixer` |
| Architecture | `cw:architect` |
| Research | `cw:Planner` + WebSearch |
| Testing | `cw:Reviewer` + Bash |
| Security | `cw:reviewer-opus` |

### By Complexity

| Complexity | Planner | Builder | Reviewer | Fixer |
|------------|---------|---------|----------|-------|
| Low (≤0.3) | Haiku | Haiku | Haiku | Haiku |
| Medium (0.3-0.7) | Sonnet | Sonnet | Sonnet | Sonnet |
| High (>0.7) | Opus | Opus | Opus | Opus |

## Usage Examples

### Basic Agent Invocation

```markdown
## Using CAW Agent
Task tool:
  subagent_type: "cw:Builder"
  model: "sonnet"
  prompt: "Implement the login feature..."
```

### Tiered Agent Selection

```markdown
## Automatic tier selection based on complexity
complexity = calculate_complexity(task)

IF complexity <= 0.3:
  agent = "cw:builder-haiku"
ELIF complexity <= 0.7:
  agent = "cw:builder-sonnet"
ELSE:
  agent = "cw:Builder"  # Opus default
```

## Integration Points

### With Model Routing

Tier selection integrates with model routing:

```markdown
tier = calculate_tier(task_complexity)
agent = get_tiered_agent("builder", tier)
// Returns: cw:builder-haiku, cw:builder-sonnet, or cw:Builder
```

### With Commands

Commands use registry for agent selection:

| Command | Primary Agent | Fallback Logic |
|---------|---------------|----------------|
| `/cw:next` | `cw:Builder` | Tier-based |
| `/cw:review` | `cw:Reviewer` | Tier-based |
| `/cw:fix` | `cw:Fixer` | Tier-based |
| `/cw:qaloop` | Multiple | Tier-based |
| `/cw:ultraqa` | `cw:reviewer-opus` | Deep analysis |
| `/cw:research` | `cw:Planner` | WebSearch tools |

## Schema Reference

See [agent-registry.schema.json](./schemas/agent-registry.schema.json) for the complete schema definition.

## Related Documentation

- [Model Routing](./model-routing.md) - Tier selection
- [Parallel Execution](./parallel-execution.md) - Concurrent agent execution
