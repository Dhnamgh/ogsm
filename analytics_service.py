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

        total_objs = df["Objective_ID"].nunique()
        total_strats = df["Strategy_ID"].nunique()
        total_measures = df["Measure_ID"].nunique()

        # Tính tỷ lệ hoàn thành trung bình
        targets = df["Target"].replace(0, 100.0)
        df_calc = df.copy()
        
        # Nếu cột Actual đã là tỷ lệ % sẵn thì lấy trực tiếp Actual
        df_calc["Completion"] = df_calc["Actual"].clip(lower=0.0, upper=100.0)
        avg_completion = float(df_calc["Completion"].mean())

        # Đếm số lượng Hoàn thành (hỗ trợ cả tiếng Việt và tiếng Anh)
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
