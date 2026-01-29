---
description: KRX-Quant Ultra 분석 모드. 모든 기능을 최대 역량으로 활용한 심층 분석.
argument-hint: <종목명|종목코드> [저장경로]
allowed-tools:
  - Read
  - Write
  - Glob
  - Bash
---

# KRX-Quant Ultra 분석 모드

모든 quant-k 기능을 최대 역량으로 활용하여 심층 종합분석을 수행합니다.

## 자동 활성화 키워드

- `울트라`, `ultra`
- `딥 분석`, `deep`
- `전체 분석`, `풀 분석`, `full`
- `심층 분석`, `최대`, `max`

## 실행 순서

### Phase 1: 데이터 수집 (Maximum)
```
krx_collect(dataType: "tickers", market: "KOSPI")
krx_collect(dataType: "tickers", market: "KOSDAQ")
krx_collect(dataType: "ohlcv", ticker: "{코드}", startDate: "3년전", endDate: "오늘")
krx_collect(dataType: "fundamental", ticker: "{코드}")
krx_collect(dataType: "marketcap", market: "{시장}")
```

### Phase 2: 전체 팩터 분석 (15 Factors)
```
factor_analyze(
  ticker: "{코드}",
  factors: ["PER", "PBR", "PSR", "PCR", "EV_EBITDA",
            "MOM_1M", "MOM_3M", "MOM_6M", "MOM_12M",
            "ROE", "ROA", "GP_MARGIN", "OP_MARGIN",
            "SIZE", "VOL_20D"]
)

factor_analyze(factors: ["PER"], market: "{시장}", topN: 100)
factor_analyze(factors: ["MOM_3M"], market: "{시장}", topN: 100)
factor_analyze(factors: ["ROE"], market: "{시장}", topN: 100)

factor_analyze(
  factors: ["PER", "MOM_3M", "ROE"],
  weights: {"PER": 0.4, "MOM_3M": 0.3, "ROE": 0.3},
  market: "{시장}",
  topN: 50
)
```

### Phase 3: 확장 스크리닝 (30+ 종목)
```
stock_screen(
  conditions: ["시총>{시총*0.3}", "시총<{시총*3}", "PER>{PER*0.5}", "PER<{PER*2}"],
  market: "ALL",
  limit: 30
)

stock_screen(
  conditions: ["PER<15", "ROE>10", "MOM_3M>0"],
  market: "ALL",
  limit: 30
)
```

### Phase 4: 웹 스크래핑 (External)
```
browser_scrape(url: "네이버금융 종목페이지", action: "extract_table")
browser_scrape(url: "네이버금융 재무제표", action: "extract_table")
browser_scrape(url: "DART 공시목록", action: "extract_list")
```

### Phase 5: 고급 분석
- 이동평균선 (5/10/20/60/120/240일)
- RSI, MACD
- 밸류에이션 적정가 (PER/PBR/PSR 기준)
- 백테스트 시뮬레이션

### Phase 6: Ultra 리포트 생성
디렉토리 구조로 출력:
```
{종목명}_ultra_{날짜}/
├── README.md           # 메인 리포트
├── executive_summary.md
├── data/               # 원시 데이터
├── analysis/           # 분석 결과
├── screening/          # 스크리닝 결과
└── external/           # 외부 데이터
```

## 사용 예시

```bash
# 기본 사용
/ultra-analyze 동운아나텍
/ultra-analyze 094170

# 저장 경로 지정
/ultra-analyze 동운아나텍 report/
/ultra-analyze 삼성전자 --output ./analysis/

# 자연어 요청
"동운아나텍 울트라 분석해줘"
"삼성전자 ultra 모드로 분석해서 report/에 저장"
"094170 딥 분석 실행"
```

## vs 일반 분석

| 항목 | stock-report | ultra-analyze |
|------|--------------|---------------|
| 가격 데이터 | 1년 | 3년 |
| 팩터 | 6개 | 15개 전체 |
| 유사 종목 | 10개 | 30개+ |
| 웹 스크래핑 | 없음 | 포함 |
| 리포트 | 단일 파일 | 디렉토리 구조 |
| 실행 시간 | 30초-1분 | 3-5분 |
