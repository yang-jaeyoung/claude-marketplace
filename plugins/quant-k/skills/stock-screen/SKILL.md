---
name: stock-screen
description: 조건 기반 종목 스크리닝
argument-hint: <conditions> [--market KOSPI] [--save name]
aliases:
  - screen
  - filter
---

# 종목 스크리닝 스킬

조건을 지정하여 종목을 필터링합니다.

## 사용법

### 기본 스크리닝
```
/stock-screen PER<10 ROE>15
/stock-screen 시총>1조 PBR<1
```

### 조건 저장/로드
```
/stock-screen PER<10 --save "저PER"
/stock-screen --load "저PER"
```

### 정렬
```
/stock-screen PER<15 --sort PER
```

## DSL 문법

```
<condition> ::= <factor><operator><value>
<operator>  ::= < | > | <= | >= | == | !=
<value>     ::= 숫자 | 숫자조 | 숫자억 | 숫자%
```

## MCP 도구

`stock_screen` 도구를 사용합니다.
