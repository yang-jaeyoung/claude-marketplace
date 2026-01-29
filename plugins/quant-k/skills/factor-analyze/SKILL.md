---
name: factor-analyze
description: 퀀트 팩터 분석
argument-hint: <종목코드> [factors]
---

# 팩터 분석 스킬

퀀트 팩터를 분석하고 종목의 팩터 노출도를 계산합니다.

## 사전 요구사항

Python과 pykrx가 필요합니다. 처음 사용 시 `/quant-k:setup`을 실행하세요.

## 사용법

### 종목 팩터 노출도 분석

1. 먼저 데이터 수집:
```bash
# 펀더멘털 데이터
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/krx_utils.py" fundamental 005930

# 가격 데이터 (모멘텀 계산용)
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/krx_utils.py" ohlcv 005930 --days 365

# 시가총액 (사이즈 팩터용)
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/krx_utils.py" market_cap 005930
```

2. 팩터 계산 (수집된 데이터 기반):

### 지원 팩터

| 카테고리 | 팩터 | 계산 방법 |
|---------|------|----------|
| **가치** | PER | fundamental에서 직접 조회 |
| | PBR | fundamental에서 직접 조회 |
| | DIV | fundamental에서 직접 조회 |
| **모멘텀** | MOM_1M | ohlcv 데이터에서 1개월 수익률 계산 |
| | MOM_3M | ohlcv 데이터에서 3개월 수익률 계산 |
| | MOM_6M | ohlcv 데이터에서 6개월 수익률 계산 |
| | MOM_12M | ohlcv 데이터에서 12개월 수익률 계산 |
| **사이즈** | SIZE | market_cap에서 시가총액 조회 |

## 팩터 점수 계산 예시

```python
# 모멘텀 계산 (ohlcv 데이터 사용)
# MOM_3M = (현재가 - 3개월전 가격) / 3개월전 가격 * 100

# 가치 팩터 (섹터 평균 대비)
# PER_SCORE = (섹터평균PER - 종목PER) / 섹터평균PER
```

## 분석 결과 예시

```
📊 삼성전자 (005930) 팩터 분석

가치 팩터:
  PER: 32.46 (시장평균 15.2 대비 고평가)
  PBR: 2.77 (시장평균 1.2 대비 고평가)
  DIV: 0.9%

모멘텀 팩터:
  1개월: +5.2%
  3개월: +12.8%
  6개월: +8.5%
  12개월: +15.3%

사이즈 팩터:
  시가총액: 959조원 (KOSPI 1위)

종합 평가:
  - 가치: 고평가 구간
  - 모멘텀: 강한 상승세
  - 추천 전략: 모멘텀 추종
```

## 시장 전체 팩터 순위

시장 전체 종목의 팩터 순위를 보려면:

```bash
# 시장 전체 펀더멘털 수집 후 정렬
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/krx_utils.py" market_tickers KOSPI
# 각 종목별 fundamental 조회 후 PER 기준 정렬
```

## 복합 팩터 전략

여러 팩터를 조합한 전략:

| 전략 | 팩터 조합 | 설명 |
|------|----------|------|
| 가치투자 | 저PER + 저PBR | 저평가 종목 |
| 모멘텀 | MOM_3M + MOM_6M | 상승 추세 종목 |
| 퀄리티 | 고ROE + 저부채 | 우량 기업 |
| 복합 | 저PER + MOM_3M | 저평가 + 상승세 |
