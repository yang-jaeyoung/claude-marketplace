---
name: browser-scraper
description: Intelligent web scraping orchestration for Korean financial data with automatic strategy selection, pagination handling, and session persistence
allowed-tools: Read, Bash, Grep, WebFetch
context: fork
---

# Browser Scraper Skill

한국 금융 웹사이트에서 데이터를 추출하는 지능형 스크래핑 오케스트레이터입니다.

---

## 🚨 핵심 실행 지침

### 6-Phase 프로토콜

```
RECONNAISSANCE → STRATEGY → EXTRACTION → PAGINATION → EXPORT → VERIFICATION
     ↓              ↓            ↓            ↓          ↓           ↓
  explore      architect-low  executor    executor    writer    architect-low
  (haiku)        (haiku)     (haiku)     (sonnet)   (haiku)     (haiku)
```

### 필수 워크플로우

**Phase 1-2는 직접 실행, Phase 3-6는 Task tool로 에이전트 실행:**

| Phase | 작업 | 도구 |
|-------|-----|------|
| 1. Reconnaissance | 페이지 구조 분석 | `browser_snapshot` |
| 2. Strategy | 전략 선택 | 직접 판단 |
| 3. Extraction | 데이터 추출 | Task → `executor` |
| 4. Pagination | 페이지 반복 | Task → `executor` |
| 5. Export | JSON/CSV 저장 | Task → `writer` |
| 6. Verification | 품질 검증 | Task → `architect-low` |

---

## 사용법

```bash
# 기본 (수동 모드)
/browser-scraper https://finance.naver.com/sise/sise_market_sum.naver "시가총액 상위 100개"

# 자동 모드 (다중 페이지)
/browser-scraper AUTO: https://dart.fss.or.kr "최근 공시 목록"

# API 탐지 모드
/browser-scraper https://data.krx.co.kr --discover-api "종목별 시세"

# 세션 관리
/browser-scraper status                    # 활성 세션 확인
/browser-scraper resume scraper-20260129   # 중단된 세션 재개
/browser-scraper cancel scraper-20260129   # 세션 취소
```

---

## 전략 선택 매트릭스

| 조건 | 전략 | 참조 문서 |
|------|------|----------|
| 정적 HTML 테이블 | DOM Direct | `./strategies/static-scraping.md` |
| XHR/Fetch API 감지 | API Discovery | `./strategies/api-discovery.md` |
| 무한 스크롤 | Scroll-and-Extract | `./strategies/dynamic-scraping.md` |
| 페이지 버튼 | Click-and-Wait | `./strategies/pagination.md` |

**⚠️ 중요:** 전략 파일은 **해당 전략 사용 시에만** 읽으세요. 모든 파일을 미리 로드하지 마세요!

```
예: DOM Direct 전략 사용 시
→ Read("./strategies/static-scraping.md") 실행
→ 다른 전략 파일은 읽지 않음
```

---

## MCP 도구 선택

| 도구 | 용도 | 사용 시점 |
|------|------|----------|
| `browser_snapshot` | 페이지 구조 분석 | Phase 1 |
| `browser_evaluate` | DOM 데이터 추출 | Phase 3 (DOM Direct) |
| `browser_network_requests` | API 탐지 | Phase 1, 3 (API Discovery) |
| `browser_click` | 페이지네이션 | Phase 4 |
| `browser_wait_for` | 동적 로드 대기 | Phase 3, 4 |

---

## 한국 금융 사이트 가이드

### Naver Finance

- **URL**: `https://finance.naver.com/sise/*`
- **전략**: DOM Direct
- **페이지네이션**: `.pgRR` 버튼 클릭
- **셀렉터**: `table.type_2 tr`

### DART

- **URL**: `https://dart.fss.or.kr/*`
- **전략**: Hybrid (API + DOM)
- **페이지네이션**: 페이지 번호 클릭
- **셀렉터**: `table.tb tr`

### KRX Data Portal

- **URL**: `https://data.krx.co.kr/*`
- **전략**: API Discovery (권장)
- **API**: `POST /comm/bldAttendant/getJsonData.cmd`

---

## 세션 디렉토리 구조

```
.omc/quant-k/scraper/{session-id}/
├── metadata.json      # 세션 메타데이터
├── state.json         # 현재 상태 (재개용)
├── data-page-*.json   # 페이지별 데이터
├── combined.json      # 통합 데이터
├── export.csv         # CSV 내보내기
└── export.md          # Markdown 테이블
```

---

## AUTO 모드 설정

```javascript
const AUTO_CONFIG = {
  maxIterations: 50,        // 최대 페이지 수
  maxRecords: 10000,        // 최대 레코드 수
  delayBetweenPages: 1500,  // 페이지 간 딜레이 (ms)
  maxRetries: 3,            // 페이지당 재시도 횟수
  timeout: 300000           // 세션 타임아웃 (5분)
};
```

**종료 조건:**
- `PROMISE:SCRAPER_COMPLETE`: 페이지네이션 완료 또는 최대 도달
- `PROMISE:SCRAPER_BLOCKED`: CAPTCHA/IP 차단 감지

---

## 에러 처리

| 에러 | 복구 방법 |
|------|----------|
| CAPTCHA 감지 | 수동 해결 후 `/browser-scraper resume` |
| Rate Limit (429) | 60초 대기, 3회 재시도 |
| 셀렉터 없음 | 대체 전략으로 폴백 |
| 타임아웃 | 부분 결과 저장 후 재개 가능 |

---

## 윤리 가이드라인

- `robots.txt` 준수
- 기본 딜레이: 1.5초/요청
- 공개 데이터만 수집
- 출처 및 시간 기록
