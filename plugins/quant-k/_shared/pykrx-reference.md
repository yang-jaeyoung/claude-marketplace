# pykrx 레퍼런스

이 문서는 pykrx 라이브러리 사용 시 필요한 컬럼명, 코딩 패턴, 에러 처리 방법을 정리합니다.

**⚠️ 필요할 때만 읽으세요.** 모든 스킬에서 자동으로 로드하지 않습니다.

---

## DataFrame 컬럼명

pykrx가 반환하는 DataFrame의 **실제 컬럼명**입니다.

### OHLCV (get_market_ohlcv)

```python
['시가', '고가', '저가', '종가', '거래량', '등락률']
# 영문 없음! '등락률'은 전일대비 변동률 (%)
```

### Fundamental (get_market_fundamental)

```python
['BPS', 'PER', 'PBR', 'EPS', 'DIV', 'DPS']
# 영문 대문자만 사용
```

### Market Cap (get_market_cap)

```python
['종가', '시가총액', '거래량', '거래대금', '상장주식수']
# '시가총액'은 원 단위 (억원 아님)
```

---

## 존재하지 않는 컬럼

`ret_3m`, `momentum_3m`, `return_1m` 같은 컬럼은 **존재하지 않습니다**.

모멘텀은 직접 계산해야 합니다:

```python
ohlcv = stock.get_market_ohlcv(start_date, end_date, ticker)
price_now = int(ohlcv['종가'].iloc[-1])
price_3m = int(ohlcv['종가'].iloc[0])
momentum_3m = round((price_now - price_3m) / price_3m * 100, 2)
```

---

## 방어적 코딩 패턴

pykrx API는 데이터가 없거나 오류 발생 시 **빈 DataFrame**을 반환합니다.

### 권장 패턴

```python
from pykrx import stock
import pandas as pd

# ✅ 빈 DataFrame 체크
df = stock.get_market_fundamental(date, date, ticker)
if df.empty:
    per = None
else:
    per = float(df['PER'].iloc[0]) if pd.notna(df['PER'].iloc[0]) else None

# ✅ try/except 패턴
try:
    df = stock.get_market_fundamental(date, date, ticker)
    per = float(df['PER'].iloc[0]) if not df.empty and pd.notna(df['PER'].iloc[0]) else None
except Exception as e:
    print(f"Error: {e}")
    per = None
```

### 빈 데이터 원인

- 휴장일/공휴일 날짜 조회
- 상장폐지된 종목코드
- 오타가 있는 종목코드
- pykrx 서버 일시 오류

---

## JSON 직렬화

numpy/pandas 타입은 직렬화 오류를 발생시킵니다.

```python
import json
import numpy as np
import pandas as pd

def safe_json_value(v):
    if isinstance(v, (np.integer, np.int64)):
        return int(v)
    elif isinstance(v, (np.floating, np.float64)):
        return float(v)
    elif isinstance(v, np.ndarray):
        return v.tolist()
    elif pd.isna(v):
        return None
    return v

# 사용
result = {k: safe_json_value(v) for k, v in data.items()}
json.dump(result, f, ensure_ascii=False)
```

---

## krx_utils.py 명령어

```bash
# 종목 검색
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/krx_utils.py" search "종목명"
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/krx_utils.py" ticker_info "종목코드"

# 데이터 수집
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/krx_utils.py" ohlcv "종목코드" --days 365
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/krx_utils.py" fundamental "종목코드"
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/krx_utils.py" market_cap "종목코드"

# 병렬 수집 (권장)
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/krx_utils.py" collect_all "종목코드" --days 365

# 시장 종목 목록
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/krx_utils.py" market_tickers KOSPI
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/krx_utils.py" market_tickers KOSDAQ

# 시장 스크리닝
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/krx_utils.py" screen_market KOSPI --min-cap 1000
```
