# Expert Specification Panel: Magic-Note Workflow Evolution

> **Panel Date**: 2026-01-03
> **Mode**: Discussion | Focus: Requirements & Architecture
> **Status**: Initial Analysis Complete

---

## Executive Summary

Magic-Note는 초기에 프로젝트에서 생성되는 계획, 프롬프트, 아이디어 등을 저장하는 노트 관리 도구로 시작했으나, 현재는 AI 코딩 워크플로우 관리 수준까지 발전했습니다. 이 문서는 전문가 패널 토론을 통해 Magic-Note를 완전한 워크플로우 관리 도구로 전환하기 위한 전략을 수립합니다.

---

## Current State Analysis

| 영역 | 현재 상태 | 워크플로우 관점 |
|------|----------|----------------|
| **Note Types** | prompt, plan, choice, insight | 워크플로우 아티팩트의 일부만 커버 |
| **Agents** | 3개 (organizer, curator, reviewer) | 작업 자동화 초기 단계 |
| **Skills** | 4개 (auto-save, prompt-lib, decision-log, insight) | 이벤트 기반 자동화 시작 |
| **Hooks** | 4개 (session start/end, post-tool, subagent) | 세션 라이프사이클 통합 |

---

## Expert Panel

**Selected Experts** (워크플로우 관리 전환에 적합):
- **Karl Wiegers** - 요구사항 정의, 사용자 니즈 분석
- **Alistair Cockburn** - 유스케이스, 목표 지향 분석
- **Martin Fowler** - 아키텍처 진화, 도메인 설계
- **Gregor Hohpe** - 통합 패턴, 메시지 기반 워크플로우
- **Michael Nygard** - 운영 우수성, 실패 복구 패턴

---

## Expert Discussion

### KARL WIEGERS (Requirements Engineering)

> "Magic-note의 현재 가치 제안을 분석해보면, **'노트 저장'**에서 시작했지만 이미 **'맥락 보존'**과 **'작업 연속성'** 문제를 해결하고 있습니다. 이것이 워크플로우 관리의 핵심입니다.
>
> 하지만 중요한 질문이 있습니다: **워크플로우 관리**라고 할 때 정확히 무엇을 의미하나요?
>
> 제가 보기에 세 가지 다른 방향이 있습니다:
>
> 1. **Task Orchestration** - 작업 의존성, 순서, 병렬 실행 관리
> 2. **Context Continuity** - 세션 간 맥락 보존, 중단/재개 지원
> 3. **Knowledge Workflow** - 아이디어 → 계획 → 구현 → 학습의 지식 흐름
>
> 현재 magic-note는 **세 번째(Knowledge Workflow)**에 가장 가깝습니다. 이것을 명확히 정의해야 합니다."

### ALISTAIR COCKBURN (Use Case Methodology)

> "Karl의 분석에 동의합니다. 핵심 질문은: **Primary Actor가 누구이고, 그들의 Goal은 무엇인가?**
>
> 현재 magic-note의 암묵적 사용자 목표를 추출해보면:
>
> ```
> 🎯 Primary Goals (현재)
> ├── G1: "내가 왜 이렇게 했는지 나중에 알고 싶다" → choice 노트
> ├── G2: "좋은 프롬프트를 재사용하고 싶다" → prompt 노트
> ├── G3: "계획을 세우고 진행 상황을 추적하고 싶다" → plan 노트 + reviewer
> └── G4: "배운 것을 잊지 않고 싶다" → insight 노트
> ```
>
> **워크플로우 관리자**로 전환하려면 새로운 목표가 추가되어야 합니다:
>
> ```
> 🎯 New Goals (워크플로우)
> ├── G5: "복잡한 작업을 분해하고 위임하고 싶다"
> ├── G6: "작업 간 의존성을 관리하고 싶다"
> ├── G7: "여러 세션에 걸친 장기 프로젝트를 관리하고 싶다"
> └── G8: "팀/AI 에이전트 간 협업을 조율하고 싶다"
> ```
>
> 이 중 어느 것을 우선시할지가 전략적 결정입니다."

### MARTIN FOWLER (Software Architecture)

> "Alistair의 목표 분석을 바탕으로 아키텍처 관점에서 보면, magic-note는 현재 **Document-Centric** 모델입니다. Note가 핵심 엔티티이고 모든 것이 Note를 중심으로 돌아갑니다.
>
> 워크플로우 관리로 전환하려면 **Domain Model Evolution**이 필요합니다:
>
> ```
> 현재 (Document-Centric):
> ┌─────────────────────────────────────────┐
> │                Note                      │
> │  - id, type, title, content             │
> │  - tags, project, created               │
> └─────────────────────────────────────────┘
>
> 진화 방향 (Workflow-Centric):
> ┌─────────────────────────────────────────┐
> │             Workflow                     │
> │  - id, name, status, context            │
> ├─────────────────────────────────────────┤
> │  ├── Task[] (분해된 작업)               │
> │  │   ├── dependencies                   │
> │  │   ├── status, assignee               │
> │  │   └── artifacts[]                    │
> │  ├── Note[] (기존 노트 - artifact로)    │
> │  ├── Decision[] (의사결정 기록)         │
> │  └── Checkpoint[] (상태 스냅샷)         │
> └─────────────────────────────────────────┘
> ```
>
> **중요한 설계 결정**: Note를 Workflow의 **artifact**로 포함시킬 것인가, 아니면 별개의 **first-class citizen**으로 유지할 것인가?"

### GREGOR HOHPE (Integration Patterns)

