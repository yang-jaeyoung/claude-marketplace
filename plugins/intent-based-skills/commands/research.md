---
description: "Run multi-agent research orchestrator for comprehensive research on any topic"
argument-hint: "--goal <goal> [--depth quick|standard|deep] [--auto]"
allowed-tools: ["Bash", "Read", "Write", "Glob", "Grep", "Task", "WebSearch", "WebFetch", "mcp__tavily__tavily_search", "mcp__exa__web_search_exa", "mcp__grep__searchGitHub"]
---

# Research Orchestrator CLI

## Overview

Research Orchestrator는 멀티 에이전트 기반 자동화된 연구 시스템입니다.
4단계 워크플로우(분해 -> 실행 -> 검증 -> 통합)를 통해 복잡한 연구 주제를 체계적으로 분석합니다.

## Usage

```bash
# Basic usage
/research --goal "연구 주제"

# With depth option
/research --goal "연구 주제" --depth standard

# Auto mode (non-interactive)
/research --goal "연구 주제" --auto
```

## Arguments

| Argument | Required | Default | Description |
|----------|----------|---------|-------------|
| `--goal` | Yes | - | 연구 목표/주제 |
| `--depth` | No | standard | 연구 깊이 (quick: 2-3 stages, standard: 4-6 stages, deep: 7-10 stages) |
| `--type` | No | technical | 연구 유형 (technical, academic, market, comparative) |
| `--output` | No | ./research-output | 출력 디렉토리 |
| `--auto` | No | false | 자동 실행 모드 (사용자 확인 없이 진행) |
| `--resume` | No | false | 이전 실행 재개 |

## Workflow Phases

### Phase 1: Decomposition
연구 목표를 독립적인 Stage로 분해합니다.
- 출력: `stages/decomposition.json`, `diagrams/research-decomposition.mmd`

### Phase 2: Execution
각 Stage를 병렬로 실행하여 Findings를 수집합니다.
- 출력: `stages/stage-{n}-data.json`, `stages/stage-{n}-{name}.md`

### Phase 3: Verification
모든 결과를 교차 검증하여 일관성을 평가합니다.
- 출력: `validation/validation-result.json`, `validation/validation-report.md`

### Phase 4: Synthesis
최종 연구 리포트를 생성합니다.
- 출력: `RESEARCH-REPORT.md`, `research-data.json`

## Output Structure

```
research-output/
├── RESEARCH-REPORT.md       # 최종 연구 리포트
├── research-data.json       # 구조화된 연구 데이터
├── stages/
│   ├── decomposition.json   # Stage 분해 결과
│   ├── stage-1-data.json    # Stage 1 결과
│   ├── stage-1-xxx.md       # Stage 1 상세
│   └── ...
├── validation/
│   ├── validation-result.json
│   └── validation-report.md
└── diagrams/
    ├── research-decomposition.mmd
    └── validation-matrix.mmd
```

## Examples

### Technical Research
```bash
/research --goal "React Server Components vs Next.js App Router 비교 분석" --type comparative --depth standard
```

### Market Research
```bash
/research --goal "2024 AI 코딩 어시스턴트 시장 분석" --type market --depth deep
```

### Academic Research
```bash
/research --goal "Large Language Model의 Reasoning 능력 평가 방법론" --type academic --depth standard
```

## Execution

Research Orchestrator를 시작하려면 아래 단계를 따르세요:

1. **연구 목표 확인**: 사용자가 제공한 연구 목표를 분석합니다.

2. **Phase 1 실행**: Decomposer 에이전트를 사용하여 연구를 Stage로 분해합니다.
   - `lib/research_orchestrator/prompts/decomposer.prompt.md` 템플릿 사용

3. **Phase 2 실행**: 각 Stage에 대해 Scientist 에이전트 실행
   - `lib/research_orchestrator/prompts/scientist.prompt.md` 템플릿 사용
   - 가능한 경우 병렬 실행

4. **Phase 3 실행**: Validator 에이전트로 결과 검증
   - `lib/research_orchestrator/prompts/validator.prompt.md` 템플릿 사용

5. **Phase 4 실행**: Synthesizer 에이전트로 최종 리포트 생성
   - `lib/research_orchestrator/prompts/synthesizer.prompt.md` 템플릿 사용

6. **검증**: 체크리스트로 결과 검증
   - `checklists/research-orchestrator.yaml` 참조

## Notes

- AUTO 모드에서는 Guardrails가 적용됩니다 (max_stages, timeout 등)
- 각 Phase 완료 후 체크포인트가 저장되어 재개 가능
- 일관성 점수가 0.7 미만이면 경고 표시
