---
name: insight-collector
description: Protocol for saving insights immediately when generated. When you create an insight block (★ Insight), you MUST save it to .caw/insights/ in the same turn using the Write tool.
allowed-tools: Read, Write, Glob
---

# Insight Collector

Immediate-save protocol for capturing valuable insights during workflow execution.

## Core Principle

**Insight 생성 = 즉시 저장**

인사이트를 생성하면 같은 턴에 반드시 저장합니다. 나중에 감지하는 방식이 아닌, 생성 시점에 저장하는 방식입니다.

## Insight Generation Protocol

### Step 1: Generate Insight Block

인사이트를 사용자에게 표시:

```
★ Insight ─────────────────────────────────────
[2-3 key educational points]
─────────────────────────────────────────────────
```

### Step 2: Immediately Save (Same Turn)

인사이트 블록 출력 직후, Write 도구로 즉시 저장:

```yaml
action: Write tool
path: .caw/insights/{date}-{slug}.md
content: |
  # Insight: [Title]

  ## Metadata
  | Field | Value |
  |-------|-------|
  | **Captured** | [timestamp] |
  | **Context** | [current task or topic] |

  ## Content

  [Original insight content]

  ## Tags

  [Auto-generated tags]
```

### Step 3: Brief Confirmation

저장 완료 후 한 줄 확인:

```
💡 Insight saved: [title]
```

## File Naming Convention

**Pattern**: `{YYYYMMDD}-{slug}.md`

- date: 오늘 날짜 (예: 20260104)
- slug: 제목에서 3-5단어, kebab-case

**Examples**:
- `20260104-jwt-token-refresh-pattern.md`
- `20260104-react-state-management.md`
- `20260104-error-handling-strategy.md`

## Insight File Template

```markdown
# Insight: [Generated Title]

## Metadata
| Field | Value |
|-------|-------|
| **Captured** | YYYY-MM-DD HH:MM |
| **Context** | [Task/Phase/Topic] |
| **Related Files** | [comma-separated if any] |

## Content

[Original insight content - preserved exactly as generated]

## Tags

#tag1 #tag2 #tag3
```

## Tag Generation Rules

인사이트 내용을 분석하여 자동으로 태그 생성:

| Content Pattern | Tag |
|-----------------|-----|
| auth, authentication, login, jwt, token | #authentication |
| security, vulnerability, xss, csrf | #security |
| performance, optimize, cache, speed | #performance |
| test, testing, coverage, mock | #testing |
| api, endpoint, rest, graphql | #api |
| database, query, sql, orm | #database |
| react, vue, angular, frontend | #frontend |
| node, express, backend, server | #backend |
| pattern, architecture, design | #architecture |
| error, exception, handling | #error-handling |

## Directory Structure

```
.caw/
└── insights/
    ├── index.md                          # Master index (optional)
    ├── 20260104-jwt-token-refresh.md
    ├── 20260104-middleware-pattern.md
    └── 20260103-error-handling.md
```

## When to Generate Insights

인사이트는 다음 상황에서 생성합니다:

1. **Implementation Discovery**: 구현 중 발견한 유용한 패턴
2. **Problem Solution**: 문제 해결 과정에서 얻은 교훈
3. **Best Practice**: 프로젝트에 특화된 모범 사례
4. **Gotcha/Pitfall**: 주의해야 할 함정이나 실수
5. **Architecture Decision**: 중요한 설계 결정의 근거

## Example Flow

```
1. 사용자: "JWT 토큰 갱신 로직을 구현해줘"

2. 모델: JWT 구현 진행...

3. 모델: 인사이트 발견 및 표시
   ★ Insight ─────────────────────────────────────
   JWT 토큰 갱신은 만료 전에 수행해야 합니다:
   - 만료 5분 전 자동 갱신 권장
   - 클라이언트에서 타이머 관리 필요
   ─────────────────────────────────────────────────

4. 모델: 즉시 Write 도구 호출
   → .caw/insights/20260104-jwt-token-refresh-timing.md 저장

5. 모델: 확인 메시지
   💡 Insight saved: JWT 토큰 갱신 타이밍
```

## Integration with Workflow

### CAW Workflow Active

워크플로우가 활성화된 경우, 메타데이터에 Phase/Step 정보 포함:

```markdown
## Metadata
| Field | Value |
|-------|-------|
| **Captured** | 2026-01-04 15:30 |
| **Context** | JWT Authentication Implementation |
| **Phase** | Phase 2: Core Implementation |
| **Step** | 2.3: Token Refresh Logic |
| **Related Files** | src/auth/jwt.ts, src/auth/refresh.ts |
```

### Without Workflow

워크플로우 없이 일반 대화에서도 인사이트 저장 가능:

```markdown
## Metadata
| Field | Value |
|-------|-------|
| **Captured** | 2026-01-04 15:30 |
| **Context** | General Discussion - React Patterns |
```

## Duplicate Handling

동일 날짜에 비슷한 주제의 인사이트:

1. slug에 숫자 추가: `20260104-jwt-refresh-2.md`
2. 또는 더 구체적인 slug 사용

## Boundaries

**Will:**
- 인사이트 생성 시 즉시 저장
- 메타데이터와 태그 자동 생성
- 원본 내용 정확히 보존

**Will Not:**
- 인사이트 내용 수정 또는 요약
- 사용자 확인 없이 기존 인사이트 덮어쓰기
- 자동으로 인사이트 삭제 또는 정리
