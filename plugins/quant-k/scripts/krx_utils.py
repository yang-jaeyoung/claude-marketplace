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
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    from pykrx import stock
    import pandas as pd
except ImportError:
    print(json.dumps({"error": "pykrx not installed. Run: pip3 install pykrx pandas"}))
    sys.exit(1)

# 병렬 실행 설정
MAX_WORKERS = 10  # KRX 서버 부하 고려


def _get_ticker_name(ticker: str) -> tuple[str, str]:
    """ticker와 name을 반환하는 헬퍼 (병렬 실행용)"""
    try:
        name = stock.get_market_ticker_name(ticker)
        return (ticker, name or "")
    except:
        return (ticker, "")


def get_latest_trading_date(max_days_back: int = 10) -> str:
    """최근 유효한 거래일 찾기 (데이터가 실제로 있는 날)

    장 개장 전이나 주말/공휴일에는 데이터가 0이므로,
    실제 유효한 데이터가 있는 날짜를 찾습니다.
    """
    today = datetime.now()
    for i in range(max_days_back):
        date = (today - timedelta(days=i)).strftime('%Y%m%d')
        try:
            # 시장 전체 펀더멘털로 확인 (더 빠름)
            df = stock.get_market_fundamental(date, market="KOSPI")
            if not df.empty:
                # 실제 데이터가 있는지 확인 (PER > 0인 종목이 있는지)
                if (df['PER'] > 0).any():
                    return date
        except:
            continue
    # 찾지 못하면 어제 날짜 반환 (폴백)
    return (today - timedelta(days=1)).strftime('%Y%m%d')


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
    """OHLCV 가격 데이터 조회 (최대 1년)"""
    try:
        # 최대 1년(365일)으로 제한
        days = min(days, 365)
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
    """시장 전체 종목 목록 조회 (병렬 실행)"""
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

        # 병렬로 종목명 조회
        result = []
        ticker_to_market = {t: m for t, m in tickers}

        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = {executor.submit(_get_ticker_name, t): t for t, _ in tickers}
            for future in as_completed(futures):
                ticker, name = future.result()
                mkt = ticker_to_market[ticker]
                result.append({"ticker": ticker, "name": name, "market": mkt})

        # ticker 순으로 정렬 (일관성)
        result.sort(key=lambda x: x["ticker"])

        return {
            "market": market,
            "date": date,
            "count": len(result),
            "tickers": result
        }
    except Exception as e:
        return {"error": str(e)}


def search_ticker(query: str) -> dict:
    """종목명으로 종목코드 검색 (병렬 실행)"""
    try:
        date = get_latest_trading_date()

        # 전체 종목 수집
        all_tickers = []
        for market in ["KOSPI", "KOSDAQ"]:
            tickers = stock.get_market_ticker_list(date, market=market)
            all_tickers.extend([(t, market) for t in tickers])

        ticker_to_market = {t: m for t, m in all_tickers}

        # 병렬로 종목명 조회
        results = []
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = {executor.submit(_get_ticker_name, t): t for t, _ in all_tickers}
            for future in as_completed(futures):
                ticker, name = future.result()
                if name and query.lower() in name.lower():
                    results.append({
                        "ticker": ticker,
                        "name": name,
                        "market": ticker_to_market[ticker]
                    })

        # ticker 순으로 정렬
        results.sort(key=lambda x: x["ticker"])

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


