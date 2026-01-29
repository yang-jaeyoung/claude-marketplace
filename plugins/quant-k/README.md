# KRX-Quant Plugin

> KRX(한국거래소) 퀀트 분석 및 종목 발굴 플러그인

## 개요

KRX-Quant는 KOSPI/KOSDAQ 시장의 퀀트 분석을 자동화하는 Claude Code 플러그인입니다. 팩터 분석, 종목 스크리닝, 종합 리포트 생성 기능을 제공합니다.

## 설치

```bash
claude plugins add github:jyyang/claude-marketplace --name quant-k
```

### 환경 설정 (필수)

플러그인 설치 후 **반드시** setup을 실행하세요:

```bash
/quant-k:setup
```

이 명령은 다음을 확인/설치합니다:
- Python 3.8+
- pykrx (KRX 데이터 API)
- pandas, numpy

## 빠른 시작

### 0. Ultra 분석 (최대 역량 모드) ⭐

```bash
# 자연어로 요청
"동운아나텍 울트라 분석해서 report/에 저장해줘"
"삼성전자 ultra 모드로 분석"

# 또는 명령어로 직접 실행
/quant-k:ultra-analyze 동운아나텍 report/
/quant-k:ultra-analyze 094170
```

**Ultra 모드 특징:**
- 1년 가격 데이터 분석
- 전체 이동평균선 (5/10/20/60/120/240일)
- RSI, MACD, 볼린저밴드
- 20개 유사 종목 스크리닝
- 투자 스코어카드 (A-F 등급)
- 디렉토리 구조 상세 리포트

### 1. 종합분석 리포트 (일반 모드)

```
# 자연어로 요청
"동운아나텍 분석해줘"
"삼성전자 매수타이밍 분석"

# 또는 명령어로 직접 실행
/quant-k:stock-report 동운아나텍 report/
/quant-k:stock-report 094170
```

### 2. 시장 데이터 수집

```bash
/quant-k:krx-collect KOSPI      # 전체 종목 목록
/quant-k:krx-collect 005930     # 삼성전자 1년 가격
```

### 3. 팩터 분석

```
/quant-k:factor-analyze 005930  # 종목 팩터 노출도
```

### 4. 종목 스크리닝

```
/quant-k:stock-screen PER<10    # 저PER 종목
```

## 사용 가능한 스킬

| 스킬 | 설명 | 예시 |
|------|------|------|
| `setup` | 환경 설정 (Python/pykrx 설치) | `/quant-k:setup` |
| `stock-report` | 종합분석 리포트 | `/quant-k:stock-report 삼성전자` |
| `ultra-analyze` | 심층분석 리포트 | `/quant-k:ultra-analyze 삼성전자` |
| `krx-collect` | KRX 데이터 수집 | `/quant-k:krx-collect KOSPI` |
| `factor-analyze` | 팩터 분석 | `/quant-k:factor-analyze 005930` |
| `stock-screen` | 조건 스크리닝 | `/quant-k:stock-screen PER<10` |
| `browser-scraper` | 웹 스크래핑 | `/quant-k:browser-scraper ...` |

## 아키텍처

이 플러그인은 **pykrx를 직접 호출**하는 방식을 사용합니다:

```
Claude Code
    ↓
스킬 (SKILL.md)
    ↓
Python 스크립트 (scripts/krx_utils.py)
    ↓
pykrx 라이브러리
    ↓
KRX 데이터
```

### 왜 MCP가 아닌가?

- **단순함**: 복잡한 브릿지/소켓 통신 불필요
- **빠름**: 직접 호출로 오버헤드 최소화
- **유지보수 용이**: pykrx API 변경 시 스크립트만 수정
- **배포 용이**: `/quant-k:setup`으로 환경 설정 완료

## Python 유틸리티

스킬들이 사용하는 Python 스크립트:

```bash
# 종목 검색
python3 scripts/krx_utils.py search "삼성"

# 종목 정보
python3 scripts/krx_utils.py ticker_info 005930

# 가격 데이터 (1년)
python3 scripts/krx_utils.py ohlcv 005930 --days 365

# 펀더멘털
python3 scripts/krx_utils.py fundamental 005930

# 시가총액
python3 scripts/krx_utils.py market_cap 005930

# 시장 전체 종목
python3 scripts/krx_utils.py market_tickers KOSPI
```

## 자동 활성화

자연어 요청에 자동으로 스킬이 활성화됩니다:

| 키워드 | 활성화 스킬 |
|--------|------------|
| "분석해줘", "리포트" | `stock-report` |
| "울트라", "ultra", "심층" | `ultra-analyze` |
| "데이터 수집", "종목 목록" | `krx-collect` |
| "팩터 분석" | `factor-analyze` |
| "스크리닝", "필터" | `stock-screen` |

## 예시

### 삼성전자 분석

```
"삼성전자 종합분석해줘"

→ 현재가, 시가총액, PER/PBR, 52주 고저, 이동평균선 분석
→ 투자의견 제시
```

### 저평가 종목 찾기

```
"PER 10 미만 종목 찾아줘"

→ KOSPI/KOSDAQ 전체 스크리닝
→ 조건에 맞는 종목 리스트
```

### Ultra 분석 리포트

```
"SK하이닉스 울트라 분석해서 report/에 저장"

→ 1년 가격 데이터 수집
→ 기술적 분석 (MA, RSI, MACD, 볼린저밴드)
→ 밸류에이션 분석
→ 유사 종목 비교
→ 디렉토리 구조로 리포트 저장
```

## 문제 해결

### pykrx 설치 오류

```bash
pip3 install --user pykrx pandas
```

### Python 버전 오류

Python 3.8 이상이 필요합니다:
```bash
python3 --version
```

### 데이터 조회 실패

- 휴일/주말에는 당일 데이터가 없을 수 있습니다
- 네트워크 연결을 확인하세요
- 잠시 후 재시도하세요

## 라이선스

MIT

## 기여

이슈나 PR은 언제나 환영합니다!
