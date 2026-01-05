# MCP (Model Context Protocol) 사용자 가이드

## 개요

MCP(Model Context Protocol)는 Claude Code와 외부 도구/서비스를 연결하는 표준화된 프로토콜입니다. 각 MCP 서버는 특정 도메인에 특화되어 있으며, 조합하여 사용하면 강력한 워크플로우를 구축할 수 있습니다.

---

## 🗺️ MCP 서버 개요

| MCP 서버 | 목적 | 주요 사용 사례 |
|----------|------|----------------|
| **Context7** | 공식 문서 조회 | 프레임워크 패턴, API 사용법 |
| **Sequential** | 다단계 추론 | 복잡한 분석, 시스템 설계 |
| **Tavily** | 웹 검색 | 최신 정보, 리서치 |
| **Playwright** | 브라우저 자동화 | E2E 테스트, UI 검증 |
| **Magic** | UI 컴포넌트 생성 | 접근성 있는 현대적 UI |
| **Morphllm** | 패턴 기반 편집 | 대량 코드 변환 |
| **Serena** | 시맨틱 코드 이해 | 심볼 연산, 세션 관리 |

---

## 📚 상세 가이드

### 1. Context7 - 공식 문서 조회

**목적**: 라이브러리/프레임워크의 공식 문서와 패턴 가이드 제공

**언제 사용**:
- `import`, `require`, `from` 등 import 문 작성 시
- React, Vue, Next.js 등 프레임워크 관련 질문
- 버전별 구현 패턴 필요 시
- 공식 표준 준수가 필수인 경우

**플래그**: `--c7`, `--context7`

**예시**:
```
"React useEffect 구현" → Context7 ✅
"Auth0 인증 추가" → Context7 ✅
"이 함수 설명해줘" → Native Claude (외부 문서 불필요)
```

**조합 패턴**:
- Context7 (문서) → Sequential (구현 전략 분석)
- Context7 (패턴) → Magic (프레임워크 준수 컴포넌트 생성)

---

### 2. Sequential - 다단계 추론 엔진

**목적**: 복잡한 분석과 체계적인 문제 해결

**언제 사용**:
- 3개 이상의 상호 연결된 컴포넌트가 있는 문제
- 근본 원인 분석, 아키텍처 리뷰, 보안 평가
- 프론트엔드, 백엔드, 데이터베이스에 걸친 문제
- 가설 검증이 필요한 디버깅

**플래그**: `--think`, `--think-hard`, `--ultrathink`

**분석 깊이**:
| 플래그 | 토큰 | 사용 사례 |
|--------|------|-----------|
| `--think` | ~4K | 일반 분석 |
| `--think-hard` | ~10K | 아키텍처 분석 |
| `--ultrathink` | ~32K | 시스템 재설계, 레거시 현대화 |

**예시**:
```
"API가 왜 느려?" → Sequential ✅ (체계적 성능 분석)
"마이크로서비스 아키텍처 설계" → Sequential ✅
"이 타이포 수정" → Native Claude (단순 작업)
```

---

### 3. Tavily - 웹 검색 엔진

**목적**: 실시간 웹 검색 및 최신 정보 수집

**언제 사용**:
- Claude 학습 데이터 이후의 최신 정보 필요
- 시장 조사, 경쟁사 분석
- 팩트 체킹, 검증
- `/sc:research` 명령 실행 시

**설정**: `TAVILY_API_KEY` 환경 변수 필요

**검색 유형**:
```yaml
기본 검색: 일반 웹 검색
뉴스 검색: 시간 필터링된 최신 뉴스
학술 검색: 연구 논문, 학술 자료
도메인 필터: 특정 사이트만 검색
```

**예시**:
```
"TypeScript 5.0 새 기능" → Tavily ✅
"이번 주 OpenAI 업데이트" → Tavily ✅
"재귀 설명" → Native Claude (일반 개념)
```

