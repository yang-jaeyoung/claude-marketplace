# Module Context

**Module:** AZ Skill Pack
**Version:** 1.0.0
**Role:** Collection of specialized skills for brainstorming, audits, and documentation.
**Tech Stack:** Markdown/YAML, JSON references.

## Core Capabilities

- Creative brainstorming with structured techniques
- Security audits (NIST/OWASP based)
- Reverse engineering documentation from codebases
- Project analysis (Vue.js, C#)
- Coding convention enforcement

---

# Operational Commands

```bash
# Brainstorming session
/az:brainstorm [topic]

# Security audit
/az:security-audit [scope] [--severity=level] [--format=type] [--fix]

# Documentation generation
/az:reverse-engineer-docs [type] [--output=format]

# Vue.js analysis
/az:analyze-vue
```

---

# Skill Inventory

## brainstorm
Creative ideation using structured techniques.
- **Techniques:** SCAMPER, Six Thinking Hats, Divergent Expansion
- **Language:** English
- **Reference:** `skills/brainstorm/references/techniques.md`

## csharp-convention
Microsoft C# coding conventions enforcement.
- **Language:** Korean
- **Scope:** Naming, formatting, code structure

## csharp-security
NIST/OWASP secure coding guidelines for C#.
- **Language:** Korean
- **Scope:** Authentication, encryption, input validation

## reverse-engineering-docs
Generates 7 types of project documentation from existing codebase.
- **Language:** Korean
- **Document Types:**
  - `requirements` — Requirements specification
  - `functional` — Functional specification
  - `usecase` — Use case documentation
  - `architecture` — Architecture design
  - `ui` — UI/UX design documentation
  - `database` — Database schema documentation
  - `operations` — Operations/deployment guide
- **Reference:** `skills/reverse-engineering-docs/references/`

## security-audit
Universal security audit framework for any technology stack.
- **Language:** Korean
- **Scopes:** `full`, `error`, `auth`, `data`, `api`, `deps`, `config`
- **Severities:** critical, high, medium, low
- **Reference:** `skills/security-audit/references/checklists.md`

## vue-project-analyzer
Vue.js project structure analysis and documentation generation.
- **Language:** Korean
- **Detects:** Vue 2/3, Vuex/Pinia, Vue Router, Composition API
- **Reference:** `skills/vue-project-analyzer/references/`

---

# Implementation Patterns

## Directory Structure

```
az-skill-pack/
  .claude-plugin/plugin.json
  README.md
  commands/
    brainstorm.md              # /az:brainstorm
    security-audit.md          # /az:security-audit
    reverse-engineer-docs.md   # /az:reverse-engineer-docs
    analyze-vue.md             # /az:analyze-vue
  skills/
    brainstorm/
      SKILL.md
      references/techniques.md
    csharp-convention/SKILL.md
    csharp-security/SKILL.md
    reverse-engineering-docs/
      SKILL.md
      references/              # Document templates
        REQUIREMENTS.md
        FUNCTIONAL.md
        USECASE.md
        ARCHITECTURE.md
        UI_DESIGN.md
        DATABASE.md
        OPERATIONS.md
    security-audit/
      SKILL.md
      references/checklists.md
    vue-project-analyzer/
      SKILL.md
      references/
        analysis-patterns.md
        phase-commands.md
        migration-checklist.md
    _shared/templates/         # Shared document templates
```

## Skill Definition Pattern

```yaml
---
name: skill-name
description: What the skill does
allowed-tools: Read, Glob, Grep, Write
---
# Instructions for skill execution
```

## Reference File Usage

Skills use `references/` directories for:
- Technique guides (brainstorm)
- Security checklists (security-audit)
- Document templates (reverse-engineering-docs)
- Analysis patterns (vue-project-analyzer)

---

# Local Golden Rules

## Do's

- **DO** use references for reusable content (checklists, templates).
- **DO** provide both Korean and English trigger support where applicable.
- **DO** structure audit output with severity levels and actionable items.
- **DO** generate all 7 document types for comprehensive reverse engineering.
- **DO** use `_shared/templates/` for cross-skill reusable formats.

## Don'ts

- **DON'T** hardcode severity mappings; use configurable checklists.
- **DON'T** skip checklist phases in security audits.
- **DON'T** generate documents without analyzing actual codebase first.
- **DON'T** mix brainstorming techniques inappropriately for the topic.
