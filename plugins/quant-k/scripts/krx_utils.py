#!/usr/bin/env python3
"""
quant-k KRX 데이터 유틸리티

pykrx를 직접 사용하여 KRX 데이터를 조회합니다.
Claude Code 스킬에서 직접 호출됩니다.

사용법:
    python3 krx_utils.py ticker_info 005930
    python3 krx_utils.py ohlcv 005930 --days 365
    python3 krx_utils.py fundamental 005930
    python3 krx_utils.py market_tickers KOSPI
"""
import argparse
import json
import sys
from datetime import datetime, timedelta
from typing import Optional

try:
    from pykrx import stock
    import pandas as pd
except ImportError:
    print(json.dumps({"error": "pykrx not installed. Run: pip3 install pykrx pandas"}))
    sys.exit(1)


def get_latest_trading_date(max_days_back: int = 7) -> str:
    """최근 거래일 찾기 (주말/공휴일 제외)"""
    today = datetime.now()
    for i in range(max_days_back):
        date = (today - timedelta(days=i)).strftime('%Y%m%d')
        try:
            df = stock.get_market_fundamental(date, date, '005930')
            if not df.empty:
                return date
        except:
            continue
    return today.strftime('%Y%m%d')


def ticker_info(ticker: str) -> dict:
    """종목 기본 정보 조회"""
    try:
        name = stock.get_market_ticker_name(ticker)
        if not name:
            return {"error": f"종목 '{ticker}'를 찾을 수 없습니다."}

        # 시장 판별
        date = get_latest_trading_date()
        kospi_tickers = stock.get_market_ticker_list(date, market="KOSPI")
        market = "KOSPI" if ticker in kospi_tickers else "KOSDAQ"

        return {
            "ticker": ticker,
            "name": name,
            "market": market,
            "date": date
        }
    except Exception as e:
        return {"error": str(e)}


def get_ohlcv(ticker: str, days: int = 365) -> dict:
    """OHLCV 가격 데이터 조회"""
    try:
        end_date = get_latest_trading_date()
        start_date = (datetime.strptime(end_date, '%Y%m%d') - timedelta(days=days)).strftime('%Y%m%d')

        df = stock.get_market_ohlcv(start_date, end_date, ticker)

        if df.empty:
            return {"error": "가격 데이터 없음", "ticker": ticker}

        # DataFrame을 JSON 직렬화 가능한 형태로 변환
        df = df.reset_index()
        df.columns = ['date', 'open', 'high', 'low', 'close', 'volume', 'change_pct']
        df['date'] = df['date'].dt.strftime('%Y-%m-%d')

        # 기본 통계
        current_price = int(df.iloc[-1]['close'])
        high_52w = int(df['high'].max())
        low_52w = int(df['low'].min())
        avg_volume = int(df['volume'].mean())

        # 이동평균
        ma20 = int(df['close'].tail(20).mean()) if len(df) >= 20 else None
        ma60 = int(df['close'].tail(60).mean()) if len(df) >= 60 else None
        ma120 = int(df['close'].tail(120).mean()) if len(df) >= 120 else None

        return {
            "ticker": ticker,
            "start_date": start_date,
            "end_date": end_date,
            "rows": len(df),
            "current_price": current_price,
            "high_52w": high_52w,
            "low_52w": low_52w,
            "avg_volume": avg_volume,
            "ma20": ma20,
            "ma60": ma60,
            "ma120": ma120,
            "data": df.to_dict(orient='records')
        }
    except Exception as e:
        return {"error": str(e)}


def get_fundamental(ticker: str) -> dict:
    """펀더멘털 지표 조회 (PER, PBR, EPS, BPS, DIV)"""
    try:
        date = get_latest_trading_date()
        df = stock.get_market_fundamental(date, date, ticker)

        if df.empty:
            return {"error": "펀더멘털 데이터 없음", "ticker": ticker, "date": date}

        row = df.iloc[0]
        return {
            "ticker": ticker,
            "date": date,
            "PER": round(float(row.get('PER', 0)), 2) if pd.notna(row.get('PER')) else None,
            "PBR": round(float(row.get('PBR', 0)), 2) if pd.notna(row.get('PBR')) else None,
            "EPS": int(row.get('EPS', 0)) if pd.notna(row.get('EPS')) else None,
            "BPS": int(row.get('BPS', 0)) if pd.notna(row.get('BPS')) else None,
            "DIV": round(float(row.get('DIV', 0)), 2) if pd.notna(row.get('DIV')) else None
        }
    except Exception as e:
        return {"error": str(e)}


