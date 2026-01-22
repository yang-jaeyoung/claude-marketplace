# Unified Agent Registry

Comprehensive catalog of all available agents for CAW and OMC integration.

## Overview

This registry documents all agents available in the CAW ecosystem, including native CAW agents and OMC agents when the oh-my-claudecode plugin is installed.

## Agent Namespaces

| Namespace | Source | Always Available |
|-----------|--------|------------------|
| `cw:` | CAW Plugin | ✅ Yes |
| `omc:` | OMC Plugin | ❌ Requires OMC |

## CAW Native Agents

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

## OMC Agents (When Available)

These agents are available when the oh-my-claudecode plugin is installed.

### Research & Analysis

#### omc:researcher
| Model | CAW Fallback |
|-------|--------------|
| Sonnet | `cw:Planner` + WebSearch |

**Purpose**: External documentation research, API exploration

**Capabilities**:
- Documentation research
- API exploration
- Library comparison
- Best practice research

---

#### omc:scientist
| Model | CAW Fallback |
|-------|--------------|
| Sonnet | `cw:Builder` + Bash |

**Purpose**: Data analysis, hypothesis testing, experimentation

**Capabilities**:
- Data analysis
- Hypothesis testing
- Experiment design
- Results interpretation

---

#### omc:analyst
| Model | CAW Fallback |
|-------|--------------|
| Opus | `cw:planner-opus` |

**Purpose**: Deep analysis, pattern recognition, insights

**Capabilities**:
- Pattern recognition
- Trend analysis
- Insight generation
- Strategic recommendations

---

### Exploration & Navigation

#### omc:explore
| Model | CAW Fallback |
|-------|--------------|
| Haiku | Task(Explore) |

**Purpose**: Codebase exploration, file discovery, pattern finding

**Capabilities**:
- Fast codebase search
- Pattern matching
- File discovery
- Structure mapping

---

### Execution & Building

#### omc:executor
| Model | CAW Fallback |
|-------|--------------|
| Sonnet | `cw:Builder` |

**Purpose**: Focused code implementation, build execution

**Capabilities**:
- Code implementation
- Build execution
- Test running
- Deployment tasks

---

#### omc:build-fixer
| Model | CAW Fallback |
|-------|--------------|
| Sonnet | `cw:Fixer` |

**Purpose**: Build error fixing, compilation issues

**Capabilities**:
- Build error diagnosis
- Compilation fixes
- Dependency resolution
- Configuration repair

---

### Quality Assurance

#### omc:qa-tester
| Model | CAW Fallback |
|-------|--------------|
| Sonnet | `cw:Reviewer` + Bash |

**Purpose**: Test execution, quality verification

**Capabilities**:
- Test execution
- Coverage analysis
- Regression testing
- Quality gates

---

#### omc:critic
| Model | CAW Fallback |
|-------|--------------|
| Opus | `cw:reviewer-opus` |

**Purpose**: Deep code critique, architectural review

**Capabilities**:
- Code critique
- Design review
- Quality assessment
- Improvement suggestions

---

#### omc:code-reviewer
| Model | CAW Fallback |
|-------|--------------|
| Opus | `cw:reviewer-opus --deep` |

**Purpose**: Comprehensive code review

**Capabilities**:
- Deep code review
- Logic analysis
- Pattern validation
- Best practice enforcement

---

#### omc:security-reviewer
| Model | CAW Fallback |
|-------|--------------|
| Opus | `cw:reviewer-opus --security` |

**Purpose**: Security-focused code analysis

**Capabilities**:
- Vulnerability scanning
- OWASP checks
- Security patterns
- Threat modeling

---

### Design & Architecture

#### omc:architect
| Model | CAW Fallback |
|-------|--------------|
| Opus | `cw:architect` |

**Purpose**: System architecture, design decisions

**Capabilities**:
- System design
- Component architecture
- Technical decisions
- Integration planning

---

#### omc:designer
| Model | CAW Fallback |
|-------|--------------|
| Sonnet | `cw:designer` |

**Purpose**: UI/UX design, visual specifications

**Capabilities**:
- Visual design
- UX patterns
- Interface specs
- Design systems

---

### Content & Documentation

#### omc:writer
| Model | CAW Fallback |
|-------|--------------|
| Sonnet | Direct LLM |

**Purpose**: Documentation, content writing

**Capabilities**:
- Documentation writing
- README creation
- API docs
- User guides

---

#### omc:vision
| Model | CAW Fallback |
|-------|--------------|
| Sonnet | Direct LLM |

**Purpose**: Image analysis, visual understanding

**Capabilities**:
- Image analysis
- Screenshot interpretation
- Visual debugging
- UI inspection

---

#### omc:tdd-guide
| Model | CAW Fallback |
|-------|--------------|
| Sonnet | `cw:Builder` |

**Purpose**: TDD methodology guidance

**Capabilities**:
- TDD workflow
- Test-first guidance
- Red-green-refactor
- Testing patterns

---

## Agent Selection Matrix

### By Task Type

| Task Type | Recommended Agent | Fallback |
|-----------|-------------------|----------|
| Planning | `cw:Planner` | - |
| Implementation | `cw:Builder` | - |
| Code Review | `cw:Reviewer` | - |
| Bug Fixing | `cw:Fixer` | - |
| Architecture | `omc:architect` | `cw:architect` |
| Research | `omc:researcher` | WebSearch |
| Testing | `omc:qa-tester` | `cw:Reviewer` + Bash |
| Security | `omc:security-reviewer` | `cw:reviewer-opus --security` |
| Data Analysis | `omc:scientist` | Bash + Python |

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

## Using OMC Agent (with fallback)
resolved_agent = resolve_agent("omc:architect")
Task tool:
  subagent_type: resolved_agent
  prompt: "Design the authentication system..."
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

### Conditional OMC Usage

```markdown
## Prefer OMC when available
IF omc_available():
  researcher = "omc:researcher"
ELSE:
  researcher = "cw:Planner"
  # Will need to manually use WebSearch/WebFetch
```

## Integration Points

### With Agent Resolver

All agent requests should go through the resolver:

```markdown
agent = resolve_agent(requested_agent)
Task(subagent_type=agent, prompt=...)
```

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
| `/cw:qaloop` | Multiple | Resolver |
| `/cw:ultraqa` | OMC preferred | Resolver |
| `/cw:research` | OMC preferred | Resolver |

## Schema Reference

See [agent-registry.schema.json](./schemas/agent-registry.schema.json) for the complete schema definition.

## Related Documentation

- [Agent Resolver](./agent-resolver.md) - Resolution and fallback logic
- [Model Routing](./model-routing.md) - Tier selection
- [Parallel Execution](./parallel-execution.md) - Concurrent agent execution
