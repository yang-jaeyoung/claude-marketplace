#!/usr/bin/env python3
"""스크리닝 엔진 with DSL Parser"""
import re
import json
import os
from typing import Dict, List, Any, Tuple, Optional
from base_bridge import BaseBridge, JsonRpcError
from pykrx import stock
import pandas as pd
from datetime import datetime

CACHE_DIR = ".omc/quant-k/data"
SCREENS_DIR = ".omc/quant-k/screens"


class DSLParser:
    """스크리닝 조건 DSL 파서"""

    # 한글 팩터명 매핑
    FACTOR_ALIASES = {
        "시총": "MARKET_CAP",
        "시가총액": "MARKET_CAP",
        "배당률": "DIV",
        "배당수익률": "DIV",
        "자기자본이익률": "ROE",
    }

    # 연산자 패턴
    OPERATORS = {
        "<=": lambda a, b: a <= b,
        ">=": lambda a, b: a >= b,
        "<": lambda a, b: a < b,
        ">": lambda a, b: a > b,
        "==": lambda a, b: a == b,
        "!=": lambda a, b: a != b,
    }

    # 단위 변환
    UNIT_MULTIPLIERS = {
        "조": 1_000_000_000_000,
        "억": 100_000_000,
        "만": 10_000,
        "%": 1,  # 퍼센트는 그대로
    }

    @classmethod
    def parse_condition(cls, condition: str) -> Tuple[str, str, float]:
        """
        조건 문자열을 파싱

        Args:
            condition: "PER<10" 또는 "시총>1조"

        Returns:
            (factor, operator, value) 튜플
        """
        condition = condition.strip()

        # 연산자 찾기 (긴 것부터)
        operator = None
        for op in ["<=", ">=", "==", "!=", "<", ">"]:
            if op in condition:
                operator = op
                break

        if not operator:
            raise JsonRpcError(1301, f"No operator found in condition: {condition}")

        parts = condition.split(operator)
        if len(parts) != 2:
            raise JsonRpcError(1301, f"Invalid condition format: {condition}")

        factor_raw = parts[0].strip()
        value_raw = parts[1].strip()

        # 팩터명 변환
        factor = cls.FACTOR_ALIASES.get(factor_raw, factor_raw)

        # 값 파싱 (단위 처리)
        value = cls._parse_value(value_raw)

        return factor, operator, value

    @classmethod
    def _parse_value(cls, value_str: str) -> float:
        """값 문자열을 숫자로 변환 (단위 처리)"""
        value_str = value_str.strip()

        # 단위 확인
        for unit, multiplier in cls.UNIT_MULTIPLIERS.items():
            if value_str.endswith(unit):
                number_part = value_str[:-len(unit)]
                try:
                    return float(number_part) * multiplier
                except ValueError:
                    raise JsonRpcError(1301, f"Invalid number: {number_part}")

        # 단위 없는 경우
        try:
            return float(value_str)
        except ValueError:
            raise JsonRpcError(1301, f"Invalid value: {value_str}")


