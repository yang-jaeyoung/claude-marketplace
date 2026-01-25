# Skill Loading Protocol

효율적인 스킬 로딩을 위한 라우팅 알고리즘 문서

## 개요

이 프로토콜은 사용자 쿼리를 분석하여 최적의 스킬을 최소 토큰으로 로드합니다.

**목표**: 토큰 효율성 85-90% 달성 (불필요한 스킬 로딩 방지)

## 라우팅 알고리즘

### 1단계: 쿼리 분석

```
INPUT: 사용자 쿼리 (예: "터보 프레임으로 댓글 시스템 만들기")

1. 키워드 추출
2. 언어 감지 (en/ko)
3. 의도 분류 (learn/implement/debug/deploy)
```

### 2단계: 트리거 매칭

```
FOR EACH skill IN MANIFEST.skills:
  score = calculate_trigger_match(query, skill.triggers)
  IF score > 0.3:
    candidates.add(skill, score)

SORT candidates BY score DESC
```

### 3단계: 조합 검사

```
FOR EACH composition IN MANIFEST.compositions:
  IF any(trigger IN query FOR trigger IN composition.triggers):
    RETURN load_composition(composition)
```

### 4단계: 의존성 해결

```
selected_skills = []
FOR skill IN top_candidates:
  selected_skills.add(skill)
  FOR dep IN skill.requires:
    IF dep NOT IN selected_skills:
      selected_skills.add(resolve_dependency(dep))
```

### 5단계: 깊이 결정

| 쿼리 유형 | 깊이 | 예시 |
|-----------|------|------|
| 개념 질문 | `shallow` | "터보 프레임이 뭐야?" |
| 구현 요청 | `standard` | "댓글 기능 추가해줘" |
| 심층 분석 | `deep` | "전체 인증 시스템 구축" |

```
depth = determine_depth(query_intent, query_complexity)
files_to_load = skill.load_depth[depth]
```

## 트리거 매칭 스코어링

### 정확 매칭 (1.0)
```
query: "turbo frame"
trigger: "turbo frame"
score: 1.0
```

### 부분 매칭 (0.5-0.9)
```
query: "터보 프레임 레이지 로딩"
trigger: "turbo frame"
score: 0.7
```

### 의미적 매칭 (0.3-0.5)
```
query: "페이지 일부분만 업데이트"
trigger: "partial update"
score: 0.4
```

## 토큰 비용 분류

| 레벨 | 토큰 범위 | 기준 | 예시 스킬 |
|------|----------|------|----------|
| `low` | <2,000 | 단일 개념, 작은 패턴 | views-forms-stimulus, background-imports |
| `medium` | 2,000-8,000 | 패턴+예제 포함 모듈 | core, views, recipes |
| `high` | >8,000 | 완전한 도메인 커버리지 | hotwire, models, auth, deploy |

## 로딩 깊이 전략

### Shallow (최소 로딩)
- SKILL.md만 로드
- 개념 설명, 빠른 참조용
- 예상 토큰: 500-1,500

### Standard (기본 로딩)
- SKILL.md + 핵심 하위 문서
- 구현 가이드, 패턴 참조용
- 예상 토큰: 2,000-6,000

### Deep (전체 로딩)
- 모든 관련 문서 + 스니펫
- 완전한 구현, 디버깅용
- 예상 토큰: 8,000-20,000

## 조합 로딩 규칙

### SaaS MVP 조합
```yaml
triggers: ["saas mvp", "SaaS MVP"]
skills:
  - core (standard)
  - auth (standard)
  - recipes-subscription (deep)
  - recipes-onboarding (standard)
```

### Real-time App 조합
```yaml
triggers: ["realtime app", "실시간 앱"]
skills:
  - hotwire (standard)
  - realtime (deep)
  - recipes-comments (standard)
```

## 캐싱 전략

```
CACHE_KEY = hash(skill_path + depth + version)

IF cache.has(CACHE_KEY):
  RETURN cache.get(CACHE_KEY)
ELSE:
  content = load_files(skill, depth)
  cache.set(CACHE_KEY, content, TTL=1hour)
  RETURN content
```

## 우선순위 규칙

1. **조합 우선**: 조합 트리거가 매칭되면 조합 로드
2. **중첩 스킬**: 특수 트리거는 중첩 스킬 직접 로드
3. **메인 스킬**: 일반 트리거는 메인 스킬 로드
4. **폴백**: 매칭 없으면 root 스킬 로드

## 오류 처리

| 상황 | 처리 |
|------|------|
| 트리거 매칭 없음 | root 스킬 shallow 로드 |
| 의존성 누락 | 경고 후 부분 로드 |
| 파일 없음 | 스킵 후 다음 파일 시도 |
| 순환 의존성 | 감지 후 중단 |

## 성능 메트릭

### 측정 항목
- 매칭 시간 (목표: <50ms)
- 로딩 시간 (목표: <200ms)
- 토큰 사용량 (목표: 필요 최소)
- 정확도 (목표: >90%)

### 최적화 기법
1. 트리거 인덱싱
2. 프리페칭 (자주 함께 사용되는 스킬)
3. 압축 캐싱
4. 점진적 로딩

## 예제 시나리오

### 시나리오 1: "터보 프레임 사용법"
```
1. 트리거 매칭: hotwire (score: 0.9)
2. 깊이 결정: shallow (개념 질문)
3. 로드: hotwire/SKILL.md
4. 예상 토큰: ~1,200
```

### 시나리오 2: "구독 결제 시스템 구현"
```
1. 트리거 매칭: recipes-subscription (score: 0.85)
2. 의존성 해결: auth, background
3. 깊이 결정: deep (완전 구현)
4. 로드:
   - recipes/saas/subscription/**/*.md
   - auth/SKILL.md (shallow)
   - background/SKILL.md (shallow)
5. 예상 토큰: ~12,000
```

### 시나리오 3: "SaaS MVP 빌드"
```
1. 조합 매칭: saas-mvp
2. 스킬 로드:
   - core (standard)
   - auth (standard)
   - recipes-subscription (deep)
   - recipes-onboarding (standard)
3. 예상 토큰: ~18,000
```

## 버전 관리

| 버전 | 변경 사항 |
|------|----------|
| 1.0.0 | 초기 프로토콜 정의 |

## 관련 파일

- `MANIFEST.json`: 스킬 레지스트리
- `*/SKILL.md`: 개별 스킬 프론트매터
