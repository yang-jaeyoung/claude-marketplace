# Vue 2 → Vue 3 마이그레이션 체크리스트

## 사전 분석

### 현재 상태 파악
```bash
# Vue 버전 확인
grep '"vue"' package.json

# 호환성 문제 자동 스캔
npx vue-migration-helper
```

---

## Breaking Changes 체크리스트

### 1. Global API 변경

| Vue 2 | Vue 3 | 상태 |
|-------|-------|------|
| `new Vue()` | `createApp()` | ☐ |
| `Vue.component()` | `app.component()` | ☐ |
| `Vue.directive()` | `app.directive()` | ☐ |
| `Vue.mixin()` | `app.mixin()` | ☐ |
| `Vue.use()` | `app.use()` | ☐ |
| `Vue.prototype.$x` | `app.config.globalProperties.$x` | ☐ |

### 2. Template 변경

| 항목 | 변경사항 | 상태 |
|------|----------|------|
| `v-model` | `.sync` 제거, `v-model:propName` 사용 | ☐ |
| `v-if` + `v-for` | 같은 요소에서 `v-if` 우선순위 변경 | ☐ |
| `key` | `<template v-for>`에 key 필수 | ☐ |
| Functional components | `functional` 속성 제거 | ☐ |

### 3. Composition API 도입

```vue
<!-- Vue 2 (Options API) -->
<script>
export default {
  data() {
    return { count: 0 }
  },
  computed: {
    doubled() { return this.count * 2 }
  },
  methods: {
    increment() { this.count++ }
  }
}
</script>

<!-- Vue 3 (Composition API) -->
<script setup>
import { ref, computed } from 'vue'

const count = ref(0)
const doubled = computed(() => count.value * 2)
const increment = () => count.value++
</script>
```

### 4. Lifecycle Hooks 변경

| Vue 2 | Vue 3 (Options) | Vue 3 (Composition) |
|-------|-----------------|---------------------|
| `beforeCreate` | `beforeCreate` | `setup()` |
| `created` | `created` | `setup()` |
| `beforeMount` | `beforeMount` | `onBeforeMount` |
| `mounted` | `mounted` | `onMounted` |
| `beforeUpdate` | `beforeUpdate` | `onBeforeUpdate` |
| `updated` | `updated` | `onUpdated` |
| `beforeDestroy` | `beforeUnmount` | `onBeforeUnmount` |
| `destroyed` | `unmounted` | `onUnmounted` |

### 5. Vuex → Pinia 마이그레이션

```javascript
// Vuex
const store = new Vuex.Store({
  state: { count: 0 },
  mutations: {
    increment(state) { state.count++ }
  },
  actions: {
    asyncIncrement({ commit }) {
      setTimeout(() => commit('increment'), 1000)
    }
  }
})

// Pinia
export const useCounterStore = defineStore('counter', {
  state: () => ({ count: 0 }),
  actions: {
    increment() { this.count++ },
    async asyncIncrement() {
      await new Promise(r => setTimeout(r, 1000))
      this.count++
    }
  }
})
```

---

## 마이그레이션 단계

### Phase 1: 준비 (1-2주)
- [ ] Vue 2.7로 업그레이드 (Composition API 백포트)
- [ ] `@vue/compat` 모드 테스트
- [ ] 호환성 경고 목록 작성

### Phase 2: 점진적 전환 (2-4주)
- [ ] 새 컴포넌트는 Composition API로 작성
- [ ] 핵심 컴포넌트부터 마이그레이션
- [ ] 테스트 커버리지 확보

### Phase 3: 완전 전환 (1-2주)
- [ ] `@vue/compat` 제거
- [ ] Vue 3 전용 기능 활용
- [ ] 성능 최적화

---

## 의존성 호환성 확인

### 주요 라이브러리

| 라이브러리 | Vue 2 | Vue 3 | 비고 |
|-----------|-------|-------|------|
| Vuex | 3.x | 4.x | Pinia 권장 |
| Vue Router | 3.x | 4.x | 문법 변경 |
| Vuetify | 2.x | 3.x | 대규모 변경 |
| Element UI | 2.x | Element Plus | 별도 패키지 |
| Vuelidate | 0.x | @vuelidate/core | 완전 재작성 |

### 호환성 확인 명령어
```bash
# 의존성 호환성 체크
npx vue-codemod check
```

---

## 자동화 도구

### vue-codemod
```bash
# 자동 변환
npx vue-codemod <file-path> -t <transformation>

# 주요 변환
npx vue-codemod src -t new-global-api
npx vue-codemod src -t vue-router-v4
npx vue-codemod src -t remove-trivial-root
```

### gogocode-plugin-vue
```bash
npm install gogocode-plugin-vue -g
gogocode -s ./src -t gogocode-plugin-vue -o ./src-vue3
```

---

## 마이그레이션 후 검증

### 기능 테스트
- [ ] 라우팅 정상 동작
- [ ] 상태 관리 정상 동작
- [ ] 폼 유효성 검사
- [ ] API 통신
- [ ] 인증/권한

### 성능 테스트
- [ ] 번들 크기 비교
- [ ] 초기 로딩 시간
- [ ] 메모리 사용량

### 브라우저 호환성
- [ ] Chrome
- [ ] Firefox
- [ ] Safari
- [ ] Edge