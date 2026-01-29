---
name: krx-collect
description: KRX 주식 데이터 수집
argument-hint: <KOSPI|KOSDAQ> [ticker] [--days N]
---

# KRX 데이터 수집 스킬

KRX(한국거래소) 주식 데이터를 수집합니다.

## 사전 요구사항

Python과 pykrx가 필요합니다. 처음 사용 시 `/quant-k:setup`을 실행하세요.

## 사용법

### 종목 목록 조회
```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/krx_utils.py" market_tickers KOSPI
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/krx_utils.py" market_tickers KOSDAQ
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/krx_utils.py" market_tickers ALL
```

### 종목 검색
```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/krx_utils.py" search "삼성"
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/krx_utils.py" ticker_info 005930
```

### 가격 데이터 (OHLCV)
```bash
# 기본 1년
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/krx_utils.py" ohlcv 005930

# 기간 지정
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/krx_utils.py" ohlcv 005930 --days 180
```

### 펀더멘털 지표
```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/krx_utils.py" fundamental 005930
```

### 시가총액
```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/krx_utils.py" market_cap 005930
```

## 명령어 요약

| 명령어 | 설명 | 예시 |
|--------|------|------|
| `market_tickers` | 시장 전체 종목 | `market_tickers KOSPI` |
| `search` | 종목명 검색 | `search "삼성"` |
| `ticker_info` | 종목 기본정보 | `ticker_info 005930` |
| `ohlcv` | 가격 데이터 | `ohlcv 005930 --days 365` |
| `fundamental` | 재무지표 | `fundamental 005930` |
| `market_cap` | 시가총액 | `market_cap 005930` |

## 출력 형식 (JSON)

### 종목 목록
```json
{
  "market": "KOSPI",
  "date": "20260129",
  "count": 932,
  "tickers": [
    {"ticker": "005930", "name": "삼성전자", "market": "KOSPI"}
  ]
}
```

### OHLCV
```json
{
  "ticker": "005930",
  "rows": 245,
  "current_price": 160700,
  "high_52w": 166600,
  "low_52w": 149200,
  "ma20": 158000,
  "ma60": 155000,
  "data": [...]
}
```

### 펀더멘털
```json
{
  "ticker": "005930",
  "date": "20260129",
  "PER": 32.46,
  "PBR": 2.77,
  "EPS": 4950,
  "BPS": 57951,
  "DIV": 0.9
}
```
