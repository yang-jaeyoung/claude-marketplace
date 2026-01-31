---
description: 퀀트 팩터 분석
---

# /factor-analyze

퀀트 팩터를 분석합니다.

## 필수 명령어

```bash
# 데이터 수집 (병렬)
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/krx_utils.py" collect_all 005930 --days 365

# 시장 비교용 스크리닝
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/krx_utils.py" screen_market KOSPI --min-cap 1000
```

⚠️ **절대 경로 필수!** 상대 경로(`scripts/...`) 사용 금지

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
