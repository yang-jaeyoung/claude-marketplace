---
name: krx-collect
description: KRX 주식 데이터 수집
argument-hint: <KOSPI|KOSDAQ> [ticker] [startDate] [endDate]
aliases:
  - collect
  - data
---

# KRX 데이터 수집 스킬

KRX(한국거래소) 주식 데이터를 수집합니다.

## 사용법

### 종목 목록 조회
```
/krx-collect KOSPI
/krx-collect KOSDAQ
```

### 가격 데이터 (OHLCV)
```
/krx-collect 005930 20240101 20241231
```

### 재무 지표
```
/krx-collect 005930 --detail
```

### 캐시 갱신
```
/krx-collect --refresh
```

## MCP 도구

이 스킬은 `krx_collect` MCP 도구를 사용합니다.

### 파라미터

| 파라미터 | 타입 | 설명 |
|---------|------|------|
| dataType | enum | tickers, ohlcv, fundamental, marketcap |
| market | enum | KOSPI, KOSDAQ |
| ticker | string | 6자리 종목 코드 |
| startDate | string | 시작일 (YYYYMMDD) |
| endDate | string | 종료일 (YYYYMMDD) |
| refresh | boolean | 캐시 무시 |

## 예시 출력

### 종목 목록
```json
{
  "tickers": [
    {"ticker": "005930", "name": "삼성전자", "market": "KOSPI"},
    {"ticker": "000660", "name": "SK하이닉스", "market": "KOSPI"}
  ],
  "count": 932,
  "date": "20241231"
}
```

### OHLCV
```json
{
  "ticker": "005930",
  "data": [
    {"date": "20240102", "open": 78000, "high": 79000, "low": 77500, "close": 78500, "volume": 12345678}
  ],
  "rows": 245,
  "cached": false
}
```