def screen_market(market: str = "KOSPI", min_cap_billions: int = 0, max_results: int = 50) -> dict:
    """시장 전체 종목 스크리닝 (펀더멘털 + 모멘텀 포함, 병렬 실행)"""
    try:
        date = get_latest_trading_date()

        # 종목 목록
        tickers = stock.get_market_ticker_list(date, market=market)

        # 시가총액 데이터 (전체 시장)
        cap_df = stock.get_market_cap(date, market=market)

        # 펀더멘털 데이터 (전체 시장)
        fund_df = stock.get_market_fundamental(date, market=market)

        # 3개월 전 날짜
        date_3m = (datetime.strptime(date, '%Y%m%d') - timedelta(days=90)).strftime('%Y%m%d')

        def get_stock_data(ticker: str) -> dict:
            """개별 종목 데이터 수집"""
            try:
                name = stock.get_market_ticker_name(ticker)

                # 시가총액
                if ticker not in cap_df.index:
                    return None
                cap = int(cap_df.loc[ticker, '시가총액']) // 100000000  # 억원

                # 시총 필터
                if cap < min_cap_billions:
                    return None

                # 펀더멘털
                if ticker not in fund_df.index:
                    return None
                per = float(fund_df.loc[ticker, 'PER']) if pd.notna(fund_df.loc[ticker, 'PER']) else None
                pbr = float(fund_df.loc[ticker, 'PBR']) if pd.notna(fund_df.loc[ticker, 'PBR']) else None
                div = float(fund_df.loc[ticker, 'DIV']) if pd.notna(fund_df.loc[ticker, 'DIV']) else None

                # 모멘텀 계산 (3개월 수익률)
                try:
                    ohlcv = stock.get_market_ohlcv(date_3m, date, ticker)
                    if not ohlcv.empty and len(ohlcv) >= 2:
                        price_now = ohlcv.iloc[-1]['종가']
                        price_3m = ohlcv.iloc[0]['종가']
                        momentum_3m = round((price_now - price_3m) / price_3m * 100, 2) if price_3m > 0 else None
                    else:
                        momentum_3m = None
                except:
                    momentum_3m = None

                return {
                    "ticker": ticker,
                    "name": name,
                    "market_cap_billions": cap,
                    "per": round(per, 2) if per else None,
                    "pbr": round(pbr, 2) if pbr else None,
                    "div": round(div, 2) if div else None,
                    "momentum_3m": momentum_3m
                }
            except:
                return None

        # 병렬로 종목 데이터 수집
        results = []
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = {executor.submit(get_stock_data, t): t for t in tickers}
            for future in as_completed(futures):
                data = future.result()
                if data:
                    results.append(data)

        # 시총 순 정렬
        results.sort(key=lambda x: x["market_cap_billions"], reverse=True)

        return {
            "market": market,
            "date": date,
            "total": len(results),
            "results": results[:max_results]
        }
    except Exception as e:
        return {"error": str(e)}


def collect_all(ticker: str, days: int = 365) -> dict:
    """Phase 1: 모든 데이터를 병렬로 수집 (ohlcv, fundamental, market_cap)"""
    try:
        with ThreadPoolExecutor(max_workers=3) as executor:
            future_ohlcv = executor.submit(get_ohlcv, ticker, days)
            future_fund = executor.submit(get_fundamental, ticker)
            future_cap = executor.submit(get_market_cap, ticker)

            ohlcv_result = future_ohlcv.result()
            fund_result = future_fund.result()
            cap_result = future_cap.result()

        return {
            "ticker": ticker,
            "ohlcv": ohlcv_result,
            "fundamental": fund_result,
            "market_cap": cap_result
        }
    except Exception as e:
        return {"error": str(e)}


def main():
    parser = argparse.ArgumentParser(description='quant-k KRX 데이터 유틸리티')
    parser.add_argument('command', choices=[
        'ticker_info', 'ohlcv', 'fundamental',
        'market_tickers', 'search', 'market_cap', 'collect_all', 'screen_market'
    ])
    parser.add_argument('arg', nargs='?', help='종목코드 또는 검색어')
    parser.add_argument('--days', type=int, default=365, help='OHLCV 조회 일수 (최대 365)')
    parser.add_argument('--market', default='KOSPI', help='시장 (KOSPI/KOSDAQ/ALL)')
    parser.add_argument('--min-cap', type=int, default=0, help='최소 시가총액 (억원)')
    parser.add_argument('--max-results', type=int, default=50, help='최대 결과 수')

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

    elif args.command == 'collect_all':
        if not args.arg:
            print(json.dumps({"error": "종목코드 필요"}))
            return
        result = collect_all(args.arg, args.days)

    elif args.command == 'screen_market':
        result = screen_market(args.arg or args.market, args.min_cap, args.max_results)

    else:
        result = {"error": f"Unknown command: {args.command}"}

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
