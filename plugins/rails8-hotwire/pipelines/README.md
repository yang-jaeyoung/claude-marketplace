# Rails 8 + Hotwire Pipelines

Pre-built multi-agent workflows for common Rails development tasks. Pipelines chain specialized agents together to complete complex tasks autonomously.

## What are Pipelines?

Pipelines are sequential agent workflows where each stage's output feeds into the next. They orchestrate multiple specialized agents to complete complex tasks that would otherwise require manual coordination.

```
[Stage 1: Analyze] --> [Stage 2: Generate] --> [Stage 3: Test] --> [Stage 4: Review]
     Architect           Executor              RSpec Tester        Reviewer
```

## How to Invoke

### Via Slash Command
```
/rails8:pipeline <pipeline-name> [context]
```

### Via Natural Language
```
"Run the auth pipeline"
"Use feature pipeline to implement user notifications"
```

## Available Pipelines

### 1. auth-pipeline

**Purpose:** Complete authentication setup from scratch

**Invocation:** `/rails8:pipeline auth`

**Triggers:** `auth`, `authentication`

**Stages:**
| Stage | Agent | Model | Description |
|-------|-------|-------|-------------|
| devise-setup | devise-specialist | sonnet | Configure Devise or Rails 8 built-in auth |
| views | rails-executor | sonnet | Generate authentication views |
| policies | devise-specialist | sonnet | Set up Pundit authorization policies |
| specs | rspec-tester | sonnet | Write authentication tests |

**Example:**
```
/rails8:pipeline auth
"Set up authentication with email/password and Google OAuth"
```

---

### 2. crud-pipeline

**Purpose:** Generate complete CRUD resource with Turbo integration

**Invocation:** `/rails8:pipeline crud`

**Triggers:** `crud`, `resource`

**Stages:**
| Stage | Agent | Model | Description |
|-------|-------|-------|-------------|
| model-gen | rails-executor | sonnet | Create model and migrations |
| scaffold | rails-executor | sonnet | Generate controller and views |
| turbo | hotwire-specialist | sonnet | Add Turbo Frame/Stream integration |
| specs | rspec-tester | sonnet | Write request and system specs |

**Example:**
```
/rails8:pipeline crud
"Create a Post resource with title, body, and published status"
```

---

### 3. deploy-pipeline

**Purpose:** Set up production deployment infrastructure

**Invocation:** `/rails8:pipeline deploy`

**Triggers:** `deploy`, `deployment`

**Stages:**
| Stage | Agent | Model | Description |
|-------|-------|-------|-------------|
| docker-setup | kamal-deployer | sonnet | Optimize Dockerfile |
| kamal-config | kamal-deployer | sonnet | Generate Kamal configuration |
| ci-setup | kamal-deployer | sonnet | Create GitHub Actions workflow |
| deploy | kamal-deployer | sonnet | Execute deployment |

**Example:**
```
/rails8:pipeline deploy
"Deploy to a Hetzner VPS with SSL"
```

---

### 4. feature-pipeline

**Purpose:** TDD-driven feature implementation

**Invocation:** `/rails8:pipeline feature`

**Triggers:** `feature`, `implement`

**Stages:**
| Stage | Agent | Model | Description |
|-------|-------|-------|-------------|
| analyze | rails-architect | opus | Analyze requirements, create implementation plan |
| test-first | rspec-tester | sonnet | Write tests before implementation |
| implement | rails-executor | sonnet | Implement to pass tests |
| hotwire | hotwire-specialist | sonnet | Add Turbo/Stimulus integration |
| review | rails-reviewer | opus | Review code quality, security, performance |

**Example:**
```
/rails8:pipeline feature
"Implement a notification system with real-time updates"
```

---

### 5. refactor-pipeline

**Purpose:** Safe refactoring with test protection

**Invocation:** `/rails8:pipeline refactor`

**Triggers:** `refactor`, `refactoring`

**Stages:**
| Stage | Agent | Model | Description |
|-------|-------|-------|-------------|
| analyze | rails-architect | opus | Analyze refactoring targets, create plan |
| specs-first | rspec-tester | sonnet | Ensure baseline test coverage |
| refactor | rails-executor-high | opus | Execute refactoring |
| verify | rspec-tester | sonnet | Confirm all tests pass |

