#!/usr/bin/env python3
"""환경 검증 스크립트"""
import sys
import json

def check_python_version():
    """Python 3.9+ 확인"""
    v = sys.version_info
    if v.major < 3 or (v.major == 3 and v.minor < 9):
        return {"ok": False, "error": f"Python {v.major}.{v.minor} < 3.9"}
    return {"ok": True, "version": f"{v.major}.{v.minor}.{v.micro}"}

def check_pykrx():
    """pykrx 설치 및 기본 동작 확인"""
    try:
        import pykrx
        from pykrx import stock
        # 실제 API 호출 테스트
        tickers = stock.get_market_ticker_list("20240101", market="KOSPI")[:3]
        if len(tickers) < 3:
            return {"ok": False, "error": "pykrx API returned insufficient data"}
        return {"ok": True, "version": pykrx.__version__, "sample_tickers": tickers}
    except ImportError:
        return {"ok": False, "error": "pykrx not installed"}
    except Exception as e:
        return {"ok": False, "error": f"pykrx API error: {str(e)}"}

def check_pandas():
    """pandas 설치 확인"""
    try:
        import pandas
        return {"ok": True, "version": pandas.__version__}
    except ImportError:
        return {"ok": False, "error": "pandas not installed"}

def check_pyarrow():
    """pyarrow 설치 확인 (Parquet 지원)"""
    try:
        import pyarrow
        return {"ok": True, "version": pyarrow.__version__}
    except ImportError:
        return {"ok": False, "error": "pyarrow not installed"}

def main():
    results = {
        "python": check_python_version(),
        "pykrx": check_pykrx(),
        "pandas": check_pandas(),
        "pyarrow": check_pyarrow(),
    }

    all_ok = all(r["ok"] for r in results.values())
    results["all_ok"] = all_ok

    print(json.dumps(results, indent=2, ensure_ascii=False))
    sys.exit(0 if all_ok else 1)

if __name__ == "__main__":
    main()
