---
name: decision-logger
description: Captures architectural and technical decisions in ADR format. Invoked when AskUserQuestion responses contain decisions or architecture choices are made. Use to document technology selections, design patterns, or trade-off decisions.
allowed-tools: Read, Write, Glob
---

# Decision Logger

Captures and documents architectural and technical decisions in Architecture Decision Record (ADR) format.

## Core Principle

**결정 = 즉시 기록**

기술적 결정이 내려지면 ADR 형식으로 즉시 기록합니다. 나중에 "왜 이렇게 했지?"라는 질문에 답할 수 있습니다.

## Triggers

이 Skill은 다음 상황에서 활성화됩니다:

1. **AskUserQuestion 응답에 결정 포함**
   - "X를 선택합니다", "Y로 하겠습니다"
   - "A 대신 B를 사용"

2. **아키텍처 선택 논의**
   - 기술 스택 선택
   - 디자인 패턴 결정
   - 라이브러리/프레임워크 선택

3. **Trade-off 논의 완료**
   - 장단점 비교 후 결론
   - 대안 검토 후 최종 선택

4. **명시적 요청**
   - "이 결정을 기록해줘"
   - "ADR로 남겨줘"

## Decision Detection Patterns

| Pattern | Example |
|---------|---------|
| 선택 표현 | "chose X over Y", "decided to use X", "X를 선택" |
| 비교 결론 | "X instead of Y because...", "X 대신 Y" |
| 근거 제시 | "because", "due to", "the reason is", "왜냐하면" |
| Trade-off | "trade-off", "pros/cons", "장단점" |
| 최종 결정 | "concluded", "final choice", "결론적으로" |

## Behavior

### Step 1: Detect Decision

대화에서 결정 패턴 감지:

```yaml
detection:
  keywords:
    - "decided", "chose", "selected", "will use"
    - "결정", "선택", "채택", "사용하기로"
  context:
    - Technology comparison
    - Architecture discussion
    - Library selection
    - Pattern choice
```

### Step 2: Generate ADR ID

순차적 ID 생성:

```yaml
id_format: ADR-{NNN}
examples:
  - ADR-001
  - ADR-002
  - ADR-015

process:
  1. Read .caw/decisions/ directory
  2. Find highest existing ADR number
  3. Increment by 1
  4. If no existing ADRs, start with 001
```

### Step 3: Extract Components

결정에서 핵심 요소 추출:

```yaml
components:
  title: Short description of the decision
  context: What prompted this decision
  options: Alternatives that were considered
  decision: The chosen option
  rationale: Why this was chosen
  consequences: Expected impacts (positive/negative)
```

### Step 4: Write ADR File

`.caw/decisions/` 에 저장:

```yaml
action: Write tool
path: .caw/decisions/ADR-{NNN}-{slug}.md
content: See ADR Template below
```

### Step 5: Update Index

인덱스 파일 업데이트 (있는 경우):

```yaml
action: Append to .caw/decisions/index.md
content: |
  | ADR-{NNN} | [Title] | [Status] | [Date] |
```

### Step 6: Confirm

저장 완료 확인:

```
📋 ADR saved: ADR-{NNN} - {Title}
```

## ADR Template

See [templates/adr-template.md](templates/adr-template.md) for the full template.

```markdown
# ADR-{NNN}: {Title}

## Metadata
| Field | Value |
|-------|-------|
| **ID** | ADR-{NNN} |
| **Date** | YYYY-MM-DD |
| **Status** | Proposed / Accepted / Deprecated / Superseded |
| **Context** | [Related workflow phase/step if applicable] |

## Context
[What is the issue that we're seeing that is motivating this decision?]

## Options Considered
### Option A: [Name]
- **Pros**: ...
- **Cons**: ...

### Option B: [Name]
- **Pros**: ...
- **Cons**: ...

## Decision
[What is the change that we're proposing and/or doing?]

## Rationale
[Why was this option chosen over others?]

## Consequences

### Positive
- [Benefit 1]
- [Benefit 2]

### Negative
- [Trade-off 1]
- [Trade-off 2]

## Related
- [Links to related ADRs, insights, or documentation]
```