**리서치 워크플로우**:
```
1. Tavily: 초기 검색
2. Sequential: 분석 및 갭 식별
3. Tavily: 후속 검색
4. Sequential: 결과 종합
5. Serena: 세션 저장
```

---

### 4. Playwright - 브라우저 자동화

**목적**: 실제 브라우저에서 E2E 테스트 및 UI 검증

**언제 사용**:
- 실제 렌더링이 필요한 테스트
- 로그인, 폼 제출 등 사용자 플로우 테스트
- 스크린샷 비교, 반응형 디자인 검증
- WCAG 접근성 테스트

**플래그**: `--play`, `--playwright`

**예시**:
```
"로그인 플로우 테스트" → Playwright ✅
"폼 유효성 검사 확인" → Playwright ✅
"접근성 검증" → Playwright ✅
"함수 로직 리뷰" → Native Claude (정적 분석)
```

**조합 패턴**:
- Sequential (테스트 전략) → Playwright (브라우저 실행)
- Magic (UI 생성) → Playwright (동작 검증)

---

### 5. Magic - UI 컴포넌트 생성

**목적**: 21st.dev 패턴 기반 현대적 UI 컴포넌트 생성

**언제 사용**:
- 버튼, 폼, 모달, 카드, 테이블 등 UI 컴포넌트
- 디자인 시스템 구현
- 반응형, 접근성 있는 컴포넌트 필요 시

**플래그**: `--magic`, `/ui`, `/21`

**예시**:
```
"로그인 폼 만들어줘" → Magic ✅
"반응형 네비게이션 바" → Magic ✅
"데이터 테이블 정렬 기능" → Magic ✅
"REST API 작성" → Native Claude (백엔드 로직)
```

**조합 패턴**:
- Magic (21st.dev 패턴) → Context7 (프레임워크 통합)
- Sequential (UI 요구사항 분석) → Magic (구조화된 컴포넌트)

---

### 6. Morphllm - 패턴 기반 편집

**목적**: 토큰 최적화된 대량 코드 변환

**언제 사용**:
- 여러 파일에 일관된 패턴 적용
- 프레임워크 업데이트, 스타일 가이드 적용
- 대량 텍스트 치환
- 토큰 효율성이 중요한 경우 (30-50% 절감)

**플래그**: `--morph`, `--morphllm`

**예시**:
```
"React 클래스 → 훅으로 변환" → Morphllm ✅
"ESLint 규칙 전체 적용" → Morphllm ✅
"console.log → logger로 변경" → Morphllm ✅
"getUserData 함수 리네임" → Serena (심볼 연산)
```

**조합 패턴**:
- Serena (시맨틱 분석) → Morphllm (정밀 편집)
- Sequential (편집 전략) → Morphllm (체계적 변경)

---

### 7. Serena - 시맨틱 코드 이해

**목적**: LSP 기반 코드 이해 및 세션 영속성

**언제 사용**:
- 심볼 리네임, 추출, 이동
- 프로젝트 전체 코드 탐색
- 다중 언어 프로젝트
- 세션 관리: `/sc:load`, `/sc:save`
- 대규모 코드베이스 (50+ 파일)

**플래그**: `--serena`

**예시**:
```
"getUserData 함수 모두 리네임" → Serena ✅
"이 클래스 참조 모두 찾기" → Serena ✅
"프로젝트 컨텍스트 로드" → Serena (/sc:load)
"세션 저장" → Serena (/sc:save)
```

**세션 라이프사이클**:
```
시작: /sc:load → 컨텍스트 복원
작업: 정기적 체크포인트 (30분 간격)
종료: /sc:save → 상태 영속화
```

---

## 🔀 MCP 선택 의사결정 트리

