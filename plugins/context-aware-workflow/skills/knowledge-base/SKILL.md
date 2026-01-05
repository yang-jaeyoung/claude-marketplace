---
name: knowledge-base
description: Centralized knowledge repository for capturing, organizing, and retrieving project knowledge. Used by all agents for context and learning. Invoked when agents need project-specific knowledge or when capturing important information.
allowed-tools: Read, Write, Glob, Grep
---

# Knowledge Base

Centralized repository for capturing, organizing, and retrieving project-specific knowledge.

## Core Principle

**지식 축적 = 컨텍스트 보존**

프로젝트에서 학습한 중요한 정보를 체계적으로 저장하여, 새 세션에서도 동일한 컨텍스트를 유지합니다.

## Triggers

이 Skill은 다음 상황에서 활성화됩니다:

1. **Agent 질문**
   - "이 프로젝트에서 X는 어떻게 동작하나요?"
   - 사용자에게 묻기 전에 knowledge-base 먼저 검색

2. **세션 완료**
   - 워크플로우 종료 시 지식 정리
   - 중요 정보 자동 캡처

3. **명시적 요청**
   - "이 정보를 저장해줘"
   - "knowledge-base에 추가"

4. **관련 정보 발견**
   - 도메인 규칙 발견 시
   - 중요한 기술적 세부사항 파악 시

## Knowledge Categories

