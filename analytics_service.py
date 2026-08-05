"""
Analytics engine for KPI calculation.
Supports Vietnamese status values from OGSM Excel files.
"""

import pandas as pd
from typing import Dict, Any


class OGSMAnalyticsService:

    @staticmethod
    def compute_summary_kpis(df: pd.DataFrame) -> Dict[str, Any]:
        if df.empty:
            return {
                "total_objectives": 0,
                "total_strategies": 0,
                "total_measures": 0,
                "avg_completion_rate": 0.0,
                "completed_measures": 0,
            }

        # Làm sạch chuỗi trước khi đếm unique (xóa khoảng trắng thừa, chuẩn hóa chữ hoa, bỏ rỗng)
        def clean_unique_count(series: pd.Series) -> int:
            if series is None or series.empty:
                return 0
            cleaned = (
                series.dropna()
                .astype(str)
                .str.strip()
                .str.upper()
            )
            # Loại bỏ các chuỗi rỗng hoặc giá trị nan sau khi strip
            cleaned = cleaned[~cleaned.isin(["", "NAN", "NONE", "NULL"])]
            return cleaned.nunique()

        total_objs = clean_unique_count(df["Objective_ID"]) if "Objective_ID" in df.columns else 0
        
        # Kiểm tra cột Strategy_ID hoặc Goal_ID
        strat_col = "Strategy_ID" if "Strategy_ID" in df.columns else ("Goal_ID" if "Goal_ID" in df.columns else None)
        total_strats = clean_unique_count(df[strat_col]) if strat_col else 0
        
        total_measures = clean_unique_count(df["Measure_ID"]) if "Measure_ID" in df.columns else 0

        # Tính tỷ lệ hoàn thành trung bình
        df_calc = df.copy()
        if "Actual" in df_calc.columns:
            df_calc["Completion"] = pd.to_numeric(df_calc["Actual"], errors="coerce").fillna(0.0).clip(lower=0.0, upper=100.0)
            avg_completion = float(df_calc["Completion"].mean())
        else:
            avg_completion = 0.0

        # Đếm số lượng Hoàn thành
        completed_cnt = 0
        if "Status" in df.columns:
            completed_mask = df["Status"].astype(str).str.strip().str.lower().isin(
                ["hoàn thành", "completed", "đạt"]
            )
            completed_cnt = int(completed_mask.sum())

        return {
            "total_objectives": total_objs,
            "total_strategies": total_strats,
            "total_measures": total_measures,
            "avg_completion_rate": round(avg_completion, 1),
            "completed_measures": completed_cnt,
        }

    @staticmethod
    def get_status_distribution(df: pd.DataFrame) -> pd.DataFrame:
        if df.empty or "Status" not in df.columns:
            return pd.DataFrame(columns=["Status", "Count"])
        
        dist = df["Status"].value_counts().reset_index()
        dist.columns = ["Status", "Count"]
        return dist
