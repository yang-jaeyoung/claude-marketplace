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

### 2. 환경 확인 (pykrx, pandas, KRX 연결)
```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/krx_utils.py" check_env
```

이 명령은 Python, pykrx, pandas 설치 및 KRX 연결 상태를 JSON으로 반환합니다.

### 3. 의존성 미설치 시
```bash
pip3 install pykrx pandas numpy
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
