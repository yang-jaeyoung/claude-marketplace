# CAW Skill Ecosystem Design

Agent를 강화하는 자동화 Skill 설계 문서.

## 설계 원칙

1. **Command는 명시적 워크플로우** - 사용자가 직접 호출
2. **Skill은 Agent 강화** - Agent가 자동으로 활용
3. **Hook과 연동** - 이벤트 기반 자동 트리거
4. **Progressive Disclosure** - 필요 시에만 컨텍스트 로드

## Skill 카탈로그

---

### 1. plan-detector
**자동 Plan Mode 감지 및 워크플로우 시작**

| 속성 | 값 |
|------|-----|
| **트리거** | Plan Mode 완료 감지 |
| **출력** | `/cw:start --from-plan` 자동 제안 |
| **연동** | PostToolUse Hook (ExitPlanMode) |

**동작 흐름:**
```
1. PostToolUse Hook이 ExitPlanMode 감지
2. plan-detector Skill 활성화
3. Plan 파일 분석 (구현 가능 여부)
4. 사용자에게 워크플로우 시작 제안
```

**예시:**
```
🎯 Plan Mode 완료 감지

계획 파일: .claude/plans/auth-system.md
- 구현 단계: 5개 Phase, 12개 Step
- 예상 파일: 8개 수정, 3개 생성

자동으로 CAW 워크플로우를 시작할까요?
[1] 예, /cw:start --from-plan 실행
[2] 아니오, 나중에 수동으로 시작
```

**필요 파일:**
```
skills/plan-detector/
├── SKILL.md
└── patterns.md      # Plan 파일 패턴 정의
```

---

### 2. insight-collector
**모델 응답의 Insight 자동 수집 및 저장**

| 속성 | 값 |
|------|-----|
| **트리거** | 응답에 `★ Insight` 패턴 감지 |
| **출력** | `.caw/insights/` 폴더에 저장 |
| **연동** | PostToolUse Hook (모든 응답) |

**동작 흐름:**
```
1. 모델 응답 스캔
2. "★ Insight" 블록 추출
3. 메타데이터 추가 (날짜, 컨텍스트, 관련 파일)
4. .caw/insights/{date}-{topic}.md 저장
5. insights/index.md 업데이트
```

**저장 형식:**
```markdown
# Insight: [추출된 제목]

## Metadata
| Field | Value |
|-------|-------|
| **Captured** | 2026-01-04 15:30 |
| **Context** | JWT Authentication Implementation |
| **Related Files** | src/auth/middleware.ts |
| **Phase** | Phase 2: Core Implementation |

## Content
[원본 Insight 내용]

## Tags
#authentication #security #middleware
```

**필요 파일:**
```
skills/insight-collector/
├── SKILL.md
├── templates/
│   └── insight-template.md
└── scripts/
    └── extract_insights.py   # Insight 패턴 추출
```

---

### 3. context-helper
**Agent의 컨텍스트 이해 및 관리 지원**

| 속성 | 값 |
|------|-----|
| **트리거** | Agent가 컨텍스트 필요 시 |
| **출력** | 관련 컨텍스트 요약 제공 |
| **연동** | 모든 CAW Agent |

**기능:**
```
1. context_manifest.json 기반 파일 우선순위 제공
2. 현재 Phase/Step에 필요한 파일만 필터링
3. 이전 Phase 결과 요약 제공
4. 관련 Insight 연결
```

**Agent 사용 예시:**
```markdown
## Context Helper 호출

현재 작업: Phase 2, Step 2.3
필요 컨텍스트:
  ✅ src/auth/jwt.ts (Phase 2.1에서 생성)
  ✅ src/auth/middleware.ts (Phase 2.2에서 수정)
  📋 관련 Insight: "JWT 토큰 갱신 패턴"

권장 읽기 순서:
1. .caw/task_plan.md (현재 상태)
2. src/auth/jwt.ts (의존성)
3. .caw/insights/jwt-refresh-pattern.md
```

**필요 파일:**
```
skills/context-helper/
├── SKILL.md
└── context-strategies.md   # 컨텍스트 전략 정의
```

---

### 4. pattern-learner
**코드베이스 패턴 학습 및 Agent에 제공**

