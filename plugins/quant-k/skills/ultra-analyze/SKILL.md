---
name: ultra-analyze
description: KRX-Quant 울트라 분석 모드. 모든 기능을 최대 역량으로 활용하여 심층 분석 수행. "울트라 분석", "ultra", "딥 분석", "전체 분석" 등의 요청에 자동 활성화.
argument-hint: <종목명|종목코드> [저장경로]
---

# KRX-Quant Ultra 분석 모드

모든 quant-k 기능을 최대 역량으로 활용하여 심층 종합분석을 수행합니다.

## 사전 요구사항

Python과 pykrx가 필요합니다. 처음 사용 시 `/quant-k:setup`을 실행하세요.

## 자동 활성화 패턴

다음 키워드가 포함된 요청에 자동 활성화됩니다:

- `울트라`, `ultra`
- `딥 분석`, `deep analysis`
- `전체 분석`, `풀 분석`
- `심층 분석`, `최대 분석`

**예시:**
```
"동운아나텍 울트라 분석해줘"
"삼성전자 ultra 모드로 분석"
"094170 딥 분석해서 report/에 저장"
```

## Ultra 모드 vs 일반 모드

| 항목 | 일반 모드 | Ultra 모드 |
|------|----------|-----------|
| 가격 데이터 | 6개월 | 1년 |
| 이동평균선 | 20/60일 | 5/10/20/60/120/240일 |
| 기술적 지표 | 기본 | RSI, MACD, 볼린저밴드 |
| 유사 종목 | 5개 | 20개 |
| 리포트 길이 | 요약 | 상세 (10+ 섹션) |

## 데이터 수집 명령어

### 기본 수집
```bash
# 종목 확인
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/krx_utils.py" search "종목명"
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/krx_utils.py" ticker_info "종목코드"

# 1년 가격 데이터
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/krx_utils.py" ohlcv "종목코드" --days 365

# 펀더멘털
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/krx_utils.py" fundamental "종목코드"

# 시가총액 및 순위
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/krx_utils.py" market_cap "종목코드"

# 시장 전체 종목 (비교용)
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/krx_utils.py" market_tickers KOSPI
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/krx_utils.py" market_tickers KOSDAQ
```

## Ultra 분석 워크플로우

### Phase 1: 데이터 수집 (Maximum Coverage)

1. **종목 확인**: search 또는 ticker_info로 종목 식별
2. **1년 OHLCV**: ohlcv --days 365
3. **펀더멘털**: fundamental
4. **시가총액**: market_cap

### Phase 2: 기술적 분석 (계산)

수집된 OHLCV 데이터로 다음을 계산:

```
이동평균선: 5/10/20/60/120/240일
볼린저밴드: 20일 기준, 2σ
RSI: 14일
MACD: 12/26/9
거래량 분석: 20일 평균 대비
```

### Phase 3: 밸류에이션 분석

```
PER 분석: 현재 vs 역사적 평균
PBR 분석: 현재 vs 섹터 평균
적정가 산출: PER/PBR 기반
```

### Phase 4: 유사 종목 검색

동일 시장에서 유사한 밸류에이션을 가진 종목 20개 식별

### Phase 5: Ultra 리포트 생성

## 리포트 구조

```markdown
# {종목명} ({종목코드}) Ultra 분석 리포트

> 생성일: {날짜} | 분석 모드: ULTRA

---

## Executive Summary
{핵심 요약 3-5문장}

## 투자 스코어카드
| 항목 | 점수 | 등급 |
|------|------|------|
| 밸류에이션 | {1-10} | {A-F} |
| 모멘텀 | {1-10} | {A-F} |
| 안정성 | {1-10} | {A-F} |
| **종합** | **{1-10}** | **{A-F}** |

---

## Part 1: 기업 개요
- 종목명, 종목코드, 시장
- 시가총액 및 순위

## Part 2: 주가 분석 (1년)
- 52주 고가/저가
- 수익률 분석 (1M/3M/6M/12M)
- 변동성 분석

## Part 3: 기술적 분석
- 이동평균선 분석 (6개)
- 볼린저밴드
- RSI, MACD
- 지지/저항선

## Part 4: 밸류에이션 분석
- PER/PBR/EPS/BPS 상세
- 적정가 산출

## Part 5: 유사 종목 비교
- 시총 유사 종목
- 밸류에이션 유사 종목

## Part 6: 투자 전략
- 매수 타이밍 분석
- 목표가/손절가
- 리스크 요인

## Part 7: 결론
- 강점/약점 요약
- 최종 투자의견

---

> 본 리포트는 quant-k Ultra 모드에 의해 자동 생성되었습니다.
```

## 출력 파일 구조

Ultra 모드는 디렉토리 구조로 출력:

```
{저장경로}/{종목명}_ultra_{날짜}/
├── README.md                    # 메인 리포트
├── data/
│   └── ohlcv.csv               # 가격 데이터
└── analysis/
    ├── technical.md            # 기술적 분석
    └── valuation.md            # 밸류에이션 분석
```

## 사용법

### 명령어
```bash
/quant-k:ultra-analyze 동운아나텍
/quant-k:ultra-analyze 094170 report/
```

### 자연어
```
"동운아나텍 울트라 분석해줘"
"삼성전자 ultra 모드로 전체 분석"
"SK하이닉스 심층 분석 리포트 만들어줘"
```

## 에러 처리

| 상황 | 처리 |
|------|------|
| pykrx 미설치 | `/quant-k:setup` 안내 |
| 데이터 부족 | 가능한 데이터만으로 부분 리포트 |
| 1년 데이터 없음 | 가용 기간으로 축소 |
| 저장 실패 | 콘솔에 전체 출력 |