> "Martin의 도메인 모델 제안에 이어서, 워크플로우 관리의 핵심은 **State Management**와 **Event Coordination**입니다.
>
> Magic-note가 이미 가지고 있는 것들을 워크플로우 패턴으로 재해석하면:
>
> ```yaml
> Current Integration Points:
>   hooks:
>     SessionStart: → "Workflow Resume" 이벤트
>     SessionEnd: → "Workflow Checkpoint" 이벤트
>     PostToolUse: → "Task Progress" 이벤트
>     SubagentStop: → "Delegated Task Complete" 이벤트
>
>   skills:
>     auto-save-plan: → "Workflow Definition" 생성
>     decision-logger: → "Decision Point" 기록
>     auto-capture-insight: → "Learning Event" 수집
> ```
>
> 이것들을 **Workflow State Machine**으로 통합할 수 있습니다:
>
> ```
> Workflow States:
> [Draft] → [Active] → [In Progress] → [Blocked] → [Completed]
>                 ↓           ↓              ↓
>            [Paused]    [Waiting]    [Escalated]
>                 ↓           ↓              ↓
>            [Resumed] → [Continued] → [Unblocked]
> ```
>
> 핵심 제안: **Event Sourcing** 패턴을 도입하여 모든 워크플로우 변경을 이벤트로 기록하세요. 이것이 '어디까지 했지?' 문제를 완벽하게 해결합니다."

### MICHAEL NYGARD (Operational Excellence)

> "Gregor의 Event Sourcing 제안에 전적으로 동의하며, 운영 관점에서 추가하겠습니다.
>
> 워크플로우 관리 도구의 **핵심 실패 모드**를 고려해야 합니다:
>
> ```
> ⚠️ Failure Modes to Handle:
>
> 1. Session Crash → 작업 상태 손실
>    해결: Auto-checkpoint (현재 SessionEnd만 있음)
>
> 2. Context Overflow → 긴 세션에서 맥락 상실
>    해결: Progressive Summarization + State Snapshots
>
> 3. Multi-Session Drift → 세션 간 일관성 손실
>    해결: Workflow State + Conflict Resolution
>
> 4. Agent Coordination Failure → 위임 작업 실패
>    해결: Task Ownership + Timeout + Retry
> ```
>
> **Circuit Breaker 패턴** 적용을 제안합니다:
>
> ```
> Workflow Resilience:
> ├── Auto-save: Every significant action
> ├── Checkpoint: Every 15 minutes or major milestone
> ├── Recovery: Session start loads last checkpoint
> └── Conflict: Merge strategy for concurrent edits
> ```
>
> 현재 magic-note의 `plan-reviewer` 에이전트가 이미 '어디까지 했지?' 기능을 가지고 있는데, 이것을 **자동 복구 메커니즘**으로 승격시키세요."

---

## Cross-Framework Synthesis

### Convergent Insights (전문가 합의 영역)

| 영역 | 합의 내용 |
|------|----------|
| **정체성** | Note 도구가 아닌 **Knowledge Workflow** 도구로 포지셔닝 |
| **진화 방향** | Document-Centric → **Workflow-Centric** 도메인 모델 |
| **핵심 패턴** | **Event Sourcing**으로 모든 변경 추적 |
| **복원력** | **자동 체크포인트**와 복구 메커니즘 필수 |
| **기존 자산** | 현재 hooks, skills, agents를 워크플로우 이벤트로 재해석 |

### Productive Tensions (전략적 선택 필요)

| Trade-off | Option A | Option B |
|-----------|----------|----------|
| **범위** | Knowledge Workflow에 집중 | Full Task Orchestration으로 확장 |
| **복잡도** | Note를 artifact로 (하위 개념) | Note를 first-class로 유지 (병렬 개념) |
| **Target** | 개인 개발자 워크플로우 | 팀/에이전트 협업 워크플로우 |
| **통합** | 독립 도구 | Claude Code 네이티브 통합 |

### Strategic Questions (다음 탐구 우선순위)

1. **"Knowledge Workflow"가 충분히 차별화된 가치 제안인가?** (vs. 기존 프로젝트 관리 도구)

2. **Note Type 확장 vs. 새로운 Workflow 엔티티 도입** - 어느 것이 사용자 멘탈 모델에 더 자연스러운가?

3. **Event Sourcing 도입 시 storage 구조 변경** - 마이그레이션 전략은?

4. **Claude Code 외부 사용 가능성** - 다른 AI 코딩 도구와의 호환성 고려?

---

## Proposed Evolution Roadmap

```
Phase 1: Foundation (현재 → 강화)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
├── Event Log 도입 (모든 변경 기록)
├── Auto-checkpoint 강화 (15분 / 마일스톤)
├── Session Recovery 자동화
└── plan-reviewer를 "Workflow Status" 에이전트로 승격

Phase 2: Workflow Model (새로운 개념)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
├── Workflow 엔티티 도입
├── Task 분해 및 의존성 관리
├── Workflow State Machine 구현
└── Note → Artifact 관계 정립

Phase 3: Intelligence (AI 네이티브)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
├── 자동 작업 분해 제안
├── 블로커 예측 및 경고
├── 크로스 세션 학습 (무엇이 효과적이었는지)
└── 컨텍스트 지능형 압축
```

---

## Key Insights

- 현재 magic-note는 이미 **암묵적 워크플로우 관리**를 하고 있음 (plan-reviewer, hooks)
- 진정한 전환은 **새로운 기능 추가**가 아니라 **기존 기능의 재해석과 통합**
- **Event Sourcing**이 "어디까지 했지?" 문제의 근본적 해결책

---

## Related Documents

- [02-domain-model-design.md](./02-domain-model-design.md) - 도메인 모델 상세 설계
- [03-mcp-tool-api-design.md](./03-mcp-tool-api-design.md) - MCP Tool API 설계