**Example:**
```
/rails8:pipeline refactor
"Extract service objects from PostsController"
```

---

### 6. test-pipeline

**Purpose:** TDD workflow for existing code

**Invocation:** `/rails8:pipeline test`

**Triggers:** `test`, `tdd`

**Stages:**
| Stage | Agent | Model | Description |
|-------|-------|-------|-------------|
| analyze | rails-architect-low | haiku | Quick analysis of test targets |
| specs | rspec-tester | sonnet | Write RSpec tests |
| fix | rails-executor | sonnet | Fix failing tests (conditional) |
| verify | rspec-tester-low | haiku | Final verification |

**Conditional Logic:** The `fix` stage only runs if `specs.failures > 0`

**Example:**
```
/rails8:pipeline test
"Add tests for the User model"
```

---

## Pipeline JSON Schema

Each pipeline is defined as a JSON file with this structure:

```json
{
  "name": "pipeline-name",
  "description": "What the pipeline does",
  "stages": [
    {
      "name": "stage-name",
      "agent": "agent-identifier",
      "model": "haiku|sonnet|opus",
      "prompt": "Instructions for the agent",
      "inputs": ["previous_output_names"],
      "outputs": ["output_names_for_next_stages"],
      "condition": "optional_condition"
    }
  ],
  "triggers": ["keyword1", "keyword2"],
  "invocation": "/rails8:pipeline name"
}
```

### Field Descriptions

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Pipeline identifier |
| `description` | Yes | Human-readable description |
| `stages` | Yes | Array of stage definitions |
| `stages[].name` | Yes | Stage identifier |
| `stages[].agent` | Yes | Agent to execute this stage |
| `stages[].model` | Yes | Model tier (haiku/sonnet/opus) |
| `stages[].prompt` | Yes | Instructions for the agent |
| `stages[].inputs` | No | Output names from previous stages |
| `stages[].outputs` | No | Named outputs for subsequent stages |
| `stages[].condition` | No | Condition for stage execution |
| `triggers` | Yes | Keywords that activate this pipeline |
| `invocation` | Yes | Explicit command syntax |

## Creating Custom Pipelines

1. Create a new JSON file in `/pipelines/`:

```json
{
  "name": "my-custom-pipeline",
  "description": "My custom workflow",
  "stages": [
    {
      "name": "plan",
      "agent": "rails-architect",
      "model": "opus",
      "prompt": "Create a detailed implementation plan",
      "outputs": ["plan"]
    },
    {
      "name": "execute",
      "agent": "rails-executor",
      "model": "sonnet",
      "prompt": "Implement according to the plan",
      "inputs": ["plan"],
      "outputs": ["implementation"]
    }
  ],
  "triggers": ["my-workflow"],
  "invocation": "/rails8:pipeline my-custom"
}
```

2. Invoke with `/rails8:pipeline my-custom`

## Agent Reference

| Agent | Specialty | Model Tiers |
|-------|-----------|-------------|
| rails-architect | Architecture, planning, analysis | opus, low (haiku) |
| rails-executor | Code implementation | sonnet, high (opus) |
| hotwire-specialist | Turbo/Stimulus patterns | sonnet, high (opus) |
| devise-specialist | Authentication/authorization | sonnet |
| rspec-tester | Test writing | sonnet, low (haiku) |
| kamal-deployer | Deployment, Docker, CI/CD | sonnet |
| rails-reviewer | Code review, security, performance | opus, low (haiku) |
| rails-migrator | Database migrations | sonnet |

## Best Practices

1. **Choose the right pipeline:** Use `feature-pipeline` for new features, `refactor-pipeline` for restructuring
2. **Provide context:** Give detailed requirements when invoking
3. **Let it complete:** Pipelines are designed to run end-to-end
4. **Review outputs:** Always review generated code before committing

## Troubleshooting

### Pipeline stops mid-execution
- Check agent outputs for errors
- Ensure required dependencies are installed
- Verify database is running for migration stages

### Tests fail in verify stage
- This is expected behavior - the pipeline will attempt fixes
- If persistent, review generated code manually

### Wrong pipeline activated
- Use explicit invocation: `/rails8:pipeline <name>`
- Check trigger keywords don't overlap
