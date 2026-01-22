# Module Context

**Module:** Intent-Based Skills
**Version:** 1.0.0
**Role:** Intent-driven skill framework for consistent and verifiable complex task execution.
**Tech Stack:** Python 3.8+, JSON Schema, Markdown/YAML.

## Core Capabilities

- Structured skill scaffolding with validation schemas
- Feedback loop system for continuous improvement
- Multi-agent research orchestrator (4-stage workflow)
- Project analyzers (React, Vue, .NET)
- OMC integration for enhanced capabilities

---

# Operational Commands

```bash
# Skill commands (in Claude Code)
/research --goal "..." --depth standard  # Research orchestrator
/feedback-start <skill>                  # Start feedback collection
/feedback-analyze <skill>                # Analyze patterns
/feedback-report <skill>                 # Generate improvement report
/verify-skill <skill>                    # Validate skill output

# Python dependencies (if using lib/)
pip install pyyaml
```

---

# Skill Inventory

## intent-skill-creator
Scaffolds new intent-based skill structure.
- **Trigger:** "새 스킬 만들어줘", "create new skill", "scaffold skill"
- **Output:** intent.yaml, SKILL.md, schema/output.schema.json, verification/

## feedback-loop
Collects and analyzes skill execution feedback for improvement suggestions.
- **Trigger:** "feedback start", "feedback analyze", "스킬 피드백 분석"
- **Events:** start, complete, failure, correction

## research-orchestrator
Multi-agent automated research system with 4-stage workflow.
- **Trigger:** `/research`, "연구 수행", "research on"
- **Stages:** Decomposition -> Execution -> Verification -> Synthesis
- **Depth:** quick (2-3), standard (4-6), deep (7-10)
- **Types:** technical, academic, market, comparative

## react-project-analyzer
Analyzes React project structure, components, state management, routing.
- **Trigger:** "React 프로젝트 분석", "React 아키텍처 분석"
- **Detects:** React 17/18/19, Vite/CRA/Next.js, Redux/Zustand/Context

## vue-project-analyzer
Analyzes Vue project structure and generates documentation.
- **Trigger:** "Vue 프로젝트 분석", "Vue 아키텍처 분석"

## dotnet-project-analyzer
Analyzes .NET project structure and generates documentation.
- **Trigger:** ".NET 프로젝트 분석", "C# 아키텍처 분석"

---

# Implementation Patterns

## Directory Structure

```
intent-based-skills/
  .claude-plugin/plugin.json
  README.md
  skills/
    <skill-name>/SKILL.md         # Skill definition
  commands/
    feedback-*.md                 # Feedback loop commands
    research.md                   # Research orchestrator CLI
    verify-skill.md               # Verification command
  schemas/
    <skill>.schema.json           # Output validation schemas
  hooks/hooks.json                # Stop event hooks
  lib/
    feedback_collector.py         # Event collection CLI
    feedback_analyzer.py          # Pattern analysis
    research_orchestrator/        # Research system library
      orchestrator.py             # Main orchestrator
      models.py                   # Data models
      agents/                     # Agent implementations
      prompts/                    # Prompt templates
```

## Skill Definition (skills/*/SKILL.md)

```yaml
---
name: skill-name
description: What the skill does
allowed-tools: Read, Glob, Grep, Write
---
# Skill execution instructions
## Triggers
## Workflow
## Output
```

## Schema Validation Pattern

JSON Schemas in `schemas/` directory validate skill outputs:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "properties": { ... },
  "required": [ ... ]
}
```

---

# Research Orchestrator Details

## Workflow Stages

1. **Decomposition:** Break research goal into independent stages
2. **Execution:** Run stages in parallel, collect findings
3. **Verification:** Cross-validate all results for consistency
4. **Synthesis:** Generate final research report

## Output Files

- `RESEARCH-REPORT.md` — Final research report
- `research-data.json` — Structured research data
- `stages/` — Per-stage results
- `validation/` — Cross-verification results
- `diagrams/` — Mermaid diagrams

## OMC Integration

When OMC is available:
- Stage execution uses `omc:scientist` for deep analysis
- Cross-verification uses `omc:critic` for critical review
- Falls back to default agents when OMC unavailable

---

# Local Golden Rules

## Do's

- **DO** define JSON schemas for all skill outputs in `schemas/`.
- **DO** use feedback-loop to track and improve skill quality.
- **DO** provide clear trigger phrases in Korean and English.
- **DO** implement graceful degradation when OMC unavailable.
- **DO** structure research reports with executive summary first.

## Don'ts

- **DON'T** skip schema validation for skill outputs.
- **DON'T** run research without specifying depth and type.
- **DON'T** ignore feedback patterns; they indicate improvement areas.
- **DON'T** hardcode agent selection; use the resolver pattern.
