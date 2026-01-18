# Vue 프로젝트 분석 패턴

## 아키텍처 패턴별 분석 전략

### 1. Pages-based (Nuxt 스타일)

**특징:**
- `pages/` 폴더의 파일 구조가 곧 라우트
- 파일명이 URL 경로가 됨
- `_id.vue` 같은 동적 라우트

**분석 순서:**
```
1. pages/ 폴더 구조 파악 → 전체 기능 목록
2. layouts/ 확인 → 공통 레이아웃
3. middleware/ 확인 → 인증/권한 로직
4. plugins/ 확인 → 전역 설정
5. 페이지별 수직 분석
```

**핵심 파일:**
- `nuxt.config.js` / `nuxt.config.ts`
- `pages/index.vue`
- `layouts/default.vue`

---

### 2. Views/Components (Classic Vue)

**특징:**
- `views/` = 페이지 컴포넌트 (라우터 연결)
- `components/` = 재사용 컴포넌트
- `router/index.js`로 라우팅 정의

**분석 순서:**
```
1. router/index.js → 기능 목록 추출
2. views/ 폴더 → 페이지별 역할 파악
3. components/ → 공통 컴포넌트 분류
4. store/ → 상태 관리 구조
5. 핵심 페이지 수직 분석
```

**핵심 파일:**
- `src/router/index.ts`
- `src/store/index.ts`
- `src/App.vue`

---

### 3. Feature-based (Domain-driven)

**특징:**
- `features/` 또는 `modules/` 폴더
- 각 기능이 자체 components, store, api 보유
- 높은 응집도, 낮은 결합도

**분석 순서:**
```
1. features/ 목록 → 도메인 파악
2. 각 feature 내부 구조 확인
3. shared/ 또는 common/ → 공통 모듈
4. feature 간 의존성 분석
5. 핵심 feature 상세 분석
```

**폴더 구조 예시:**
```
src/
├── features/
│   ├── auth/
│   │   ├── components/
│   │   ├── store/
│   │   ├── api/
│   │   └── index.ts
│   ├── dashboard/
│   └── settings/
└── shared/
```

---

### 4. Atomic Design

**특징:**
- `atoms/` - 버튼, 입력 등 최소 단위
- `molecules/` - atom 조합
- `organisms/` - 복잡한 UI 섹션
- `templates/` - 페이지 레이아웃
- `pages/` - 실제 페이지

**분석 순서:**
```
1. atoms/ → 기본 UI 요소 파악
2. molecules/ → 조합 패턴
3. organisms/ → 비즈니스 로직 포함 여부
4. templates/ → 레이아웃 패턴
5. pages/ → 데이터 연결 방식
```

---

## 컴포넌트 분석 체크리스트

### Props 분석
```bash
# 컴포넌트의 props 추출
grep -A 20 "defineProps\|props:" src/components/MyComponent.vue
```

### Emits 분석
```bash
# 이벤트 emit 패턴
grep -E "emit\(|defineEmits" src/components/MyComponent.vue
```

### Composables 사용
```bash
# 사용 중인 composable 목록
grep -rh "use[A-Z]" src --include="*.vue" | sort | uniq
```

---

## 상태관리 분석

### Pinia 스토어 분석

```bash
# 스토어 목록
find src/stores -name "*.ts" -exec basename {} \;

# 스토어별 state 파악
grep -A 10 "state:" src/stores/*.ts

# actions 목록
grep -E "async.*\(|function.*\(" src/stores/*.ts
```

### Vuex 모듈 분석

```bash
# 모듈 목록
ls src/store/modules/

# mutations 목록
grep -E "^\s+\[.*\]|^\s+[A-Z_]+\(" src/store/modules/*.ts

# actions 목록
grep -E "async.*\{|\.dispatch\(" src/store/modules/*.ts
```

---

## API 계층 분석

### Axios 인스턴스 설정
```bash
# 베이스 URL, 인터셉터 확인
cat src/api/index.ts 2>/dev/null || cat src/services/http.ts
```

### 엔드포인트 목록화
```bash
# 모든 API 엔드포인트 추출
grep -rh "get\|post\|put\|delete\|patch" src/api --include="*.ts" | \
  grep -oE "['\"]\/[^'\"]+['\"]" | sort | uniq
```

---

## 성능 분석 포인트

### 번들 크기 분석
```bash
# Vite
npx vite-bundle-analyzer

# Webpack
npx webpack-bundle-analyzer dist/stats.json
```

### 컴포넌트 크기 분석
```bash
# 큰 컴포넌트 찾기 (500줄 이상)
find src -name "*.vue" -exec wc -l {} \; | sort -rn | head -20
```

### 의존성 무게
```bash
# 무거운 의존성 확인
npx depcheck
npx cost-of-modules
```

---

## 코드 품질 지표

### TypeScript 커버리지
```bash
npx type-coverage
```

### 테스트 커버리지
```bash
# Vitest
npx vitest --coverage

# Jest
npx jest --coverage
```

### 린트 이슈
```bash
npx eslint src --ext .vue,.ts,.js --format compact | wc -l
```

---

## 빠른 참조: 자주 쓰는 명령어

| 목적 | 명령어 |
|------|--------|
| Vue 파일 수 | `find src -name "*.vue" \| wc -l` |
| 가장 큰 파일 | `find src -name "*.vue" -exec wc -l {} \; \| sort -rn \| head -10` |
| import 분석 | `grep -rh "import.*from" src \| sort \| uniq -c \| sort -rn \| head -20` |
| 미사용 export | `npx ts-prune` |
| 순환 의존성 | `npx madge --circular src` |
| 의존성 그래프 | `npx madge --image deps.svg src` |