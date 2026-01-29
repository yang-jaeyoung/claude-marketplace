---
description: 퀀트 팩터 분석
---

# /factor-analyze

퀀트 팩터를 분석합니다.

## 사용법

```
/factor-analyze <팩터> [옵션]
```

## 예시

```bash
# PER 팩터 상위 20종목
/factor-analyze PER

# 모멘텀 팩터 (KOSDAQ)
/factor-analyze MOM_3M --market KOSDAQ --top 30

# 복합 팩터 (Value + Momentum)
/factor-analyze PER MOM_3M --weights 0.6 0.4

# 삼성전자 팩터 노출도
/factor-analyze 005930
```