class ScreenerBridge(BaseBridge):
    """종목 스크리닝 엔진"""

    def __init__(self):
        super().__init__(19003)

        self.register_method("screen", self.screen)
        self.register_method("save_screen", self.save_screen)
        self.register_method("load_screen", self.load_screen)
        self.register_method("list_screens", self.list_screens)
        self.register_method("parse_conditions", self.parse_conditions)

    def _get_market_data(self, market: str, date: str) -> pd.DataFrame:
        """시장 데이터 수집 (PER, PBR, 시총 등)"""
        # 기본 지표
        fundamental = stock.get_market_fundamental(date, market=market)

        # 시가총액
        cap = stock.get_market_cap(date, market=market)

        # 병합
        df = fundamental.join(cap[["시가총액"]], how="inner")
        df = df.rename(columns={"시가총액": "MARKET_CAP"})

        # ROE 계산 (EPS / BPS) * 100
        # ROE = (EPS / BPS) * 100, only where BPS > 0
        valid_mask = (df["BPS"] > 0) & (df["EPS"].notna())
        df["ROE"] = pd.Series(index=df.index, dtype=float)
        df.loc[valid_mask, "ROE"] = (df.loc[valid_mask, "EPS"] / df.loc[valid_mask, "BPS"]) * 100

        # 종목명 추가
        names = {}
        for ticker in df.index:
            try:
                names[ticker] = stock.get_market_ticker_name(ticker)
            except:
                names[ticker] = ticker
        df["name"] = pd.Series(names)

        return df

    def _apply_condition(self, df: pd.DataFrame, factor: str, operator: str, value: float) -> pd.DataFrame:
        """단일 조건 적용"""
        if factor not in df.columns:
            raise JsonRpcError(1201, f"Unknown factor: {factor}. Available: {list(df.columns)}")

        op_func = DSLParser.OPERATORS.get(operator)
        if not op_func:
            raise JsonRpcError(1301, f"Unknown operator: {operator}")

        mask = op_func(df[factor], value)
        return df[mask]

    def screen(self, params: Dict) -> Dict:
        """
        조건 기반 스크리닝

        Args:
            conditions: ["PER<10", "ROE>15", ...]
            market: "KOSPI" | "KOSDAQ" | "ALL"
            date: 기준일 (YYYYMMDD)
            sort_by: 정렬 기준 팩터
            sort_order: "asc" | "desc"
            limit: 최대 결과 수
            load: 저장된 조건명
        """
        conditions = params.get("conditions", [])
        market = params.get("market", "KOSPI")
        date = params.get("date", datetime.now().strftime("%Y%m%d"))
        sort_by = params.get("sort_by")
        sort_order = params.get("sort_order", "desc")
        limit = params.get("limit", 100)
        load_name = params.get("load")
        save_name = params.get("save")

        # 저장된 조건 로드
        if load_name:
            loaded = self.load_screen({"name": load_name})
            conditions = loaded.get("conditions", [])
            if not conditions:
                raise JsonRpcError(1301, f"No conditions found in screen: {load_name}")

        if not conditions:
            raise JsonRpcError(1301, "At least one condition required")

        # 시장 데이터 수집
        if market == "ALL":
            df_kospi = self._get_market_data("KOSPI", date)
            df_kosdaq = self._get_market_data("KOSDAQ", date)
            df = pd.concat([df_kospi, df_kosdaq])
        else:
            if market not in ("KOSPI", "KOSDAQ"):
                raise JsonRpcError(1101, f"Invalid market: {market}")
            df = self._get_market_data(market, date)

        total_count = len(df)

        # 조건 적용
        parsed_conditions = []
        for cond in conditions:
            factor, operator, value = DSLParser.parse_condition(cond)
            parsed_conditions.append({"factor": factor, "operator": operator, "value": value})
            df = self._apply_condition(df, factor, operator, value)

        # 정렬
        if sort_by and sort_by in df.columns:
            ascending = sort_order == "asc"
            df = df.sort_values(by=sort_by, ascending=ascending)

        # 제한
        df = df.head(limit)

        # 결과 포맷
        results = []
        for ticker in df.index:
            row = df.loc[ticker]
            values = {}
            for col in df.columns:
                if col != "name":
                    val = row[col]
                    if pd.notna(val):
                        if isinstance(val, (int, float)):
                            values[col] = round(float(val), 2) if isinstance(val, float) else int(val)
                        else:
                            values[col] = str(val)

            results.append({
                "ticker": ticker,
                "name": row.get("name", ticker),
                "values": values
            })

        # 조건 저장
        if save_name:
            self.save_screen({"name": save_name, "conditions": conditions})

        return {
            "conditions": conditions,
            "parsed": parsed_conditions,
            "market": market,
            "date": date,
            "matchCount": len(results),
            "totalCount": total_count,
            "results": results,
            "savedAs": save_name
        }

    def save_screen(self, params: Dict) -> Dict:
        """스크리닝 조건 저장"""
        name = params.get("name")
        conditions = params.get("conditions", [])

        if not name:
            raise JsonRpcError(1301, "Screen name required")

        os.makedirs(SCREENS_DIR, exist_ok=True)
        path = f"{SCREENS_DIR}/{name}.json"

        with open(path, "w", encoding="utf-8") as f:
            json.dump({"name": name, "conditions": conditions, "created": datetime.now().isoformat()}, f, ensure_ascii=False, indent=2)

        return {"saved": True, "name": name, "path": path}

    def load_screen(self, params: Dict) -> Dict:
        """저장된 스크리닝 조건 로드"""
        name = params.get("name")

        if not name:
            raise JsonRpcError(1301, "Screen name required")

        path = f"{SCREENS_DIR}/{name}.json"

        if not os.path.exists(path):
            raise JsonRpcError(1301, f"Screen not found: {name}")

        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def list_screens(self, params: Dict) -> Dict:
        """저장된 스크리닝 목록"""
        if not os.path.exists(SCREENS_DIR):
            return {"screens": []}

        screens = []
        for filename in os.listdir(SCREENS_DIR):
            if filename.endswith(".json"):
                name = filename[:-5]
                screens.append(name)

        return {"screens": screens}

    def parse_conditions(self, params: Dict) -> Dict:
        """조건 파싱 테스트"""
        conditions = params.get("conditions", [])

        parsed = []
        for cond in conditions:
            factor, operator, value = DSLParser.parse_condition(cond)
            parsed.append({
                "original": cond,
                "factor": factor,
                "operator": operator,
                "value": value
            })

        return {"parsed": parsed}


if __name__ == "__main__":
    bridge = ScreenerBridge()
    bridge.run()
