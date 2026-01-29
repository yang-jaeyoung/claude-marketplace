#!/usr/bin/env python3
"""팩터 계산 엔진 (배치 캐싱 방식)"""
import numpy as np
import pandas as pd
from typing import Dict, List, Any
from base_bridge import BaseBridge, JsonRpcError
from pykrx import stock
import os
from datetime import datetime

CACHE_DIR = ".omc/quant-k/data/factors"


class FactorBridge(BaseBridge):
    """팩터 계산 엔진 (배치 캐싱 방식)"""

    FACTOR_DEFINITIONS = {
        # Value Factors (낮을수록 좋음 → 역수 취해서 높을수록 좋음)
        "PER": "value",
        "PBR": "value",
        "PSR": "value",
        "PCR": "value",
        "EV_EBITDA": "value",

        # Momentum Factors (높을수록 좋음)
        "MOM_1M": "momentum",
        "MOM_3M": "momentum",
        "MOM_6M": "momentum",
        "MOM_12M": "momentum",

        # Profitability Factors (높을수록 좋음)
        "ROE": "profitability",
        "ROA": "profitability",
        "GP_MARGIN": "profitability",
        "OP_MARGIN": "profitability",

        # Size Factors
        "SIZE": "size",
        "SIZE_INV": "size",

        # Volatility
        "VOL_20D": "volatility",
    }

    def __init__(self):
        super().__init__(19002)

        self.register_method("calculate_factor", self.calculate_factor)
        self.register_method("calculate_composite", self.calculate_composite)
        self.register_method("rank_by_factor", self.rank_by_factor)
        self.register_method("get_factor_exposure", self.get_factor_exposure)
        self.register_method("list_factors", self.list_factors)
        self.register_method("refresh_cache", self.refresh_cache)

    def list_factors(self, params: Dict) -> Dict:
        """지원 팩터 목록 반환"""
        return {
            "factors": list(self.FACTOR_DEFINITIONS.keys()),
            "categories": {
                "value": ["PER", "PBR", "PSR", "PCR", "EV_EBITDA"],
                "momentum": ["MOM_1M", "MOM_3M", "MOM_6M", "MOM_12M"],
                "profitability": ["ROE", "ROA", "GP_MARGIN", "OP_MARGIN"],
                "size": ["SIZE", "SIZE_INV"],
                "volatility": ["VOL_20D"],
            }
        }

    def _get_cache_path(self, factor: str, market: str, date: str) -> str:
        """캐시 파일 경로 생성"""
        return f"{CACHE_DIR}/{factor}_{market}_{date}.parquet"

    def _is_cache_valid(self, cache_path: str) -> bool:
        """캐시 유효성 확인 (24시간)"""
        if not os.path.exists(cache_path):
            return False

        mtime = os.path.getmtime(cache_path)
        age_hours = (datetime.now().timestamp() - mtime) / 3600
        return age_hours < 24

    def _calculate_value_factor(self, factor: str, market: str, date: str) -> pd.DataFrame:
        """Value 팩터 계산 (PER, PBR)"""
        df = stock.get_market_fundamental(date, market=market)

        if df.empty:
            raise JsonRpcError(1004, f"No data available for {market} on {date}")

        if factor not in df.columns:
            raise JsonRpcError(1201, f"Factor {factor} not available in fundamental data")

        # 낮을수록 좋음 → 역수 취함 (0 및 음수 처리)
        values = df[factor].replace(0, np.nan)
        values = values.apply(lambda x: x if x > 0 else np.nan)
        scores = 1 / values

        result = pd.DataFrame({
            "ticker": df.index,
            "raw_value": df[factor],
            "score": self._zscore(scores)
        })

        return result.dropna()

    def _calculate_momentum_factor(self, factor: str, market: str, date: str) -> pd.DataFrame:
        """Momentum 팩터 계산"""
        period_map = {
            "MOM_1M": 20,
            "MOM_3M": 60,
            "MOM_6M": 120,
            "MOM_12M": 240
        }

        period = period_map.get(factor)
        if not period:
            raise JsonRpcError(1201, f"Unknown momentum factor: {factor}")

        # 전체 종목 가격 데이터 수집
        tickers = stock.get_market_ticker_list(date, market=market)
        start_date = (datetime.strptime(date, "%Y%m%d") -
                     pd.Timedelta(days=period * 2)).strftime("%Y%m%d")

        momentum_scores = []
        for ticker in tickers[:100]:  # MVP: 상위 100개만
            try:
                ohlcv = stock.get_market_ohlcv(start_date, date, ticker)
                if len(ohlcv) >= period:
                    returns = (ohlcv["종가"].iloc[-1] / ohlcv["종가"].iloc[-period] - 1) * 100
                    momentum_scores.append({"ticker": ticker, "raw_value": returns})
            except:
                continue

        if not momentum_scores:
            raise JsonRpcError(1004, "No momentum data available")

        df = pd.DataFrame(momentum_scores)
        df["score"] = self._zscore(df["raw_value"])

        return df

    def _calculate_profitability_factor(self, factor: str, market: str, date: str) -> pd.DataFrame:
        """Profitability 팩터 계산 (ROE, ROA, GP_MARGIN, OP_MARGIN)"""
        df = stock.get_market_fundamental(date, market=market)

        if df.empty:
            raise JsonRpcError(1004, f"No data available for {market} on {date}")

        # ROE 계산: EPS / BPS
        if factor == "ROE":
            if "EPS" not in df.columns or "BPS" not in df.columns:
                raise JsonRpcError(1201, "EPS or BPS not available for ROE calculation")

            # BPS가 0이거나 음수인 경우 제외
            valid_mask = (df["BPS"] > 0) & (df["EPS"].notna())
            roe_values = pd.Series(index=df.index, dtype=float)
            roe_values[valid_mask] = (df.loc[valid_mask, "EPS"] / df.loc[valid_mask, "BPS"]) * 100

            result = pd.DataFrame({
                "ticker": df.index,
                "raw_value": roe_values,
                "score": self._zscore(roe_values)
            })

            return result.dropna()

        # ROA, GP_MARGIN, OP_MARGIN은 아직 구현되지 않음
        elif factor in ["ROA", "GP_MARGIN", "OP_MARGIN"]:
            raise JsonRpcError(1201, f"Factor {factor} is not yet fully implemented. Currently only ROE is supported for profitability factors.")

        else:
            raise JsonRpcError(1201, f"Unknown profitability factor: {factor}")

    def _zscore(self, series: pd.Series) -> pd.Series:
        """Z-score 정규화 with Winsorization"""
        if series.isna().all():
            return series

        # Winsorization (1%, 99%)
        lower = series.quantile(0.01)
        upper = series.quantile(0.99)
        clipped = series.clip(lower, upper)

        mean = clipped.mean()
        std = clipped.std()

        if std == 0 or pd.isna(std):
            return pd.Series([0.0] * len(series))

        return (clipped - mean) / std

    def calculate_factor(self, params: Dict) -> Dict:
        """단일 팩터 계산 (배치 캐싱)"""
        factor = params.get("factor")
        market = params.get("market", "KOSPI")
        date = params.get("date", datetime.now().strftime("%Y%m%d"))
        refresh = params.get("refresh", False)

        if factor not in self.FACTOR_DEFINITIONS:
            raise JsonRpcError(1201, f"Unknown factor: {factor}. Supported: {list(self.FACTOR_DEFINITIONS.keys())}")

        if market not in ("KOSPI", "KOSDAQ"):
            raise JsonRpcError(1101, f"Invalid market: {market}")

        cache_path = self._get_cache_path(factor, market, date)

        # 캐시 확인
        if not refresh and self._is_cache_valid(cache_path):
            df = pd.read_parquet(cache_path)
            return {
                "factor": factor,
                "date": date,
                "market": market,
                "scores": df.set_index("ticker")["score"].to_dict(),
                "cached": True,
                "count": len(df)
            }

        # 팩터 계산
        category = self.FACTOR_DEFINITIONS[factor]

        if category == "value":
            df = self._calculate_value_factor(factor, market, date)
        elif category == "momentum":
            df = self._calculate_momentum_factor(factor, market, date)
        elif category == "profitability":
            df = self._calculate_profitability_factor(factor, market, date)
        else:
            raise JsonRpcError(1201, f"Factor category {category} not yet implemented")

        # 캐시 저장
        os.makedirs(os.path.dirname(cache_path), exist_ok=True)
        df.to_parquet(cache_path)

        return {
            "factor": factor,
            "date": date,
            "market": market,
            "scores": df.set_index("ticker")["score"].to_dict(),
            "cached": False,
            "count": len(df)
        }

    def calculate_composite(self, params: Dict) -> Dict:
        """복합 팩터 계산 (가중 평균)"""
        factors = params.get("factors", [])
        weights = params.get("weights", {})
        market = params.get("market", "KOSPI")
        date = params.get("date", datetime.now().strftime("%Y%m%d"))

        if not factors:
            raise JsonRpcError(1201, "At least one factor required")

        # 가중치 정규화
        if not weights:
            weights = {f: 1.0 / len(factors) for f in factors}

        total_weight = sum(weights.values())
        weights = {k: v / total_weight for k, v in weights.items()}

        # 각 팩터 점수 수집
        all_scores = {}
        for factor in factors:
            result = self.calculate_factor({
                "factor": factor,
                "market": market,
                "date": date
            })
            for ticker, score in result["scores"].items():
                if ticker not in all_scores:
                    all_scores[ticker] = {}
                all_scores[ticker][factor] = score

        # 복합 점수 계산
        composite_scores = {}
        for ticker, scores in all_scores.items():
            if len(scores) == len(factors):
                composite = sum(scores[f] * weights[f] for f in factors)
                composite_scores[ticker] = composite

        return {
            "factors": factors,
            "weights": weights,
            "date": date,
            "market": market,
            "composite_scores": composite_scores,
            "count": len(composite_scores)
        }

    def rank_by_factor(self, params: Dict) -> Dict:
        """팩터 기준 순위"""
        factor = params.get("factor")
        market = params.get("market", "KOSPI")
        date = params.get("date", datetime.now().strftime("%Y%m%d"))
        top_n = params.get("top_n", 20)

        result = self.calculate_factor({
            "factor": factor,
            "market": market,
            "date": date
        })

        scores = result["scores"]
        sorted_items = sorted(scores.items(), key=lambda x: x[1], reverse=True)

        rankings = []
        for rank, (ticker, score) in enumerate(sorted_items[:top_n], 1):
            try:
                name = stock.get_market_ticker_name(ticker)
            except:
                name = ticker

            rankings.append({
                "rank": rank,
                "ticker": ticker,
                "name": name,
                "score": round(score, 4)
            })

        return {
            "factor": factor,
            "date": date,
            "market": market,
            "rankings": rankings
        }

    def get_factor_exposure(self, params: Dict) -> Dict:
        """특정 종목의 팩터 노출도"""
        ticker = params.get("ticker")
        factors = params.get("factors", list(self.FACTOR_DEFINITIONS.keys()))
        date = params.get("date", datetime.now().strftime("%Y%m%d"))

        if not ticker:
            raise JsonRpcError(1002, "ticker is required")

        exposures = {}
        for factor in factors:
            try:
                result = self.calculate_factor({
                    "factor": factor,
                    "market": "KOSPI",
                    "date": date
                })
                if ticker in result["scores"]:
                    exposures[factor] = round(result["scores"][ticker], 4)
            except:
                continue

        return {
            "ticker": ticker,
            "date": date,
            "exposures": exposures
        }

    def refresh_cache(self, params: Dict) -> Dict:
        """캐시 갱신 (배치)"""
        market = params.get("market", "KOSPI")
        date = params.get("date", datetime.now().strftime("%Y%m%d"))
        factors = params.get("factors", list(self.FACTOR_DEFINITIONS.keys()))

        refreshed = []
        for factor in factors:
            try:
                self.calculate_factor({
                    "factor": factor,
                    "market": market,
                    "date": date,
                    "refresh": True
                })
                refreshed.append(factor)
            except:
                continue

        return {
            "market": market,
            "date": date,
            "refreshed": refreshed,
            "count": len(refreshed)
        }


if __name__ == "__main__":
    bridge = FactorBridge()
    bridge.run()
