#!/usr/bin/env python3
"""pykrx API 래퍼 브릿지"""
from base_bridge import BaseBridge, JsonRpcError
from pykrx import stock
import pandas as pd
import os
from datetime import datetime
from typing import Dict, Any

CACHE_DIR = ".omc/krx-quant/data"


class KrxBridge(BaseBridge):
    """pykrx API 래퍼 브릿지"""

    def __init__(self):
        super().__init__("/tmp/krx-quant-bridge.sock")

        # 메서드 등록
        self.register_method("get_ticker_list", self.get_ticker_list)
        self.register_method("get_ohlcv", self.get_ohlcv)
        self.register_method("get_fundamental", self.get_fundamental)
        self.register_method("get_market_cap", self.get_market_cap)

    def get_ticker_list(self, params: Dict) -> Dict:
        """
        종목 목록 조회
        Args:
            market: "KOSPI" | "KOSDAQ"
        Returns:
            {"tickers": [{"ticker": "005930", "name": "삼성전자", "market": "KOSPI"}, ...]}
        """
        market = params.get("market", "KOSPI")

        if market not in ("KOSPI", "KOSDAQ"):
            raise JsonRpcError(1101, f"Invalid market: {market}. Supported: KOSPI, KOSDAQ")

        try:
            date = datetime.now().strftime("%Y%m%d")
            tickers = stock.get_market_ticker_list(date, market=market)

            result = []
            for ticker in tickers:
                name = stock.get_market_ticker_name(ticker)
                result.append({
                    "ticker": ticker,
                    "name": name,
                    "market": market
                })

            return {"tickers": result, "count": len(result), "date": date}

        except Exception as e:
            raise JsonRpcError(1001, f"pykrx API error: {str(e)}")

    def get_ohlcv(self, params: Dict) -> Dict:
        """
        OHLCV 가격 데이터 조회
        Args:
            ticker: 종목 코드 (예: "005930")
            start: 시작일 (YYYYMMDD)
            end: 종료일 (YYYYMMDD)
            freq: "d" (일봉) | "w" (주봉) | "m" (월봉)
        Returns:
            {"ticker": str, "data": list, "cached": bool, "rows": int}
        """
        ticker = params.get("ticker")
        start = params.get("start")
        end = params.get("end")
        freq = params.get("freq", "d")

        if not ticker:
            raise JsonRpcError(1002, "ticker is required")
        if not start or not end:
            raise JsonRpcError(1003, "start and end dates are required (YYYYMMDD)")

        # 날짜 형식 검증
        try:
            datetime.strptime(start, "%Y%m%d")
            datetime.strptime(end, "%Y%m%d")
        except ValueError:
            raise JsonRpcError(1003, "Invalid date format. Use YYYYMMDD")

        # 캐시 확인
        cache_path = f"{CACHE_DIR}/prices/{ticker}_{start}_{end}.parquet"
        if os.path.exists(cache_path):
            df = pd.read_parquet(cache_path)
            return {
                "ticker": ticker,
                "data": df.to_dict(orient="records"),
                "cached": True,
                "rows": len(df)
            }

        try:
            df = stock.get_market_ohlcv(start, end, ticker, freq=freq)

            if df.empty:
                return {
                    "ticker": ticker,
                    "data": [],
                    "cached": False,
                    "rows": 0
                }

            # 인덱스를 컬럼으로 변환
            df = df.reset_index()
            df.columns = ["date", "open", "high", "low", "close", "volume", "value", "change"]
            df["date"] = df["date"].dt.strftime("%Y%m%d")

            # 캐시 저장 (과거 데이터만)
            today = datetime.now().strftime("%Y%m%d")
            if end < today:
                os.makedirs(os.path.dirname(cache_path), exist_ok=True)
                df.to_parquet(cache_path)

            return {
                "ticker": ticker,
                "data": df.to_dict(orient="records"),
                "cached": False,
                "rows": len(df)
            }

        except Exception as e:
            raise JsonRpcError(1001, f"pykrx API error: {str(e)}")

    def get_fundamental(self, params: Dict) -> Dict:
        """
        재무 지표 조회 (PER, PBR, 배당수익률)
        """
        ticker = params.get("ticker")
        date = params.get("date")

        if not ticker:
            raise JsonRpcError(1002, "ticker is required")
        if not date:
            date = datetime.now().strftime("%Y%m%d")

        try:
            df = stock.get_market_fundamental(date, date, ticker)

            if df.empty:
                return {"ticker": ticker, "date": date, "data": None}

            row = df.iloc[0]
            return {
                "ticker": ticker,
                "date": date,
                "data": {
                    "PER": float(row.get("PER", 0)) if pd.notna(row.get("PER")) else 0,
                    "PBR": float(row.get("PBR", 0)) if pd.notna(row.get("PBR")) else 0,
                    "DIV": float(row.get("DIV", 0)) if pd.notna(row.get("DIV")) else 0,
                    "EPS": float(row.get("EPS", 0)) if pd.notna(row.get("EPS")) else 0,
                    "BPS": float(row.get("BPS", 0)) if pd.notna(row.get("BPS")) else 0
                }
            }

        except Exception as e:
            raise JsonRpcError(1001, f"pykrx API error: {str(e)}")

    def get_market_cap(self, params: Dict) -> Dict:
        """
        시가총액 조회
        """
        market = params.get("market", "KOSPI")
        date = params.get("date")

        if market not in ("KOSPI", "KOSDAQ"):
            raise JsonRpcError(1101, f"Invalid market: {market}")

        if not date:
            date = datetime.now().strftime("%Y%m%d")

        try:
            df = stock.get_market_cap(date, market=market)

            # 시가총액을 억원 단위로 변환
            cap_data = {}
            for ticker in df.index:
                cap_data[ticker] = int(df.loc[ticker, "시가총액"] / 100000000)  # 억원

            return {
                "market": market,
                "date": date,
                "data": cap_data,
                "count": len(df)
            }

        except Exception as e:
            raise JsonRpcError(1001, f"pykrx API error: {str(e)}")


if __name__ == "__main__":
    bridge = KrxBridge()
    bridge.run()
