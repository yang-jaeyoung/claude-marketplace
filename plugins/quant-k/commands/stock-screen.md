---
description: 조건 기반 종목 스크리닝
---

# /stock-screen

조건을 지정하여 종목을 필터링합니다.

## 필수 명령어

```bash
# 시장 전체 스크리닝
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/krx_utils.py" screen_market KOSPI --min-cap 1000 --max-results 100
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/krx_utils.py" screen_market KOSDAQ --min-cap 500
```

⚠️ **절대 경로 필수!** 상대 경로(`scripts/...`) 사용 금지

## 사용법

```
/stock-screen <조건1> [조건2] ... [옵션]
```

## 예시

```bash
# 저PER + 고ROE
/stock-screen PER<10 ROE>15

# 대형주 저평가
/stock-screen 시총>1조 PBR<1

# 조건 저장
/stock-screen PER<10 --save "저PER전략"

# 저장된 조건 사용
/stock-screen --load "저PER전략"
```

## DSL 문법

- `PER<10` - PER 10 미만
- `시총>1조` - 시가총액 1조 초과
- `배당률>=3%` - 배당수익률 3% 이상
