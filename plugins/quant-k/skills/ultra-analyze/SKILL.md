---
name: ultra-analyze
description: KRX-Quant 울트라 분석 모드. 모든 기능을 최대 역량으로 활용하여 심층 분석 수행. "울트라 분석", "ultra", "딥 분석", "전체 분석" 등의 요청에 자동 활성화.
argument-hint: <종목명|종목코드> [저장경로]
allowed-tools:
  - Read
  - Write
  - Glob
  - Grep
  - Bash
  - Task
  - WebFetch
---

# KRX-Quant Ultra 분석 모드

---

## 🚨 최우선 실행 지침

### ❌ 금지 사항

- Bash로 직접 모든 분석을 수행하지 마세요
- 팩터 분석/유사 종목 검색/웹 스크래핑을 직접 수행하지 마세요

### ✅ 필수 실행 패턴

| Phase | 실행 방법 | 도구 |
|-------|----------|------|
| Phase 1 | `collect_all` 명령 실행 | Bash |
| **Phase 2-4** | **에이전트 3개 동시 실행** | **Task (필수!)** |
| Phase 5-6 | 기술분석 + 리포트 생성 | Write |

### 🎯 Phase 2-4: 에이전트 병렬 실행

**Phase 1 완료 직후, 아래 3개의 Task를 하나의 응답에서 동시 실행:**

| 에이전트 | subagent_type | 출력 파일 | prompt 요약 |
|----------|---------------|-----------|-------------|
| 웹 스크래퍼 | `quant-k:web-scraper` | `analysis/web-data.md` | 네이버 금융에서 투자의견, 목표가, 뉴스 수집 |
| 퀀트 분석가 | `quant-k:quant-analyst` | `analysis/valuation.md` | PER/PBR 밸류에이션, 모멘텀, 적정가, 스코어카드 |
| 종목 스크리너 | `quant-k:stock-screener` | `analysis/similar-stocks.md` | 유사 밸류에이션 종목 20개 검색 |

⚠️ **파일 충돌 방지**: 각 에이전트는 **자신의 전용 파일에만** 작성. **README.md는 Phase 6에서만 생성**.

### ⚠️ 스킬 vs 에이전트

| ❌ 스킬 (Task 불가) | ✅ 에이전트 (Task 사용) |
|-------------------|----------------------|
| `quant-k:factor-analyze` | `quant-k:quant-analyst` |
| `quant-k:stock-screen` | `quant-k:stock-screener` |
| `quant-k:browser-scraper` | `quant-k:web-scraper` |

---

## Phase 1: 데이터 수집

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/krx_utils.py" collect_all "종목코드" --days 365
```

**pykrx 레퍼런스가 필요하면:** `_shared/pykrx-reference.md` 참조

---

## Phase 5: 기술분석

- 이동평균선 (5/10/20/60/120/240일)
- RSI, MACD, 볼린저밴드
- 지지/저항선 분석

---

## Phase 6: 리포트 구조

```
{저장경로}/{종목명}_ultra_{날짜}/
├── README.md          # 메인 리포트 (Phase 6에서만 생성)
├── data/ohlcv.csv     # 가격 데이터
└── analysis/
    ├── web-data.md    # 웹 스크래퍼 출력
    ├── valuation.md   # 퀀트 분석가 출력
    ├── similar-stocks.md  # 스크리너 출력
    └── technical.md   # 기술분석
```

### ⚠️ README.md 작성 전 필수 체크

```
1. Glob으로 README.md 존재 여부 확인
2. 파일이 존재하면 → Read로 먼저 읽기
3. 그 후 Write로 새 내용 작성
```

**리포트 섹션:** Executive Summary → 스코어카드 → 기업개요 → 주가분석 → 기술분석 → 밸류에이션 → 유사종목 → 투자전략 → 결론

---

## ⚠️ 출력 경로 규칙

- 모든 파일은 **저장경로 아래에만** 생성
- 미지정 시 `{종목명}_ultra_{날짜}/` 디렉토리 생성
- **프로젝트 루트에 직접 파일 생성 금지**

---

## 사용법

```bash
/quant-k:ultra-analyze 동운아나텍
/quant-k:ultra-analyze 094170 report/
```

```
"삼성전자 울트라 분석해줘"
"SK하이닉스 심층 분석 리포트"
```

---

## ✅ 완료 체크리스트

- [ ] Phase 1: `collect_all` 완료
- [ ] Phase 2-4: 에이전트 3개 Task로 실행
- [ ] Phase 5: 기술분석 수행
- [ ] Phase 6: README.md 리포트 생성
