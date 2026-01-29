---
name: ultra-analyze
description: KRX-Quant 울트라 분석 모드. 모든 기능을 최대 역량으로 활용하여 심층 분석 수행. "울트라 분석", "ultra", "딥 분석", "전체 분석" 등의 요청에 자동 활성화.
argument-hint: <종목명|종목코드> [저장경로]
---

# KRX-Quant Ultra 분석 모드

모든 quant-k 기능을 최대 역량으로 활용하여 심층 종합분석을 수행합니다.

## 사전 요구사항

Python과 pykrx가 필요합니다. 처음 사용 시 `/quant-k:setup`을 실행하세요.

## 자동 활성화 패턴

다음 키워드가 포함된 요청에 자동 활성화됩니다:

- `울트라`, `ultra`
- `딥 분석`, `deep analysis`
- `전체 분석`, `풀 분석`
- `심층 분석`, `최대 분석`

**예시:**
```
"동운아나텍 울트라 분석해줘"
"삼성전자 ultra 모드로 분석"
"094170 딥 분석해서 report/에 저장"
```

## Ultra 모드 vs 일반 모드

| 항목 | 일반 모드 | Ultra 모드 |
|------|----------|-----------|
| 가격 데이터 | 6개월 | 1년 |
| 이동평균선 | 20/60일 | 5/10/20/60/120/240일 |
| 기술적 지표 | 기본 | RSI, MACD, 볼린저밴드 |
| 유사 종목 | 5개 | 20개 |
| 리포트 길이 | 요약 | 상세 (10+ 섹션) |

## 데이터 수집 명령어

### pykrx DataFrame 컬럼 레퍼런스

pykrx가 반환하는 DataFrame의 **실제 컬럼명**입니다. 인라인 Python 코드에서 반드시 이 컬럼명을 사용하세요.

**OHLCV (get_market_ohlcv):**
```python
['시가', '고가', '저가', '종가', '거래량', '등락률']
# 영문 없음! '등락률'은 전일대비 변동률 (%)
```

**Fundamental (get_market_fundamental):**
```python
['BPS', 'PER', 'PBR', 'EPS', 'DIV', 'DPS']
# 영문 대문자만 사용
```

**Market Cap (get_market_cap):**
```python
['종가', '시가총액', '거래량', '거래대금', '상장주식수']
# '시가총액'은 원 단위 (억원 아님)
```

**⚠️ 주의:** `ret_3m`, `momentum_3m`, `return_1m` 같은 컬럼은 **존재하지 않습니다**. 모멘텀은 직접 계산해야 합니다:

```python
# 3개월 수익률 계산 예시
ohlcv = stock.get_market_ohlcv(start_date, end_date, ticker)
price_now = int(ohlcv['종가'].iloc[-1])
price_3m = int(ohlcv['종가'].iloc[0])
momentum_3m = round((price_now - price_3m) / price_3m * 100, 2)
```

### 방어적 코딩 패턴

pykrx API는 데이터가 없거나 오류 발생 시 **빈 DataFrame**을 반환합니다. 항상 확인하세요:

```python
from pykrx import stock
import pandas as pd

# ❌ 잘못된 코드 - 빈 DataFrame 시 KeyError 발생
df = stock.get_market_fundamental(date, date, ticker)
per = df['PER'].iloc[0]  # KeyError if df is empty!

# ✅ 올바른 코드 - 빈 DataFrame 체크
df = stock.get_market_fundamental(date, date, ticker)
if df.empty:
    per = None
    print(f"Warning: No data for {ticker}")
else:
    per = float(df['PER'].iloc[0]) if pd.notna(df['PER'].iloc[0]) else None

# ✅ 더 안전한 패턴 - try/except
try:
    df = stock.get_market_fundamental(date, date, ticker)
    per = float(df['PER'].iloc[0]) if not df.empty and pd.notna(df['PER'].iloc[0]) else None
except Exception as e:
    print(f"Error fetching data: {e}")
    per = None
```

**빈 데이터 발생 원인:**
- 휴장일/공휴일 날짜 조회
- 상장폐지된 종목코드
- 오타가 있는 종목코드
- pykrx 서버 일시 오류

