---
name: krx-collect
description: KRX 주식 데이터 수집
argument-hint: <KOSPI|KOSDAQ> [ticker] [--days N]
---

# KRX 데이터 수집

## 명령어

```bash
# 종목 목록
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/krx_utils.py" market_tickers KOSPI

# 종목 검색
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/krx_utils.py" search "삼성"
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/krx_utils.py" ticker_info 005930

# 가격 데이터
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/krx_utils.py" ohlcv 005930 --days 365

# 펀더멘털
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/krx_utils.py" fundamental 005930

# 시가총액
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/krx_utils.py" market_cap 005930

# 병렬 수집 (권장)
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/krx_utils.py" collect_all 005930 --days 365
```

## 명령어 요약

| 명령어 | 설명 |
|--------|------|
| `market_tickers` | 시장 전체 종목 |
| `search` | 종목명 검색 |
| `ticker_info` | 종목 기본정보 |
| `ohlcv` | 가격 데이터 |
| `fundamental` | PER/PBR/DIV |
| `market_cap` | 시가총액 |
| `collect_all` | 병렬 수집 |
| `screen_market` | 시장 스크리닝 |

## 출력 (JSON)

모든 출력은 JSON 형식. `_shared/pykrx-reference.md` 참조.
