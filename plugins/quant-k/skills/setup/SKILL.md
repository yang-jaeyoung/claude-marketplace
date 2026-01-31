---
name: setup
description: quant-k 플러그인 환경 설정. Python과 pykrx 설치 확인.
---

# quant-k 환경 설정

## 설정 단계

### 1. Python 확인
```bash
python3 --version  # 3.8+ 필요
```

### 2. pykrx 설치
```bash
python3 -c "import pykrx; print(f'pykrx {pykrx.__version__} OK')" 2>/dev/null || pip3 install pykrx
```

### 3. 의존성 설치
```bash
pip3 install pandas numpy
```

### 4. 연결 테스트
```bash
python3 -c "from pykrx import stock; print('✓ KRX 연결:', stock.get_market_ticker_name('005930'))"
```

## 에러 처리

| 문제 | 해결 |
|------|------|
| Python 없음 | `brew install python3` (macOS) |
| pip 없음 | `python3 -m ensurepip --upgrade` |
| pykrx 설치 실패 | `pip3 install --user pykrx` |
| KRX 연결 실패 | 네트워크 확인, 재시도 |

## 설정 완료 후

```
/quant-k:stock-report <종목명>  - 종합분석
/quant-k:stock-screen          - 스크리닝
/quant-k:factor-analyze        - 팩터분석
/quant-k:ultra-analyze         - 심층분석
```
