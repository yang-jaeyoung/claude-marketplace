---
name: stock-screen
description: 조건 기반 종목 스크리닝
argument-hint: <conditions> [--market KOSPI|KOSDAQ]
---

# 종목 스크리닝

## 데이터 수집

```bash
# 시장 전체 스크리닝 (펀더멘털 + 3개월 모멘텀)
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/krx_utils.py" screen_market KOSPI --min-cap 1000 --max-results 100
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/krx_utils.py" screen_market KOSDAQ --min-cap 500
```

## 지원 조건

| 조건 | 필드 | 예시 |
|------|------|------|
| PER | `per` | `per < 10` |
| PBR | `pbr` | `pbr < 1` |
| 배당률 | `div` | `div > 3` |
| 시총(억) | `market_cap_billions` | `> 5000` |
| 모멘텀 | `momentum_3m` | `> 10` |

## 스크리닝 전략 예시

| 전략 | 조건 |
|------|------|
| 저PER | `0 < per < 10` |
| 고배당 | `div > 3` |
| 저평가 우량주 | `per < 15 AND pbr < 1.5 AND 시총 > 5000억` |
| 소형 가치주 | `시총 < 3000억 AND per < 10 AND pbr < 0.8` |

## 출력 형식

```markdown
📋 스크리닝 결과: {전략명}

조건: {조건}
결과: {N}개 종목

| 순위 | 종목명 | 코드 | PER | PBR | DIV | 시총(억) |
```

## 주의사항

- 전체 시장 스크리닝: 1-5분 소요
- 결과는 조회 시점 기준 (실시간 아님)
