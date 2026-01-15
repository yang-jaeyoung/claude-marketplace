# Project Onboarding Template

Template for `project_onboarding` Serena memory.

## Structure

```markdown
# Project Onboarding

## Metadata
- **Last Updated**: YYYY-MM-DDTHH:MM:SSZ
- **Source**: Bootstrapper Agent
- **Version**: 1.0

## Project Info
- **Name**: [project name from package.json/pyproject.toml]
- **Type**: [nodejs | python | rust | go | java | unknown]
- **Root**: [relative path, usually "."]

## Detected Frameworks

| Name | Version | Category |
|------|---------|----------|
| [framework] | [version] | [frontend|backend|testing|language|linting|build] |

## Conventions
- **Code Style**: [ESLint + Prettier | Black + isort | rustfmt | ...]
- **Git**: [Conventional Commits | Feature branches | ...]
- **Testing**: [Jest | pytest | cargo test | ...]

## Key Files

### Configuration
| File | Purpose |
|------|---------|
| package.json | Dependencies and scripts |
| tsconfig.json | TypeScript configuration |

### Documentation
| File | Purpose |
|------|---------|
| GUIDELINES.md | Project conventions |
| README.md | Project overview |

### Entry Points
| File | Purpose |
|------|---------|
| src/index.ts | Main entry |
| src/app.ts | Application setup |

## Project Structure Summary

```
[Brief directory tree of important folders]
```

## Notes
- [Any special considerations]
- [Known quirks or gotchas]
```

## Usage

**Save (Bootstrapper)**:
```
write_memory("project_onboarding", content)
```

**Load (Any Agent)**:
```
read_memory("project_onboarding")
```

## When to Update

- Project type changes (new framework added)
- Major restructuring
- New conventions established
- Key files added/removed