| 속성 | 값 |
|------|-----|
| **트리거** | /cw:start 시 자동, Agent 요청 시 |
| **출력** | `.caw/patterns/` 에 패턴 문서화 |
| **연동** | Planner, Builder Agent |

**학습 대상:**
```
1. 코딩 스타일 (naming, formatting)
2. 아키텍처 패턴 (디렉토리 구조, 모듈화)
3. 테스트 패턴 (테스트 파일 위치, 명명)
4. 에러 처리 패턴
5. API 응답 형식
```

**출력 예시:**
```markdown
# Learned Patterns: [Project Name]

## Naming Conventions
- Components: PascalCase (UserProfile.tsx)
- Utilities: camelCase (formatDate.ts)
- Constants: UPPER_SNAKE (MAX_RETRY_COUNT)

## Architecture Patterns
- Feature-based directory structure
- Barrel exports (index.ts)
- Separation: components/ hooks/ utils/

## Testing Patterns
- Test location: __tests__/ alongside source
- Naming: {filename}.test.ts
- Framework: Jest + React Testing Library

## Error Handling
- Custom error classes in errors/
- Try-catch with specific error types
- Consistent error response format
```

**필요 파일:**
```
skills/pattern-learner/
├── SKILL.md
├── analyzers/
│   ├── style-analyzer.md
│   ├── architecture-analyzer.md
│   └── test-analyzer.md
└── templates/
    └── patterns-template.md
```

---

### 5. decision-logger
**기술적 결정 자동 기록**

| 속성 | 값 |
|------|-----|
| **트리거** | AskUserQuestion 응답, 아키텍처 선택 |
| **출력** | `.caw/decisions/` ADR 형식 저장 |
| **연동** | Architect, Planner Agent |

**ADR (Architecture Decision Record) 형식:**
```markdown
# ADR-001: JWT vs Session Authentication

## Status
Accepted

## Context
사용자 인증 방식 선택 필요.
RESTful API 서버로 stateless 선호.

## Decision
JWT 기반 인증 채택

## Rationale
- Stateless: 서버 확장성
- Mobile 지원 용이
- Microservices 호환

## Consequences
- 토큰 갱신 로직 필요
- 토큰 크기로 인한 헤더 증가
- 즉시 무효화 어려움 (블랙리스트 필요)

## Alternatives Considered
1. Session-based: 서버 메모리 부담
2. OAuth only: 외부 의존성 증가
```

**필요 파일:**
```
skills/decision-logger/
├── SKILL.md
├── templates/
│   └── adr-template.md
└── scripts/
    └── generate_adr_id.py
```

---

### 6. progress-tracker
**작업 진행 상황 메트릭 추적**

| 속성 | 값 |
|------|-----|
| **트리거** | Step 완료, Phase 전환 |
| **출력** | `.caw/metrics.json` 업데이트 |
| **연동** | PostToolUse Hook, /cw:status |

**추적 메트릭:**
```json
{
  "task_id": "auth-jwt-impl",
  "started": "2026-01-04T10:00:00Z",
  "phases": {
    "phase_1": {
      "name": "Setup",
      "started": "2026-01-04T10:00:00Z",
      "completed": "2026-01-04T10:30:00Z",
      "duration_minutes": 30,
      "steps_total": 3,
      "steps_completed": 3
    },
    "phase_2": {
      "name": "Implementation",
      "started": "2026-01-04T10:30:00Z",
      "completed": null,
      "steps_total": 5,
      "steps_completed": 2
    }
  },
  "overall_progress": 0.45,
  "estimated_completion": "2026-01-04T12:00:00Z",
  "blockers": [],
  "insights_captured": 3
}
```

**필요 파일:**
```
skills/progress-tracker/
├── SKILL.md
└── scripts/
    └── calculate_metrics.py
```

---

### 7. quality-gate
**Step 완료 전 품질 검증**

| 속성 | 값 |
|------|-----|
| **트리거** | Builder가 Step 완료 선언 시 |
| **출력** | 검증 결과, 통과/실패 |
| **연동** | Builder, Reviewer Agent |

