---
name: factor-analyze
description: 퀀트 팩터 분석
argument-hint: <종목코드> [factors]
---

# 팩터 분석

## 데이터 수집

```bash
# 병렬 수집 권장
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/krx_utils.py" collect_all 005930 --days 365

# 시장 비교용
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/krx_utils.py" screen_market KOSPI --min-cap 1000
```

## 지원 팩터

| 카테고리 | 팩터 | 출처 |
|---------|------|------|
| **가치** | PER, PBR, DIV | fundamental |
| **모멘텀** | 1M/3M/6M/12M | ohlcv 수익률 계산 |
| **사이즈** | 시가총액 | market_cap |

## 분석 출력

```
📊 {종목명} 팩터 분석

가치 팩터:
  PER: {값} (시장평균 대비 {평가})
  PBR: {값}
  DIV: {값}%

모멘텀 팩터:
  1개월: {수익률}%
  3개월: {수익률}%

종합 평가: {가치/모멘텀/복합 전략 추천}
```

## 복합 팩터 전략

| 전략 | 조합 |
|------|------|
| 가치투자 | 저PER + 저PBR |
| 모멘텀 | MOM_3M + MOM_6M |
| 복합 | 저PER + 양의 MOM_3M |
