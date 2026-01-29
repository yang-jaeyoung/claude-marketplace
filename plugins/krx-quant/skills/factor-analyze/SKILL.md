---
name: factor-analyze
description: 퀀트 팩터 분석
argument-hint: <factors> [--market KOSPI] [--top N]
aliases:
  - factor
  - analyze
---

# 팩터 분석 스킬

퀀트 팩터를 분석하고 종목 순위를 계산합니다.

## 사용법

### 단일 팩터 분석
```
/factor-analyze PER
/factor-analyze MOM_3M --market KOSDAQ
```

### 복합 팩터 분석
```
/factor-analyze PER MOM_3M --weights 0.5 0.5
```

### 종목 팩터 노출도
```
/factor-analyze 005930
```

## 지원 팩터

| 카테고리 | 팩터 |
|---------|------|
| Value | PER, PBR |
| Momentum | MOM_1M, MOM_3M, MOM_6M, MOM_12M |

## MCP 도구

`factor_analyze` 도구를 사용합니다.