**검증 항목:**
```
1. 코드 변경 사항 존재 확인
2. 린트/타입체크 통과
3. 관련 테스트 통과
4. task_plan.md 상태 업데이트 확인
5. 패턴 준수 확인 (pattern-learner 연동)
```

**검증 결과:**
```
🔍 Quality Gate: Step 2.3

Checks:
  ✅ Code changes detected (3 files)
  ✅ TypeScript compilation passed
  ✅ ESLint passed (0 errors)
  ⚠️ Tests: 2 passed, 1 skipped
  ✅ task_plan.md updated
  ✅ Naming conventions followed

Result: PASSED (with warnings)

Warnings:
  - 1 test skipped in auth.test.ts:45

Proceed to next step? [Y/n]
```

**필요 파일:**
```
skills/quality-gate/
├── SKILL.md
├── checks/
│   ├── code-checks.md
│   ├── test-checks.md
│   └── pattern-checks.md
└── scripts/
    └── run_checks.py
```

---

### 8. knowledge-base
**프로젝트 지식 축적 및 검색**

| 속성 | 값 |
|------|-----|
| **트리거** | Agent 질문, 세션 종료 |
| **출력** | `.caw/knowledge/` 지식 저장소 |
| **연동** | 모든 Agent |

**지식 유형:**
```
1. 코드베이스 구조 (자동 생성)
2. 외부 의존성 정보
3. 비즈니스 로직 설명
4. 트러블슈팅 기록
5. 성능 최적화 노트
```

**구조:**
```
.caw/knowledge/
├── index.md                    # 지식 인덱스
├── codebase/
│   ├── structure.md            # 디렉토리 구조
│   └── dependencies.md         # 주요 의존성
├── domain/
│   ├── authentication.md       # 도메인 지식
│   └── user-management.md
├── troubleshooting/
│   └── common-errors.md        # 해결된 문제들
└── performance/
    └── optimization-notes.md
```

**필요 파일:**
```
skills/knowledge-base/
├── SKILL.md
├── templates/
│   ├── knowledge-entry.md
│   └── troubleshooting-entry.md
└── scripts/
    └── search_knowledge.py
```

---

### 9. session-persister
**세션 상태 저장 및 복구**

| 속성 | 값 |
|------|-----|
| **트리거** | 세션 시작, 수동 요청 |
| **출력** | `.caw/session.json` 세션 데이터 |
| **연동** | `/cw:status`, `/cw:start` |

**저장 데이터:**
```json
{
  "session_id": "sess_20260104_143000",
  "task_plan": ".caw/task_plan.md",
  "current_phase": "phase_2",
  "current_step": "2.3",
  "context_files": [
    "src/auth/jwt.ts",
    "src/auth/middleware.ts"
  ],
  "pending_questions": [],
  "last_checkpoint": "2026-01-04T14:45:00Z",
  "notes": "JWT 구현 중, 토큰 갱신 로직 작업 중"
}
```

**세션 복구:**
```
🔄 이전 세션 발견

Session: sess_20260104_143000
Task: JWT 인증 시스템 구현
Progress: Phase 2, Step 2.3 (45%)
Last Activity: 30분 전

[1] 이전 세션 이어서 진행
[2] 새 세션 시작 (이전 세션 아카이브)
[3] 세션 상태만 확인
```

**필요 파일:**
```
skills/session-persister/
├── SKILL.md
├── templates/
│   └── session-template.json
└── scripts/
    ├── save_session.py
    └── restore_session.py
```

---

### 10. review-assistant
**코드 리뷰 체크리스트 자동 생성**

| 속성 | 값 |
|------|-----|
| **트리거** | /cw:review 실행 시 |
| **출력** | 컨텍스트 기반 리뷰 체크리스트 |
| **연동** | Reviewer Agent |

**체크리스트 생성:**
```markdown
# Review Checklist: Phase 2 Implementation

## 기반 정보
- Pattern: src/auth/ 디렉토리 패턴
- Related Decisions: ADR-001 (JWT 선택)
- Insights: 3개 관련 Insight

## 자동 생성 체크리스트

### Security (JWT 관련)
- [ ] 토큰 만료 시간 적절한가?
- [ ] Refresh token 안전하게 저장되는가?
- [ ] 토큰 검증 로직 완전한가?

### Code Quality
- [ ] 기존 auth 패턴과 일관성 있는가?
- [ ] 에러 처리가 표준을 따르는가?
- [ ] 테스트 커버리지 충분한가?

### Performance
- [ ] 토큰 검증이 매 요청마다 효율적인가?
- [ ] 불필요한 DB 조회 없는가?
```

