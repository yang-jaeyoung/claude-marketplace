---
name: stock-screen
description: 조건 기반 종목 스크리닝
argument-hint: <conditions> [--market KOSPI|KOSDAQ]
---

# 종목 스크리닝 스킬

조건을 지정하여 종목을 필터링합니다.

## 사전 요구사항

Python과 pykrx가 필요합니다. 처음 사용 시 `/quant-k:setup`을 실행하세요.

## 스크리닝 워크플로우

### 1단계: 시장 전체 종목 조회
```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/krx_utils.py" market_tickers KOSPI
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/krx_utils.py" market_tickers KOSDAQ
```

### 병렬 스크리닝 (권장)
```bash
# 시장 전체 스크리닝 (펀더멘털 + 3개월 모멘텀 포함)
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/krx_utils.py" screen_market KOSPI

# 시총 1000억 이상, 상위 100개
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/krx_utils.py" screen_market KOSPI --min-cap 1000 --max-results 100

# KOSDAQ 스크리닝
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/krx_utils.py" screen_market KOSDAQ --min-cap 500
```

이 명령어는 펀더멘털(PER/PBR/DIV)과 3개월 모멘텀을 병렬로 수집합니다.

### 2단계: 각 종목 펀더멘털 조회
```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/krx_utils.py" fundamental {종목코드}
```

### 3단계: 조건 필터링

수집된 데이터를 기반으로 조건에 맞는 종목 필터링

## 지원 조건

| 조건 | 예시 | 설명 |
|------|------|------|
| PER | `PER<15` | PER 15 미만 |
| PBR | `PBR<1` | PBR 1 미만 |
| DIV | `DIV>3` | 배당수익률 3% 초과 |
| 시총 | `시총>1조` | 시가총액 1조 초과 |
| 시총 | `시총<1000억` | 시가총액 1000억 미만 |

### 모멘텀 조건 (screen_market 사용 시)
| 조건 | 예시 | 설명 |
|------|------|------|
| 모멘텀 | `momentum_3m > 10` | 3개월 수익률 10% 초과 |
| 모멘텀 | `momentum_3m < -10` | 3개월 수익률 -10% 미만 |

## 스크리닝 예시

### 저PER 종목
```
조건: PER > 0 AND PER < 10
```

### 고배당 종목
```
조건: DIV > 3%
```

### 저평가 우량주
```
조건: PER < 15 AND PBR < 1.5 AND 시총 > 5000억
```

### 소형 가치주
```
조건: 시총 < 3000억 AND PER < 10 AND PBR < 0.8
```

## 결과 출력 형식

```
📋 스크리닝 결과: 저PER 종목 (PER < 10)

시장: KOSPI + KOSDAQ
조건: PER > 0 AND PER < 10
결과: 127개 종목

| 순위 | 종목명 | 코드 | 시장 | PER | PBR | 시총(억) |
|------|--------|------|------|-----|-----|---------|
| 1 | XXX | 123456 | KOSPI | 3.2 | 0.5 | 12,500 |
| 2 | YYY | 234567 | KOSDAQ | 4.1 | 0.7 | 3,200 |
| ... | ... | ... | ... | ... | ... | ... |
```

## 고급 스크리닝 (Python 직접 사용)

복잡한 조건은 Python으로 직접 처리:

```python
from pykrx import stock
from datetime import datetime

date = datetime.now().strftime('%Y%m%d')

# KOSPI 전 종목 펀더멘털
for ticker in stock.get_market_ticker_list(date, market="KOSPI"):
    df = stock.get_market_fundamental(date, date, ticker)
    if not df.empty:
        per = df.iloc[0]['PER']
        pbr = df.iloc[0]['PBR']

        # 조건 필터링
        if 0 < per < 10 and pbr < 1:
            name = stock.get_market_ticker_name(ticker)
            print(f"{name} ({ticker}): PER={per}, PBR={pbr}")
```

## 주의사항

- 전체 시장 스크리닝은 시간이 오래 걸릴 수 있습니다 (1-5분)
- pykrx API 호출 제한에 주의하세요
- 결과는 조회 시점 기준이며, 실시간 데이터가 아닙니다