| Category | Description | Examples |
|----------|-------------|----------|
| **domain/** | 비즈니스 로직, 도메인 규칙 | 주문 처리 규칙, 가격 정책 |
| **technical/** | 기술적 구현 세부사항 | API 연동 방법, 설정 값 |
| **conventions/** | 프로젝트 규칙 | 코딩 표준, 브랜치 전략 |
| **gotchas/** | 주의사항, 함정 | 알려진 버그, 비직관적 동작 |
| **integrations/** | 외부 서비스 연동 | API 키 위치, 엔드포인트 |

## Behavior

### Step 1: Knowledge Detection

캡처할 가치가 있는 정보 식별:

```yaml
detection:
  high_value:
    - Domain rules: "X일 때 Y해야 함"
    - Configuration: "환경변수 Z 필요"
    - Gotchas: "이렇게 하면 안 됨"
    - Integration details: "API는 이렇게 호출"

  sources:
    - insight-collector: 캡처된 인사이트
    - decision-logger: 기록된 결정
    - 대화 중 발견된 정보
    - 코드 주석/문서
```

### Step 2: Categorize

적절한 카테고리 할당:

```yaml
categorization:
  domain:
    keywords: ["business", "rule", "policy", "when", "must"]
    examples: ["주문이 $100 이상이면 무료배송"]

  technical:
    keywords: ["implementation", "config", "setup", "api"]
    examples: ["Redis 캐시 TTL은 1시간"]

  conventions:
    keywords: ["standard", "convention", "always", "never"]
    examples: ["모든 API는 JSON:API 형식"]

  gotchas:
    keywords: ["careful", "don't", "avoid", "bug", "issue"]
    examples: ["Date.now()는 테스트에서 flaky"]

  integrations:
    keywords: ["external", "third-party", "api", "service"]
    examples: ["Stripe webhook secret 위치"]
```

### Step 3: Create Entry

지식 항목 생성:

```yaml
action: Write tool
path: .caw/knowledge/{category}/{slug}.md
content: See Knowledge Entry Template
```

### Step 4: Update Index

인덱스 파일 업데이트:

```yaml
action: Write tool
path: .caw/knowledge/index.json
content:
  entries:
    - id: kb-{NNN}
      title: "..."
      category: ["technical", "architecture"]
      keywords: ["jwt", "auth"]
      path: "technical/jwt-implementation.md"
```

### Step 5: Confirm

저장 완료 확인:

```
📚 Knowledge saved: {title}
   Category: {category}
   Path: .caw/knowledge/{path}
```

## Knowledge Entry Template

See [templates/knowledge-entry.md](templates/knowledge-entry.md) for the full template.

```markdown
# {Title}

## Metadata
| Field | Value |
|-------|-------|
| **ID** | kb-{NNN} |
| **Category** | {primary} > {sub} |
| **Created** | YYYY-MM-DD |
| **Updated** | YYYY-MM-DD |
| **Sources** | insight / decision / code / conversation |

## Summary
[1-2 sentence summary]

## Content
[Detailed knowledge content]

## Context
[When this knowledge applies]

## Related
- [Links to ADRs, insights, other entries]

## Keywords
#keyword1 #keyword2 #keyword3
```

## Directory Structure

```
.caw/
└── knowledge/
    ├── index.json                 # Master index
    │
    ├── domain/
    │   ├── order-processing.md
    │   └── pricing-rules.md
    │
    ├── technical/
    │   ├── architecture/
    │   │   └── service-layer.md
    │   └── integrations/
    │       └── stripe-webhook.md
    │
    ├── conventions/
    │   └── api-response-format.md
    │
    └── gotchas/
        ├── date-handling.md
        └── async-testing.md
```

## Index File Format

```json
{
  "version": "1.0",
  "last_updated": "2026-01-04T15:30:00Z",
  "entries": [
    {
      "id": "kb-001",
      "title": "JWT Token Refresh Strategy",
      "category": ["technical", "architecture"],
      "keywords": ["jwt", "auth", "token", "refresh"],
      "path": "technical/architecture/jwt-refresh.md",
      "related": ["ADR-001", "insight-20260104-jwt"],
      "created": "2026-01-04",
      "sources": ["decision", "insight"]
    }
  ],
  "categories": {
    "domain": {"count": 5},
    "technical": {"count": 12},
    "conventions": {"count": 3},
    "gotchas": {"count": 8}
  }
}
```

## Search Behavior

Agent가 지식을 검색할 때:

```yaml
search:
  methods:
    keyword:
      - Match against keywords array
      - Match against title
      weight: 1.0

    category:
      - Filter by category path
      weight: 0.8

    full_text:
      - Search content body
      weight: 0.5

    related:
      - Follow relationship links
      weight: 0.6

  ranking:
    - Exact match: highest
    - Multiple keyword match: high
    - Category match: medium
    - Content match: lower
```

## Example Flow

### Capturing Knowledge

```
1. 사용자: "주문 금액이 $100 이상이면 무료배송이에요"

2. 모델: 도메인 규칙 감지
   → 이것은 비즈니스 규칙입니다

3. 모델: Knowledge entry 생성
   📚 Knowledge saved: Order Free Shipping Rule
      Category: domain
      Path: .caw/knowledge/domain/order-free-shipping.md

4. 저장 내용:
   # Order Free Shipping Rule

   ## Summary
   Orders $100 or more qualify for free shipping.

   ## Content
   - Threshold: $100 (before tax)
   - Applies to: All shipping methods
   - Exclusions: None currently

   ## Keywords
   #order #shipping #pricing
```

### Retrieving Knowledge

```
1. Builder: "배송비 계산 로직을 구현해야 하는데..."

2. knowledge-base 검색:
   Query: "shipping", "order", "pricing"
   Result: kb-005 Order Free Shipping Rule

3. Builder에게 컨텍스트 제공:
   📚 Related knowledge found:
   - Order Free Shipping Rule (domain)
     "Orders $100+ get free shipping"
```

## Integration with Agents

| Agent | Usage |
|-------|-------|
| **Planner** | 도메인 규칙 확인하여 계획 수립 |
| **Builder** | 구현 전 관련 지식 검색 |
| **Reviewer** | 규칙 준수 여부 확인 |
| **Architect** | 기존 아키텍처 결정 참조 |
| **All** | 사용자에게 묻기 전 지식 검색 |

## Integration with Other Skills

| Skill | Integration |
|-------|-------------|
| **insight-collector** | 인사이트를 지식으로 승격 |
| **decision-logger** | ADR을 지식으로 연결 |
| **context-helper** | 관련 지식을 컨텍스트로 제공 |
| **session-persister** | 세션 종료 시 지식 정리 |

## Knowledge Lifecycle

```yaml
lifecycle:
  creation:
    - Auto-capture from insights/decisions
    - Manual addition

  update:
    - Edit existing entry
    - Add related links
    - Update keywords

  archival:
    - Mark as outdated (don't delete)
    - Link to replacement entry

  deletion:
    - Only with user explicit request
    - Keep in archive folder
```

## Auto-Capture Rules

자동으로 캡처해야 하는 정보:

```yaml
auto_capture:
  from_insights:
    condition: Insight marked as "persistent"
    action: Create knowledge entry

  from_decisions:
    condition: All accepted ADRs
    action: Link in knowledge index

  from_conversation:
    patterns:
      - "Remember that..."
      - "Important: ..."
      - "Note: ..."
      - "기억해야 할 것: ..."
    action: Prompt for knowledge capture
```

## Boundaries

**Will:**
- 프로젝트 지식 체계적 저장
- 카테고리별 정리 및 인덱싱
- 키워드 기반 검색 제공
- 관련 항목 간 링크 유지

**Will Not:**
- 사용자 확인 없이 지식 삭제
- 민감 정보 저장 (credentials, secrets)
- 자동으로 지식 만료 처리
- 외부 시스템과 동기화