**필요 파일:**
```
skills/review-assistant/
├── SKILL.md
├── checklists/
│   ├── security-checklist.md
│   ├── performance-checklist.md
│   └── quality-checklist.md
└── templates/
    └── review-template.md
```

---

## Hook 연동 설계

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": {
          "tool_name": "ExitPlanMode"
        },
        "hooks": [
          {
            "type": "skill",
            "skill": "plan-detector"
          }
        ]
      },
      {
        "matcher": {
          "response_pattern": "★ Insight"
        },
        "hooks": [
          {
            "type": "skill",
            "skill": "insight-collector"
          }
        ]
      },
      {
        "matcher": {
          "tool_name": "Edit",
          "context": "caw_workflow_active"
        },
        "hooks": [
          {
            "type": "skill",
            "skill": "progress-tracker"
          }
        ]
      }
    ],
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "skill",
            "skill": "session-persister",
            "action": "restore"
          }
        ]
      }
    ],
    "Stop": [
      {
        "hooks": [
          {
            "type": "skill",
            "skill": "session-persister",
            "action": "save"
          }
        ]
      }
    ]
  }
}
```

---

## Agent-Skill 매핑

| Agent | 사용 Skills |
|-------|-------------|
| **Planner** | pattern-learner, context-helper, decision-logger |
| **Builder** | context-helper, quality-gate, progress-tracker |
| **Reviewer** | review-assistant, pattern-learner, insight-collector |
| **ComplianceChecker** | quality-gate, knowledge-base |
| **Ideator** | knowledge-base, insight-collector |
| **Designer** | pattern-learner, decision-logger |
| **Architect** | decision-logger, knowledge-base, pattern-learner |

---

## 구현 우선순위 제안

### Tier 1: 핵심 (즉시 가치)
1. **plan-detector** - Plan Mode 연동 자동화
2. **insight-collector** - 지식 자동 축적
3. **session-persister** - 세션 연속성

### Tier 2: 품질 강화
4. **quality-gate** - 자동 품질 검증
5. **progress-tracker** - 진행 상황 가시화
6. **context-helper** - Agent 효율성 향상

### Tier 3: 지식 관리
7. **pattern-learner** - 코드베이스 학습
8. **decision-logger** - 의사결정 기록
9. **knowledge-base** - 지식 축적

### Tier 4: 고급 기능
10. **review-assistant** - 리뷰 자동화

---

## 디렉토리 구조

```
context-aware-workflow/
├── .claude-plugin/
│   └── plugin.json
├── agents/
│   └── *.md
├── commands/
│   └── *.md
├── skills/                    # NEW
│   ├── plan-detector/
│   │   └── SKILL.md
│   ├── insight-collector/
│   │   ├── SKILL.md
│   │   └── templates/
│   ├── session-persister/
│   │   ├── SKILL.md
│   │   └── scripts/
│   └── ...
├── hooks/
│   └── hooks.json            # Updated
└── docs/
    └── SKILL_DESIGN.md       # This file
```

---

## 선택 가이드

어떤 Skill을 구현할지 선택해주세요:

| # | Skill | 복잡도 | 즉시 가치 | 의존성 |
|---|-------|--------|----------|--------|
| 1 | plan-detector | 낮음 | 높음 | Hook |
| 2 | insight-collector | 중간 | 높음 | Hook |
| 3 | session-persister | 중간 | 높음 | Hook |
| 4 | quality-gate | 중간 | 중간 | Builder |
| 5 | progress-tracker | 낮음 | 중간 | Hook |
| 6 | context-helper | 낮음 | 중간 | - |
| 7 | pattern-learner | 높음 | 중간 | - |
| 8 | decision-logger | 낮음 | 낮음 | - |
| 9 | knowledge-base | 높음 | 낮음 | - |
| 10 | review-assistant | 중간 | 낮음 | Reviewer |