```
작업 유형?
│
├─ 문서/패턴 조회 → Context7
│
├─ 복잡한 분석
│  └─ 컴포넌트 3개 이상? → Sequential
│     └─ 단순 설명 → Native Claude
│
├─ 최신 정보 필요
│  └─ 학습 데이터 이후? → Tavily
│     └─ 일반 지식 → Native Claude
│
├─ 브라우저 테스트
│  └─ 실제 렌더링 필요? → Playwright
│     └─ 정적 분석 → Native Claude
│
├─ UI 컴포넌트
│  └─ 프론트엔드 UI? → Magic
│     └─ 백엔드 로직 → Native Claude
│
├─ 코드 편집
│  ├─ 패턴 기반 대량 변환 → Morphllm
│  └─ 심볼 연산/리네임 → Serena
│
└─ 세션 관리 → Serena
```

---

## 🔗 MCP 조합 워크플로우

### 1. 리서치 워크플로우
```
Tavily (검색) → Sequential (분석) → Tavily (추가 검색) → Serena (저장)
```

### 2. UI 개발 워크플로우
```
Context7 (프레임워크 패턴) → Magic (컴포넌트 생성) → Playwright (테스트)
```

### 3. 코드 리팩토링 워크플로우
```
Serena (시맨틱 분석) → Sequential (리팩토링 전략) → Morphllm (대량 변환)
```

### 4. 아키텍처 설계 워크플로우
```
Sequential (분석) → Context7 (패턴 참조) → Serena (문서화)
```

### 5. 프론트엔드 검증 워크플로우
```
Magic (UI 생성) → Playwright (E2E 테스트) → Sequential (결과 분석)
```

---

## ⚙️ 플래그 빠른 참조

| 플래그 | MCP 서버 | 용도 |
|--------|----------|------|
| `--c7`, `--context7` | Context7 | 공식 문서 조회 |
| `--seq`, `--sequential` | Sequential | 다단계 추론 |
| `--think` | Sequential | 일반 분석 (~4K) |
| `--think-hard` | Sequential | 깊은 분석 (~10K) |
| `--ultrathink` | Sequential | 최대 깊이 (~32K) |
| `--tavily` | Tavily | 웹 검색 |
| `--play`, `--playwright` | Playwright | 브라우저 자동화 |
| `--magic`, `/ui`, `/21` | Magic | UI 컴포넌트 |
| `--morph`, `--morphllm` | Morphllm | 패턴 기반 편집 |
| `--serena` | Serena | 시맨틱 이해 |
| `--all-mcp` | 모두 | 최대 복잡도 시나리오 |
| `--no-mcp` | 없음 | 네이티브만 사용 |

---

## 🚀 시작하기

### 1. MCP 서버 설정 확인
```bash
# 설정 파일 위치
~/.claude/settings.json
~/.claude/mcp.json  # MCP 서버 설정 (선택)
```

### 2. API 키 설정 (필요한 경우)
```bash
# Tavily 검색 사용 시
export TAVILY_API_KEY="your-api-key"
```

### 3. 플러그인 활성화 확인
```json
// ~/.claude/settings.json
{
  "enabledPlugins": {
    "context7@claude-plugins-official": true,
    "perplexity@perplexity-mcp-server": true
    // ...
  }
}
```

---

## 💡 베스트 프랙티스

1. **단일 MCP로 시작**: 필요에 따라 조합 추가
2. **적절한 깊이 선택**: 간단한 작업에 `--ultrathink` 사용 자제
3. **조합 활용**: 복잡한 작업은 MCP 조합으로 시너지 효과
4. **세션 관리**: 긴 작업은 `/sc:save`로 진행 상황 저장
5. **컨텍스트 고려**: 토큰 사용량이 많을 때 `--no-mcp` 고려

---

## 📖 관련 문서

- `~/.claude/MCP_Context7.md` - Context7 상세 가이드
- `~/.claude/MCP_Sequential.md` - Sequential 상세 가이드
- `~/.claude/MCP_Tavily.md` - Tavily 상세 가이드
- `~/.claude/MCP_Playwright.md` - Playwright 상세 가이드
- `~/.claude/MCP_Magic.md` - Magic 상세 가이드
- `~/.claude/MCP_Morphllm.md` - Morphllm 상세 가이드
- `~/.claude/MCP_Serena.md` - Serena 상세 가이드