### 기본 수집
```bash
# 종목 확인
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/krx_utils.py" search "종목명"
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/krx_utils.py" ticker_info "종목코드"

# 1년 가격 데이터
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/krx_utils.py" ohlcv "종목코드" --days 365

# 펀더멘털
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/krx_utils.py" fundamental "종목코드"

# 시가총액 및 순위
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/krx_utils.py" market_cap "종목코드"

# 시장 전체 종목 (비교용)
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/krx_utils.py" market_tickers KOSPI
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/krx_utils.py" market_tickers KOSDAQ
```

### 병렬 데이터 수집 (권장)
```bash
# Phase 1 데이터를 병렬로 수집 (ohlcv + fundamental + market_cap 동시 실행)
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/krx_utils.py" collect_all "종목코드" --days 365
```

이 명령어는 ohlcv, fundamental, market_cap을 ThreadPoolExecutor로 동시에 수집하여 3배 빠릅니다.

## ⚠️ 필수 실행 지침 (MANDATORY EXECUTION)

**이 스킬이 로드되면 아래 워크플로우를 반드시 순서대로 실행하세요. 단순 참고가 아닌 실행 명령입니다!**

### 실행 순서 요약

1. **Phase 1**: KRX 기본 데이터 수집 (Bash - `collect_all`)
2. **Phase 2-4**: 에이전트 병렬 실행 (**Task tool 필수 사용**)
3. **Phase 5**: 기술분석 수행
4. **Phase 6**: Ultra 리포트 통합 생성

### ⚠️ 중요: 스킬 vs 에이전트 구분

**Task tool 호출 시 반드시 에이전트 이름을 사용하세요. 스킬 이름은 Task tool에서 작동하지 않습니다!**

| 용도 | ❌ 스킬 (슬래시 명령용) | ✅ 에이전트 (Task tool용) |
|------|-------------------------|---------------------------|
| 팩터 분석 | `quant-k:factor-analyze` | **`quant-k:quant-analyst`** |
| 종목 스크리닝 | `quant-k:stock-screen` | **`quant-k:stock-screener`** |
| 웹 스크래핑 | `quant-k:browser-scraper` | **`quant-k:web-scraper`** |

**왜 중요한가?**
- 스킬(`/quant-k:factor-analyze`)은 대화형 명령으로, 사용자가 직접 실행
- 에이전트(`quant-k:quant-analyst`)는 Task tool의 `subagent_type`으로 병렬 실행 가능
- 스킬 이름을 `subagent_type`에 사용하면 **즉시 종료되어 작업이 수행되지 않음**

### 에이전트 구성

| 에이전트 | 역할 | Phase |
|----------|------|-------|
| `quant-k:web-scraper` | 외부 데이터 수집 (네이버/DART) | Phase 2 |
| `quant-k:quant-analyst` | 팩터 분석, 밸류에이션 | Phase 3 |
| `quant-k:stock-screener` | 유사 종목 검색 | Phase 4 |

---

## 📥 데이터 수집 단계

### Phase 1: KRX 기본 데이터 수집

**권장: collect_all로 병렬 수집**
```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/krx_utils.py" collect_all "종목코드" --days 365
```

위 명령 하나로 ohlcv, fundamental, market_cap을 병렬 수집합니다.

### Phase 2-4: 에이전트 병렬 실행 (⚠️ 필수)

**Phase 1 완료 후, 아래 3개 에이전트를 Task tool로 동시에 병렬 실행하세요!**

```
# ✅ 반드시 하나의 메시지에서 3개의 Task tool을 동시 호출하세요:

Task(
  subagent_type="quant-k:web-scraper",
  model="sonnet",
  prompt="네이버 금융에서 {종목코드} 추가 정보 수집: 투자의견, 목표가, 뉴스 헤드라인. 저장경로: {저장경로}"
)

Task(
  subagent_type="quant-k:quant-analyst",
  model="sonnet",
  prompt="""
  다음 종목의 퀀트 팩터 분석을 수행하세요:
  - 종목: {종목명} ({종목코드})
  - 저장경로: {저장경로}

  분석 항목:
  1. PER/PBR 밸류에이션 평가
  2. 3/6/12개월 모멘텀 계산
  3. 적정가 산출 (PER/PBR 기반)
  4. 투자 스코어카드 작성
  """
)

Task(
  subagent_type="quant-k:stock-screener",
  model="sonnet",
  prompt="시장에서 {종목명}과 유사한 밸류에이션을 가진 종목 20개를 찾아주세요. 조건: PER ±30%, PBR ±30%, 동일 시장. 저장경로: {저장경로}"
)
```

