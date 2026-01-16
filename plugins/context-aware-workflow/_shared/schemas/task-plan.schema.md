# Task Plan Schema

Location: `.caw/task_plan.md`

## Structure

```markdown
# Task Plan: [Title]

## Metadata
| Field | Value |
|-------|-------|
| **Created** | [timestamp] |
| **Source** | User request / Plan Mode import |
| **Status** | Planning / In Progress / Complete |

## Context Files
### Active Context
| File | Reason | Status |
|------|--------|--------|
| `path/file` | [reason] | 📝 Edit / 👁️ Read |

### Project Context (Read-Only)
- `GUIDELINES.md`
- `package.json`

## Task Summary
[2-3 sentence summary]

## Execution Phases

### Phase N: [Name]
**Phase Deps**: - | phase N | phase N, M

| # | Step | Status | Agent | Deps | Notes |
|---|------|--------|-------|------|-------|
| N.1 | [description] | ⏳/🔄/✅/❌ | Builder | - | |

## Validation Checklist
- [ ] Tests pass
- [ ] Follows conventions

## Open Questions
- [Unresolved items]
```

## Phase Dependency Notation

### Phase-Level Dependencies (Phase Deps)

Phase 간 의존성을 명시합니다. 선행 Phase가 완료되어야 해당 Phase를 시작할 수 있습니다.

| Notation | Meaning | Example |
|----------|---------|---------|
| `-` | 독립적, 즉시 시작 가능 | Phase 1 (Setup) |
| `phase N` | Phase N 완료 후 시작 | `phase 1` |
| `phase N, M` | Phase N과 M 모두 완료 후 | `phase 2, 3` |

**병렬 실행 가능 판단**:
- 동일한 Phase Deps를 가진 Phase들은 병렬 실행 가능
- 예: Phase 2 (`phase 1`), Phase 3 (`phase 1`) → 병렬 가능

### Step-Level Dependencies (Deps Column)

Step 간 의존성을 명시합니다.

| Notation | Meaning | Example |
|----------|---------|---------|
| `-` | 독립적, 해당 Phase 시작 시 즉시 실행 가능 | |
| `N.M` | 특정 Step 완료 후 실행 | `2.1` |
| `N.M, N.K` | 여러 Step 완료 후 실행 | `2.1, 2.3` |
| `N.*` | Phase N 전체 완료 후 실행 | `1.*` |
| `!N.M` | Step N.M과 동시 실행 불가 (mutual exclusion) | `!2.3` |

## Status Icons

| Icon | Status | Description |
|------|--------|-------------|
| ⏳ | Pending | 실행 대기 중 |
| 🔄 | In Progress | 실행 중 |
| ✅ | Complete | 완료 |
| ❌ | Blocked | 차단됨 (의존성 미충족 또는 오류) |
| ⏭️ | Skipped | 건너뜀 |
| 🌳 | In Worktree | 별도 worktree에서 작업 중 |

## Agent Column

| Value | Description |
|-------|-------------|
| Builder | 기본 구현 에이전트 |
| Builder-Haiku | 간단한 작업용 경량 에이전트 |
| Builder-Opus | 복잡한 작업용 고급 에이전트 |
| Reviewer | 코드 리뷰 에이전트 |

## Example: Full Task Plan

```markdown
# Task Plan: User Authentication System

## Metadata
| Field | Value |
|-------|-------|
| **Created** | 2026-01-16 10:00 |
| **Source** | User request |
| **Status** | In Progress |

## Context Files
### Active Context
| File | Reason | Status |
|------|--------|--------|
| `src/auth/jwt.ts` | JWT 유틸리티 구현 | 📝 Edit |
| `src/middleware/auth.ts` | 인증 미들웨어 | 📝 Edit |

### Project Context (Read-Only)
- `package.json`
- `tsconfig.json`

## Task Summary
JWT 기반 사용자 인증 시스템을 구현합니다. 토큰 생성/검증, 미들웨어, 로그인 엔드포인트를 포함합니다.

## Execution Phases

### Phase 1: Setup
**Phase Deps**: -

| # | Step | Status | Agent | Deps | Notes |
|---|------|--------|-------|------|-------|
| 1.1 | 의존성 설치 (jsonwebtoken, bcrypt) | ✅ | Builder | - | |
| 1.2 | 타입 정의 추가 | ✅ | Builder | - | ⚡ 1.1과 병렬 가능 |
| 1.3 | 테스트 fixture 설정 | ✅ | Builder | - | ⚡ 1.1, 1.2와 병렬 가능 |

### Phase 2: Core Implementation
**Phase Deps**: phase 1

| # | Step | Status | Agent | Deps | Notes |
|---|------|--------|-------|------|-------|
| 2.1 | JWT 유틸리티 함수 구현 | 🔄 | Builder | - | |
| 2.2 | 토큰 생성 함수 | ⏳ | Builder | 2.1 | |
| 2.3 | 토큰 검증 함수 | ⏳ | Builder | 2.1 | ⚡ 2.2와 병렬 가능 |
| 2.4 | 인증 미들웨어 | ⏳ | Builder | 2.2, 2.3 | |

### Phase 3: API Layer
**Phase Deps**: phase 1

| # | Step | Status | Agent | Deps | Notes |
|---|------|--------|-------|------|-------|
| 3.1 | User 모델 정의 | ⏳ | Builder | - | |
| 3.2 | 비밀번호 해싱 유틸리티 | ⏳ | Builder | - | ⚡ 3.1과 병렬 가능 |
| 3.3 | 회원가입 엔드포인트 | ⏳ | Builder | 3.1, 3.2 | |

### Phase 4: Integration
**Phase Deps**: phase 2, phase 3

| # | Step | Status | Agent | Deps | Notes |
|---|------|--------|-------|------|-------|
| 4.1 | 로그인 엔드포인트 | ⏳ | Builder | - | |
| 4.2 | 인증 라우트 보호 적용 | ⏳ | Builder | 4.1 | |
| 4.3 | 통합 테스트 | ⏳ | Builder | 4.2 | |

## Validation Checklist
- [ ] 모든 테스트 통과
- [ ] 프로젝트 컨벤션 준수
- [ ] 보안 검토 완료

## Open Questions
- 토큰 만료 시간 설정값?
```

## Parallel Execution Analysis

위 예시에서 병렬 실행 가능한 조합:

### Phase 병렬
- Phase 2와 Phase 3: 둘 다 `phase 1`에만 의존 → **병렬 가능**

### Step 병렬 (Phase 1 내)
- Step 1.1, 1.2, 1.3: 모두 `-` (독립) → **병렬 가능**

### Step 병렬 (Phase 2 내)
- Step 2.2, 2.3: 둘 다 `2.1`에만 의존 → **병렬 가능**

### Worktree 활용 예시

```bash
# Phase 1 완료 후

# 터미널 1 (메인)
/caw:next --worktree phase 2

# 터미널 2
/caw:next --worktree phase 3

# 각 worktree에서
cd .worktrees/phase-2 && claude
/caw:next --parallel phase 2  # 2.2, 2.3 병렬 실행

# 완료 후 메인에서
/caw:merge --all
```