## File Naming Convention

**Pattern**: `ADR-{NNN}-{slug}.md`

- NNN: 3자리 순차 번호 (001, 002, ...)
- slug: 제목에서 3-5단어, kebab-case

**Examples**:
- `ADR-001-jwt-over-session-auth.md`
- `ADR-002-postgres-database-selection.md`
- `ADR-003-rest-api-design.md`

## Directory Structure

```
.caw/
└── decisions/
    ├── index.md                        # Master ADR index
    ├── ADR-001-jwt-over-session.md
    ├── ADR-002-postgres-database.md
    └── ADR-003-rest-api-design.md
```

## ADR Status Values

| Status | Meaning |
|--------|---------|
| **Proposed** | Under discussion, not yet accepted |
| **Accepted** | Approved and in effect |
| **Deprecated** | No longer recommended, but not replaced |
| **Superseded** | Replaced by another ADR (link to new one) |

## Index File Format

```markdown
# Architecture Decision Records

| ID | Title | Status | Date |
|----|-------|--------|------|
| [ADR-001](ADR-001-jwt-over-session.md) | JWT over Session Auth | Accepted | 2026-01-04 |
| [ADR-002](ADR-002-postgres-database.md) | PostgreSQL Selection | Accepted | 2026-01-04 |
```

## Example Flow

```
1. 사용자: "인증 방식으로 JWT와 Session 중 어떤 걸 사용할까요?"

2. 모델: 장단점 비교 제시
   - JWT: Stateless, 확장성 좋음, 토큰 크기 큼
   - Session: 서버 관리 필요, 즉시 무효화 가능

3. 사용자: "JWT를 사용하겠습니다. 확장성이 중요해서요."

4. 모델: 결정 감지 → ADR 생성
   → .caw/decisions/ADR-001-jwt-authentication.md 저장

5. 모델: 확인 메시지
   📋 ADR saved: ADR-001 - JWT Authentication Selection
```

## Integration with Workflow

### CAW Workflow Active

워크플로우가 활성화된 경우, 메타데이터에 Phase/Step 정보 포함:

```markdown
## Metadata
| Field | Value |
|-------|-------|
| **ID** | ADR-001 |
| **Date** | 2026-01-04 |
| **Status** | Accepted |
| **Context** | Phase 1: Architecture Design, Step 1.2 |
```

### Without Workflow

일반 대화에서도 ADR 저장 가능:

```markdown
## Metadata
| Field | Value |
|-------|-------|
| **ID** | ADR-001 |
| **Date** | 2026-01-04 |
| **Status** | Accepted |
| **Context** | General Discussion - Tech Stack Selection |
```

## Integration with Other Skills

| Skill | Integration |
|-------|-------------|
| knowledge-base | ADR을 knowledge entry로 연결 |
| insight-collector | 관련 insight 링크 |
| review-assistant | 결정 준수 체크리스트 생성 |

## Superseding ADRs

기존 결정을 대체할 때:

1. 기존 ADR 상태를 `Superseded` 로 변경
2. 새 ADR에 대체 사유 명시
3. 양방향 링크 추가

```markdown
# ADR-001: JWT Authentication (SUPERSEDED)

**Status**: Superseded by [ADR-005](ADR-005-oauth2-migration.md)
```

## Boundaries

**Will:**
- 결정 발생 시 즉시 ADR 생성
- 순차적 ID 관리
- 관련 ADR 간 링크 유지
- 상태 변경 추적

**Will Not:**
- 결정 자체를 내리는 것 (기록만 함)
- 사용자 확인 없이 기존 ADR 수정
- 자동으로 ADR 삭제 또는 만료
