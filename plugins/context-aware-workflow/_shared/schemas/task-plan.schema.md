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
| **Methodology** | Tidy First (Kent Beck) |

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

| # | Step | Type | Status | Agent | Deps | Notes |
|---|------|------|--------|-------|------|-------|
| N.0 | [structural prep] | 🧹 Tidy | ⏳ | Builder | - | |
| N.1 | [behavioral change] | 🔨 Build | ⏳ | Builder | N.0 | |

## Validation Checklist
- [ ] Tests pass
- [ ] Follows conventions
- [ ] Tidy commits separate from Build commits

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

## Step Type Column (Tidy First)

Kent Beck의 Tidy First 방법론에 따라 모든 Step은 Type을 명시합니다.

| Icon | Type | Description | Commit Prefix |
|------|------|-------------|---------------|
| 🧹 | Tidy | 구조적 변경 (동작 변화 없음) | `[tidy]` |
| 🔨 | Build | 동작 변경 (새 기능, 버그 수정) | `[feat]`, `[fix]` |
| 🔧 | Refactor | 혼합 변경 (가급적 피함) | `[refactor]` |

### Tidy First 원칙

1. **구조적 변경 먼저**: 동작 변경 전에 코드 정리
2. **커밋 분리**: Tidy와 Build 커밋을 절대 혼합하지 않음
3. **작은 단위**: 각 변경은 최소 단위로

### Tidy Step 예시

| 작업 | Type | 설명 |
|------|------|------|
| 변수/함수 이름 변경 | 🧹 Tidy | 명확한 네이밍 |
| 메서드 추출 | 🧹 Tidy | 중복 코드 분리 |
| 파일 재구성 | 🧹 Tidy | 디렉토리 정리 |
| 사용하지 않는 코드 제거 | 🧹 Tidy | Dead code 삭제 |
| 의존성 명시화 | 🧹 Tidy | 암시적 의존성 노출 |

### Build Step 예시

| 작업 | Type | 설명 |
|------|------|------|
| 새 함수 추가 | 🔨 Build | 새 기능 |
| 로직 수정 | 🔨 Build | 동작 변경 |
| 버그 수정 | 🔨 Build | 결함 수정 |
| 테스트 추가 | 🔨 Build | 새 테스트 케이스 |

### Step 순서 규칙

```
Phase N:
  N.0 [Tidy] 구조적 정리  ─┐
  N.1 [Tidy] 리팩토링     ─┼─ Tidy 먼저
  N.2 [Build] 기능 구현   ─┤
  N.3 [Build] 테스트      ─┘ Build 나중
```

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

## Example: Full Task Plan (Tidy First)

```markdown
# Task Plan: User Authentication System

## Metadata
| Field | Value |
|-------|-------|
| **Created** | 2026-01-16 10:00 |
| **Source** | User request |
| **Status** | In Progress |
| **Methodology** | Tidy First (Kent Beck) |

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
JWT 기반 사용자 인증 시스템을 구현합니다. Tidy First 방법론에 따라 구조적 정리 후 기능을 구현합니다.

## Execution Phases

### Phase 1: Setup
**Phase Deps**: -

| # | Step | Type | Status | Agent | Deps | Notes |
|---|------|------|--------|-------|------|-------|
| 1.1 | 의존성 설치 (jsonwebtoken, bcrypt) | 🔨 Build | ✅ | Builder | - | |
| 1.2 | 타입 정의 추가 | 🔨 Build | ✅ | Builder | - | ⚡ 1.1과 병렬 |
| 1.3 | 테스트 fixture 설정 | 🔨 Build | ✅ | Builder | - | ⚡ 병렬 가능 |

### Phase 2: Core Implementation
**Phase Deps**: phase 1

| # | Step | Type | Status | Agent | Deps | Notes |
|---|------|------|--------|-------|------|-------|
| 2.0 | 기존 auth 코드 정리 | 🧹 Tidy | ✅ | Builder | - | 네이밍 개선 |
| 2.1 | JWT 유틸리티 함수 구현 | 🔨 Build | 🔄 | Builder | 2.0 | |
| 2.2 | 토큰 생성 함수 | 🔨 Build | ⏳ | Builder | 2.1 | |
| 2.3 | 토큰 검증 함수 | 🔨 Build | ⏳ | Builder | 2.1 | ⚡ 2.2와 병렬 |
| 2.4 | 인증 미들웨어 | 🔨 Build | ⏳ | Builder | 2.2, 2.3 | |

### Phase 3: API Layer
**Phase Deps**: phase 1

| # | Step | Type | Status | Agent | Deps | Notes |
|---|------|------|--------|-------|------|-------|
| 3.0 | User 모델 리팩토링 | 🧹 Tidy | ⏳ | Builder | - | 필드명 정규화 |
| 3.1 | User 모델 확장 | 🔨 Build | ⏳ | Builder | 3.0 | |
| 3.2 | 비밀번호 해싱 유틸리티 | 🔨 Build | ⏳ | Builder | 3.0 | ⚡ 3.1과 병렬 |
| 3.3 | 회원가입 엔드포인트 | 🔨 Build | ⏳ | Builder | 3.1, 3.2 | |

### Phase 4: Integration
**Phase Deps**: phase 2, phase 3

| # | Step | Type | Status | Agent | Deps | Notes |
|---|------|------|--------|-------|------|-------|
| 4.1 | 로그인 엔드포인트 | 🔨 Build | ⏳ | Builder | - | |
| 4.2 | 인증 라우트 보호 적용 | 🔨 Build | ⏳ | Builder | 4.1 | |
| 4.3 | 통합 테스트 | 🔨 Build | ⏳ | Builder | 4.2 | |

## Validation Checklist
- [ ] 모든 테스트 통과
- [ ] 프로젝트 컨벤션 준수
- [ ] 보안 검토 완료
- [ ] Tidy/Build 커밋 분리 확인

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
/cw:next --worktree phase 2

# 터미널 2
/cw:next --worktree phase 3

# 각 worktree에서
cd .worktrees/phase-2 && claude
/cw:next --parallel phase 2  # 2.2, 2.3 병렬 실행

# 완료 후 메인에서
/cw:merge --all
```