**⚠️ 주의사항:**
- 3개의 Task tool 호출을 **하나의 응답에서 동시에** 실행해야 병렬 처리됩니다
- 각 에이전트에 저장경로를 전달하여 결과가 올바른 위치에 저장되도록 합니다
- 에이전트 완료를 기다린 후 Phase 5로 진행합니다

---

## 📊 심층 분석 단계

### Phase 5: 고급 기술분석

- 이동평균선 분석 (5/10/20/60/120/240일)
- RSI, MACD
- 볼린저밴드
- 지지/저항선 분석

---

## 📝 리포트 단계

### Phase 6: Ultra 리포트 통합

모든 에이전트 결과를 통합하여 Ultra 리포트 생성

### 순차 실행 vs 병렬 실행

| 방식 | Phase 1-2 | Phase 3-4 | Phase 5-6 | 총 시간 |
|------|-----------|-----------|-----------|---------|
| 순차 실행 | 30초 | 60초 | 30초 | ~120초 |
| 병렬 실행 | 10초 | 20초 | 15초 | ~45초 |

**⚠️ 주의:** 에이전트 병렬 실행 시 동일 파일 수정 금지 (race condition 방지)

## 리포트 구조

```markdown
# {종목명} ({종목코드}) Ultra 분석 리포트

> 생성일: {날짜} | 분석 모드: ULTRA

---

## Executive Summary
{핵심 요약 3-5문장}

## 투자 스코어카드
| 항목 | 점수 | 등급 |
|------|------|------|
| 밸류에이션 | {1-10} | {A-F} |
| 모멘텀 | {1-10} | {A-F} |
| 안정성 | {1-10} | {A-F} |
| **종합** | **{1-10}** | **{A-F}** |

---

## Part 1: 기업 개요
- 종목명, 종목코드, 시장
- 시가총액 및 순위

## Part 2: 주가 분석 (1년)
- 52주 고가/저가
- 수익률 분석 (1M/3M/6M/12M)
- 변동성 분석

## Part 3: 기술적 분석
- 이동평균선 분석 (6개)
- 볼린저밴드
- RSI, MACD
- 지지/저항선

## Part 4: 밸류에이션 분석
- PER/PBR/EPS/BPS 상세
- 적정가 산출

## Part 5: 유사 종목 비교
- 시총 유사 종목
- 밸류에이션 유사 종목

## Part 6: 투자 전략
- 매수 타이밍 분석
- 목표가/손절가
- 리스크 요인

## Part 7: 결론
- 강점/약점 요약
- 최종 투자의견

---

> 본 리포트는 quant-k Ultra 모드에 의해 자동 생성되었습니다.
```

## 출력 파일 구조

Ultra 모드는 디렉토리 구조로 출력:

```
{저장경로}/{종목명}_ultra_{날짜}/
├── README.md                    # 메인 리포트
├── data/
│   └── ohlcv.csv               # 가격 데이터
└── analysis/
    ├── technical.md            # 기술적 분석
    └── valuation.md            # 밸류에이션 분석
```

## ⚠️ 출력 경로 규칙 (필수)

**모든 파일은 반드시 사용자가 지정한 저장경로 아래에만 생성해야 합니다.**

```
✅ 올바른 예시 (저장경로: report/lnk)
report/lnk/
├── data/ohlcv.csv
├── analysis/technical.md
├── scripts/analysis.py
└── README.md

❌ 잘못된 예시 (프로젝트 루트에 파일 생성)
./data/           ← 금지!
./scripts/        ← 금지!
./docs/           ← 금지!
./PROJECT_STATUS.txt  ← 금지!
```

**에이전트 실행 시 규칙:**
1. 저장경로가 지정되면, 모든 중간 파일(data, scripts, docs)도 해당 경로 아래에 생성
2. 저장경로가 미지정이면, 현재 디렉토리에 `{종목명}_ultra_{날짜}/` 디렉토리 생성 후 그 안에 모든 파일 저장
3. **절대로 프로젝트 루트에 직접 파일을 생성하지 않음**
4. 디렉토리가 없으면 자동 생성 (`mkdir -p`)

## 사용법

### 명령어
```bash
/quant-k:ultra-analyze 동운아나텍
/quant-k:ultra-analyze 094170 report/
```

