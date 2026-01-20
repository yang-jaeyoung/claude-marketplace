# plansDirectory 설정 지원 구현 계획

## 개요

Claude Code의 `plansDirectory` 설정을 CAW 플러그인에서 지원하도록 수정.

## 배경

- Claude Code 업데이트로 `plansDirectory` 설정 추가됨
- 현재 CAW는 `.claude/plan.md`, `.claude/plans/` 경로가 하드코딩됨
- 커스텀 경로 사용 시 Plan Mode 자동 감지가 실패함

## 설정 우선순위

```
1. .claude/settings.local.json   (프로젝트 로컬, 최우선)
2. .claude/settings.json         (프로젝트)
3. ~/.claude/settings.json       (전역)
4. 기본값: .claude/plans/
```

## 수정 파일 목록

### 1. 새 파일 생성

| 파일 | 목적 |
|------|------|
| `_shared/plans-directory-resolution.md` | 공통 경로 해석 지침 |

### 2. 기존 파일 수정

| 파일 | 수정 내용 |
|------|----------|
| `agents/bootstrapper.md` (204-224줄) | Step 4: Plan 감지 로직에 설정 해석 추가 |
| `commands/start.md` (95-96, 279-282줄) | Plan Mode 감지 경로 동적 해석 |
| `commands/init.md` (130줄) | 출력 메시지 업데이트 |
| `skills/plan-detector/SKILL.md` (3, 20, 30줄) | 감지 경로 동적 해석 |
| `_shared/schemas/manifest.schema.md` (26줄) | plansDirectory 필드 추가 |
| `docs/design/04_plan_mode_integration.md` (37-38줄) | DEFAULT_PLAN_PATHS 로직 수정 |
| `README.md` (55, 89줄) | 문서 업데이트 |

## 구현 단계

### Phase 1: 공통 지침 파일 생성

**파일**: `_shared/plans-directory-resolution.md`

```markdown
# Plans Directory Resolution

## 설정 읽기 절차

1. Read `.claude/settings.local.json` → `plansDirectory` 확인
2. 없으면 → Read `.claude/settings.json`
3. 없으면 → Read `~/.claude/settings.json`
4. 없으면 → 기본값 `.claude/plans/`

## 경로 해석

- 절대 경로 (/) → 그대로 사용
- 상대 경로 → 프로젝트 루트 기준

## Plan 파일 검색 순서

1. {plansDirectory}/current.md
2. {plansDirectory}/*.md
3. .claude/plan.md (레거시, 항상 확인)
```

### Phase 2: bootstrapper.md 수정

**위치**: line 202-224 (Step 4: Detect Existing Plans)

**변경 내용**:
```markdown
### Step 4: Detect Existing Plans

**First, resolve plansDirectory setting:**

1. Check settings files (priority order):
   - Read `.claude/settings.local.json` → extract "plansDirectory"
   - If not found: Read `.claude/settings.json`
   - If not found: Read `~/.claude/settings.json`
   - If not found: Use default ".claude/plans/"

2. Handle path types:
   - Absolute path (/) → Use as-is
   - Relative path → Resolve from project root

**Then, search for Plan Mode outputs:**

Glob: {plansDirectory}/current.md      # Active plan
Glob: {plansDirectory}/*.md            # All plans
Glob: .claude/plan.md                   # Legacy (always check)
Glob: plan.md, PLAN.md                  # Project root
```

### Phase 3: start.md 수정

**위치 1**: line 94-103 (Mode 2)

**변경 내용**:
```markdown
1. **Resolve plansDirectory** (참조: _shared/plans-directory-resolution.md)
2. **Detect** Plan Mode output:
   - Check `{plansDirectory}/*.md`
   - Check `.claude/plan.md` (레거시)
```

**위치 2**: line 278-292 (자동 감지)

**변경 내용**:
```markdown
/cw:start 실행 시:
1. plansDirectory 설정 해석
2. Plan Mode 파일 확인:
   - {plansDirectory}/*.md
   - .claude/plan.md (레거시)
```

### Phase 4: plan-detector/SKILL.md 수정

**위치**: line 3 (description), line 20, line 30

**변경 내용**:
- description에 "configured plansDirectory" 추가
- 감지 조건에 설정 해석 단계 추가
- 검색 경로를 동적으로 변경

### Phase 5: 스키마 및 문서 업데이트

**manifest.schema.md**:
```json
"plans": {
  "plansDirectory": ".claude/plans/",  // 해석된 경로
  "detected": [...],
  "active": null
}
```

**README.md**: plansDirectory 설정 지원 문서화

## 검증 방법

### 테스트 1: 기본 동작
```bash
# 설정 없는 상태에서 기본 경로 사용 확인
rm -f .claude/settings*.json
/cw:start --from-plan
# 예상: .claude/plans/ 에서 검색
```

### 테스트 2: 커스텀 경로
```bash
# settings.local.json에 plansDirectory 설정
echo '{"plansDirectory": ".plans/"}' > .claude/settings.local.json
/cw:start --from-plan
# 예상: .plans/ 에서 검색
```

### 테스트 3: 레거시 호환성
```bash
# 커스텀 경로 설정 상태에서 레거시 경로도 확인
touch .claude/plan.md
/cw:start --from-plan
# 예상: .plans/와 .claude/plan.md 둘 다 감지
```

## 핵심 원칙

1. **하위 호환성**: `.claude/plan.md`는 항상 확인 (레거시 지원)
2. **설정 우선순위**: local > project > global > default
3. **에러 처리**: 설정 파일 없거나 파싱 실패 시 기본값 사용
