---
description: Generate project documentation by analyzing the codebase (requirements, functional spec, use cases, architecture, UI, database, operations)
argument-hint: "[doc-type] [--output=format]"
allowed-tools: Read, Grep, Glob, Bash
---

# Reverse Engineer Docs Command

Analyze codebase and generate comprehensive project documentation.

## Arguments

| Argument | Values | Default | Description |
|----------|--------|---------|-------------|
| `doc-type` | `all`, `requirements`, `functional`, `usecase`, `architecture`, `ui`, `database`, `operations` | `all` | Document type to generate |
| `--output` | `markdown`, `docx` | `markdown` | Output format |

## Document Types

| Type | Description | Template |
|------|-------------|----------|
| `requirements` | Functional/non-functional requirements | [REQUIREMENTS.md](${CLAUDE_PLUGIN_ROOT}/skills/reverse-engineering-docs/references/REQUIREMENTS.md) |
| `functional` | Detailed function specifications | [FUNCTIONAL.md](${CLAUDE_PLUGIN_ROOT}/skills/reverse-engineering-docs/references/FUNCTIONAL.md) |
| `usecase` | User-system interaction scenarios | [USECASE.md](${CLAUDE_PLUGIN_ROOT}/skills/reverse-engineering-docs/references/USECASE.md) |
| `architecture` | System structure and component relationships | [ARCHITECTURE.md](${CLAUDE_PLUGIN_ROOT}/skills/reverse-engineering-docs/references/ARCHITECTURE.md) |
| `ui` | User interface design and flows | [UI_DESIGN.md](${CLAUDE_PLUGIN_ROOT}/skills/reverse-engineering-docs/references/UI_DESIGN.md) |
| `database` | Data model and schema definitions | [DATABASE.md](${CLAUDE_PLUGIN_ROOT}/skills/reverse-engineering-docs/references/DATABASE.md) |
| `operations` | Deployment, monitoring, troubleshooting | [OPERATIONS.md](${CLAUDE_PLUGIN_ROOT}/skills/reverse-engineering-docs/references/OPERATIONS.md) |

## Instructions

1. **Project Structure Analysis**
   ```bash
   tree -L 3 -I "node_modules|bin|obj|.git"
   ```
   - Identify directory structure
   - Find configuration files
   - Analyze dependencies

2. **Technology Stack Identification**
   - Detect language/framework from config files
   - Identify UI framework, database, CI/CD tools

3. **Architecture Pattern Analysis**
   - Layer structure (Controllers, Services, Repositories)
   - Module relationships
   - Communication patterns

4. **Domain Model Extraction**
   - Entities and value objects
   - Business rules
   - API endpoints

5. **Document Generation**
   - Load template from references/
   - Follow template structure
   - Include Mermaid diagrams
   - Reference code locations for traceability

## Quality Criteria

| Criterion | Description |
|-----------|-------------|
| Completeness | Include all identified features/components |
| Accuracy | Match actual implementation |
| Consistency | Unified terminology across documents |
| Traceability | Include code location references |
| Readability | Use diagrams, tables, examples |

## Usage Examples

```
/az:reverse-engineer-docs
/az:reverse-engineer-docs architecture
/az:reverse-engineer-docs database --output=docx
/az:reverse-engineer-docs all
```

## Important Notes

- **Code-first**: Base analysis on actual code, not assumptions
- **Version**: Record analysis timestamp and code state
- **Exclude sensitive data**: No passwords, API keys in output