### 자연어
```
"동운아나텍 울트라 분석해줘"
"삼성전자 ultra 모드로 전체 분석"
"SK하이닉스 심층 분석 리포트 만들어줘"
```

## 주의: JSON 직렬화

분석 결과를 JSON으로 저장할 때 numpy/pandas 타입은 직렬화 오류를 발생시킵니다.

**안전한 JSON 저장 패턴:**
```python
import json
import numpy as np

def safe_json_value(v):
    """numpy 타입을 Python 네이티브 타입으로 변환"""
    if isinstance(v, (np.integer, np.int64)):
        return int(v)
    elif isinstance(v, (np.floating, np.float64)):
        return float(v)
    elif isinstance(v, np.ndarray):
        return v.tolist()
    elif pd.isna(v):
        return None
    return v

def safe_dict(d):
    """딕셔너리의 모든 값을 안전하게 변환"""
    return {k: safe_json_value(v) for k, v in d.items()}

# 사용 예시
result = safe_dict({"per": df['PER'].iloc[0], "price": ohlcv['종가'].iloc[-1]})
json.dump(result, f, ensure_ascii=False)
```

**또는 간단히:**
```python
# 모든 숫자를 float()로 변환
result = {
    "per": float(per) if per else None,
    "price": int(price),
}
```

## WebFetch 차단 사이트 처리

일부 금융 사이트(예: `finance.naver.com`, `dart.fss.or.kr`)는 WebFetch로 접근이 차단됩니다.

**차단된 사이트에서 데이터가 필요한 경우:**

browser-scraper 스킬을 사용하세요:

```bash
# 네이버 금융 시가총액 순위
/quant-k:browser-scraper https://finance.naver.com/sise/sise_market_sum.naver "시가총액 상위 100개"

# 네이버 금융 종목 상세
/quant-k:browser-scraper https://finance.naver.com/item/main.naver?code={종목코드} "기업 정보"

# DART 공시 검색
/quant-k:browser-scraper AUTO: https://dart.fss.or.kr "최근 공시"

# KRX 데이터 포털 (API 자동 탐지)
/quant-k:browser-scraper https://data.krx.co.kr --discover-api "종목별 시세"
```

**browser-scraper vs WebFetch:**

| 도구 | 장점 | 단점 | 사용 시나리오 |
|------|------|------|--------------|
| WebFetch | 빠름, 간단 | 일부 사이트 차단 | 공개 API, 허용된 사이트 |
| browser-scraper | 차단 우회, JS 렌더링 | 느림, 복잡 | 네이버, DART, KRX 등 |

**권장 워크플로우:**
1. 먼저 pykrx로 기본 데이터 수집 (`collect_all`)
2. 추가 정보 필요 시 browser-scraper로 네이버/DART 스크래핑
3. 결과 통합하여 리포트 생성

## 에러 처리

| 상황 | 처리 |
|------|------|
| pykrx 미설치 | `/quant-k:setup` 안내 |
| 데이터 부족 | 가능한 데이터만으로 부분 리포트 |
| 1년 데이터 없음 | 가용 기간으로 축소 |
| 저장 실패 | 콘솔에 전체 출력 |

---

## ✅ 실행 체크리스트 (완료 전 확인 필수)

**Ultra 분석을 완료하기 전에 모든 항목이 체크되어야 합니다:**

- [ ] **Phase 1**: `collect_all` 명령으로 KRX 기본 데이터 수집 완료
- [ ] **Phase 2**: `quant-k:web-scraper` 에이전트 실행 (Task tool 사용)
- [ ] **Phase 3**: `quant-k:quant-analyst` 에이전트 실행 (Task tool 사용)
- [ ] **Phase 4**: `quant-k:stock-screener` 에이전트 실행 (Task tool 사용)
- [ ] **Phase 5**: 기술적 분석 (이동평균, RSI, MACD, 볼린저밴드) 수행
- [ ] **Phase 6**: Ultra 리포트 통합 생성 및 저장

**⚠️ 중요:** Phase 2-4는 반드시 Task tool로 에이전트를 spawn해야 합니다. 직접 분석하지 마세요!

**완료 조건:**
1. 모든 에이전트가 결과를 반환함
2. README.md (메인 리포트)가 저장경로에 생성됨
3. 사용자에게 리포트 위치와 요약을 안내함
