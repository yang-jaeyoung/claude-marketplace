---
description: quant-k 플러그인 환경 설정 (Python, pykrx 설치 확인)
---

# quant-k 환경 설정

quant-k 플러그인 사용을 위한 환경을 설정합니다.

## 설정 단계

### 1단계: Python 확인

```bash
python3 --version
```

Python 3.8 이상이 필요합니다. 없으면 설치 안내를 제공합니다.

### 2단계: pykrx 설치 확인 및 설치

```bash
python3 -c "import pykrx; print(f'pykrx {pykrx.__version__} OK')" 2>/dev/null || pip3 install pykrx
```

### 3단계: 추가 의존성 설치

```bash
pip3 install pandas numpy
```

### 4단계: 연결 테스트

```python
from pykrx import stock
from datetime import datetime

# 삼성전자로 연결 테스트
ticker = '005930'
date = datetime.now().strftime('%Y%m%d')
name = stock.get_market_ticker_name(ticker)
print(f'✓ KRX 연결 성공: {name} ({ticker})')
```

## 예상 출력

```
🔧 quant-k 환경 설정

1. Python 확인
   ✓ Python 3.11.4

2. pykrx 설치 확인
   ✓ pykrx 1.0.45 설치됨

3. 추가 의존성
   ✓ pandas 2.0.3
   ✓ numpy 1.24.3

4. KRX 연결 테스트
   ✓ 삼성전자 (005930) 조회 성공

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ quant-k 설정 완료!

사용 가능한 명령어:
  /quant-k:stock-report <종목명>  - 종합분석 리포트
  /quant-k:stock-screen          - 조건 스크리닝
  /quant-k:factor-analyze        - 팩터 분석
  /quant-k:ultra-analyze         - 심층 분석
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## 에러 처리

| 문제 | 해결책 |
|------|--------|
| Python 없음 | macOS: `brew install python3`, Windows: python.org에서 설치 |
| pip 없음 | `python3 -m ensurepip --upgrade` |
| pykrx 설치 실패 | `pip3 install --user pykrx` |
| KRX 연결 실패 | 네트워크 확인, 잠시 후 재시도 |

## 환경 요구사항

- Python 3.8+
- pip3
- 인터넷 연결 (KRX 데이터 조회용)