def get_market_tickers(market: str = "KOSPI") -> dict:
    """시장 전체 종목 목록 조회"""
    try:
        if market not in ("KOSPI", "KOSDAQ", "ALL"):
            return {"error": f"Invalid market: {market}. Use KOSPI, KOSDAQ, or ALL"}

        date = get_latest_trading_date()

        if market == "ALL":
            kospi = stock.get_market_ticker_list(date, market="KOSPI")
            kosdaq = stock.get_market_ticker_list(date, market="KOSDAQ")
            tickers = [(t, "KOSPI") for t in kospi] + [(t, "KOSDAQ") for t in kosdaq]
        else:
            tickers = [(t, market) for t in stock.get_market_ticker_list(date, market=market)]

        result = []
        for ticker, mkt in tickers:
            name = stock.get_market_ticker_name(ticker)
            result.append({"ticker": ticker, "name": name, "market": mkt})

        return {
            "market": market,
            "date": date,
            "count": len(result),
            "tickers": result
        }
    except Exception as e:
        return {"error": str(e)}


def search_ticker(query: str) -> dict:
    """종목명으로 종목코드 검색"""
    try:
        date = get_latest_trading_date()

        results = []
        for market in ["KOSPI", "KOSDAQ"]:
            tickers = stock.get_market_ticker_list(date, market=market)
            for ticker in tickers:
                name = stock.get_market_ticker_name(ticker)
                if query.lower() in name.lower():
                    results.append({
                        "ticker": ticker,
                        "name": name,
                        "market": market
                    })

        return {
            "query": query,
            "count": len(results),
            "results": results[:20]  # 최대 20개
        }
    except Exception as e:
        return {"error": str(e)}


def get_market_cap(ticker: str) -> dict:
    """시가총액 조회"""
    try:
        date = get_latest_trading_date()

        # 시장 판별
        kospi_tickers = stock.get_market_ticker_list(date, market="KOSPI")
        market = "KOSPI" if ticker in kospi_tickers else "KOSDAQ"

        df = stock.get_market_cap(date, market=market)

        if ticker not in df.index:
            return {"error": f"시가총액 데이터 없음: {ticker}"}

        cap = int(df.loc[ticker, '시가총액'])
        cap_billions = cap // 100000000  # 억원

        # 시장 내 순위
        df_sorted = df.sort_values('시가총액', ascending=False)
        rank = df_sorted.index.get_loc(ticker) + 1
        total = len(df_sorted)
        percentile = round((1 - rank / total) * 100, 1)

        return {
            "ticker": ticker,
            "date": date,
            "market": market,
            "market_cap": cap,
            "market_cap_billions": cap_billions,
            "rank": rank,
            "total": total,
            "percentile": percentile
        }
    except Exception as e:
        return {"error": str(e)}


def main():
    parser = argparse.ArgumentParser(description='quant-k KRX 데이터 유틸리티')
    parser.add_argument('command', choices=[
        'ticker_info', 'ohlcv', 'fundamental',
        'market_tickers', 'search', 'market_cap'
    ])
    parser.add_argument('arg', nargs='?', help='종목코드 또는 검색어')
    parser.add_argument('--days', type=int, default=365, help='OHLCV 조회 일수')
    parser.add_argument('--market', default='KOSPI', help='시장 (KOSPI/KOSDAQ/ALL)')

    args = parser.parse_args()

    if args.command == 'ticker_info':
        if not args.arg:
            print(json.dumps({"error": "종목코드 필요"}))
            return
        result = ticker_info(args.arg)

    elif args.command == 'ohlcv':
        if not args.arg:
            print(json.dumps({"error": "종목코드 필요"}))
            return
        result = get_ohlcv(args.arg, args.days)

    elif args.command == 'fundamental':
        if not args.arg:
            print(json.dumps({"error": "종목코드 필요"}))
            return
        result = get_fundamental(args.arg)

    elif args.command == 'market_tickers':
        result = get_market_tickers(args.arg or args.market)

    elif args.command == 'search':
        if not args.arg:
            print(json.dumps({"error": "검색어 필요"}))
            return
        result = search_ticker(args.arg)

    elif args.command == 'market_cap':
        if not args.arg:
            print(json.dumps({"error": "종목코드 필요"}))
            return
        result = get_market_cap(args.arg)

    else:
        result = {"error": f"Unknown command: {args.command}"}

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
