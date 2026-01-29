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

### pykrx DataFrame 컬럼 레퍼런스

pykrx가 반환하는 DataFrame의 **실제 컬럼명**입니다. 인라인 Python 코드에서 반드시 이 컬럼명을 사용하세요.

**OHLCV (get_market_ohlcv):**
```python
['시가', '고가', '저가', '종가', '거래량', '등락률']
# 영문 없음! '등락률'은 전일대비 변동률 (%)
```

**Fundamental (get_market_fundamental):**
```python
['BPS', 'PER', 'PBR', 'EPS', 'DIV', 'DPS']
# 영문 대문자만 사용
```

**Market Cap (get_market_cap):**
```python
['종가', '시가총액', '거래량', '거래대금', '상장주식수']
# '시가총액'은 원 단위 (억원 아님)
```

**⚠️ 주의:** `ret_3m`, `momentum_3m`, `return_1m` 같은 컬럼은 **존재하지 않습니다**. 모멘텀은 직접 계산해야 합니다:

```python
# 3개월 수익률 계산 예시
ohlcv = stock.get_market_ohlcv(start_date, end_date, ticker)
price_now = int(ohlcv['종가'].iloc[-1])
price_3m = int(ohlcv['종가'].iloc[0])
momentum_3m = round((price_now - price_3m) / price_3m * 100, 2)
```

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

### 병렬 데이터 수집 (권장)
```bash
# Phase 1 데이터를 병렬로 수집 (ohlcv + fundamental + market_cap 동시 실행)
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/krx_utils.py" collect_all "종목코드" --days 365
```

이 명령어는 ohlcv, fundamental, market_cap을 ThreadPoolExecutor로 동시에 수집하여 3배 빠릅니다.

## Ultra 분석 워크플로우

### Phase 1: 데이터 수집 (Maximum Coverage)

**권장: 병렬 수집**
```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/krx_utils.py" collect_all "종목코드" --days 365
```

위 명령 하나로 ohlcv, fundamental, market_cap을 병렬 수집합니다.

**개별 수집 (필요 시)**
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

## 주의: JSON 직렬화

분석 결과를 JSON으로 저장할 때 numpy/pandas 타입은 직렬화 오류를 발생시킵니다.

**안전한 JSON 저장 패턴:**
```python
import json
import numpy as np

def safe_json_value(v):
    """numpy 타입을 Python 네이티브 타입으로 변환"""
    if isinstance(v, (np.integer, np.int64)):
        return int(v)
    elif isinstance(v, (np.floating, np.float64)):
        return float(v)
    elif isinstance(v, np.ndarray):
        return v.tolist()
    elif pd.isna(v):
        return None
    return v

def safe_dict(d):
    """딕셔너리의 모든 값을 안전하게 변환"""
    return {k: safe_json_value(v) for k, v in d.items()}

# 사용 예시
result = safe_dict({"per": df['PER'].iloc[0], "price": ohlcv['종가'].iloc[-1]})
json.dump(result, f, ensure_ascii=False)
```

**또는 간단히:**
```python
# 모든 숫자를 float()로 변환
result = {
    "per": float(per) if per else None,
    "price": int(price),
}
```

## WebFetch 차단 사이트 처리

일부 금융 사이트(예: `finance.naver.com`, `dart.fss.or.kr`)는 WebFetch로 접근이 차단됩니다.

**차단된 사이트에서 데이터가 필요한 경우:**

browser-scraper 스킬을 사용하세요:

```bash
# 네이버 금융 시가총액 순위
/quant-k:browser-scraper https://finance.naver.com/sise/sise_market_sum.naver "시가총액 상위 100개"

# 네이버 금융 종목 상세
/quant-k:browser-scraper https://finance.naver.com/item/main.naver?code={종목코드} "기업 정보"

# DART 공시 검색
/quant-k:browser-scraper AUTO: https://dart.fss.or.kr "최근 공시"

# KRX 데이터 포털 (API 자동 탐지)
/quant-k:browser-scraper https://data.krx.co.kr --discover-api "종목별 시세"
```

**browser-scraper vs WebFetch:**

| 도구 | 장점 | 단점 | 사용 시나리오 |
|------|------|------|--------------|
| WebFetch | 빠름, 간단 | 일부 사이트 차단 | 공개 API, 허용된 사이트 |
| browser-scraper | 차단 우회, JS 렌더링 | 느림, 복잡 | 네이버, DART, KRX 등 |

**권장 워크플로우:**
1. 먼저 pykrx로 기본 데이터 수집 (`collect_all`)
2. 추가 정보 필요 시 browser-scraper로 네이버/DART 스크래핑
3. 결과 통합하여 리포트 생성

## 에러 처리

| 상황 | 처리 |
|------|------|
| pykrx 미설치 | `/quant-k:setup` 안내 |
| 데이터 부족 | 가능한 데이터만으로 부분 리포트 |
| 1년 데이터 없음 | 가용 기간으로 축소 |
| 저장 실패 | 콘솔에 전체 출력 |
