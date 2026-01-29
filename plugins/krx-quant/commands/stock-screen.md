---
description: 조건 기반 종목 스크리닝
---

# /stock-screen

조건을 지정하여 종목을 필터링합니다.

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
