# Vue Analysis Phase Commands

각 분석 Phase별 실행 명령어입니다.

## Phase 1: 진입점 파악

```bash
# 프로젝트 메타 정보
cat package.json | head -50

# 빌드 설정 확인
ls -la vite.config.* vue.config.* nuxt.config.* 2>/dev/null

# 앱 초기화 흐름
cat src/main.ts 2>/dev/null || cat src/main.js
```

**수집 항목:**
- Vue 버전 (2.x / 3.x)
- 빌드 도구 (Vite / Webpack / Nuxt)
- 상태관리 (Vuex / Pinia / 없음)
- TypeScript 사용 여부
- UI 프레임워크

## Phase 2: 구조 분류

```bash
# 디렉토리 구조
find src -type d -maxdepth 3 | head -50

# Vue 파일 분포
find src -name "*.vue" | wc -l
find src -name "*.vue" -path "*/views/*" | wc -l
find src -name "*.vue" -path "*/components/*" | wc -l

# 라우트 구조
cat src/router/index.ts 2>/dev/null || cat src/router/index.js
```

## Phase 3: 모듈별 분석

### 컴포넌트 의존성

```bash
# 가장 많이 import되는 컴포넌트
grep -rh "import.*from.*components" src --include="*.vue" --include="*.ts" | \
  sed "s/.*from ['\"]//;s/['\"].*//" | sort | uniq -c | sort -rn | head -20

# 특정 컴포넌트의 사용처
grep -rl "ComponentName" src --include="*.vue"
```

### 스토어 구조

```bash
# Pinia stores
find src -name "*.ts" -path "*stores*"

# Vuex modules
find src -name "*.ts" -path "*store/modules*"
```

### API 계층

```bash
# API 파일 목록
find src -type f \( -path "*api*" -o -path "*services*" \) -name "*.ts"

# 엔드포인트 추출
grep -rh "axios\|fetch\|api\." src --include="*.ts" | head -30
```

## 대체 경로 탐색 순서

```
소스 코드: src/ → app/ → lib/ → client/ → .
라우터: src/router/ → src/routes/ → pages/
스토어: src/stores/ → src/store/ → src/state/
API: src/api/ → src/services/ → src/http/
```

## 에러 대응

| 상황 | 대응 |
|------|------|
| `src/` 없음 | `app/`, `lib/`, `client/` 확인 |
| Vue 파일 없음 | Nuxt/Quasar 메타 프레임워크 검토 |
| 라우터 없음 | 파일 기반 라우팅 (pages/) 확인 |
| TypeScript 없음 | `.js` 확장자로 대체 |
| 스토어 없음 | Composition API `provide/inject` 확인 |
