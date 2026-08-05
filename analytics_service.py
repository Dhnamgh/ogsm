"""
OGSM Analytics Service - Thuật toán tính toán chuẩn xác theo đúng cấu trúc file OneDrive.
"""

import pandas as pd
from typing import Dict, Any


class OGSMAnalyticsService:
    @staticmethod
    def compute_summary_kpis(df: pd.DataFrame) -> Dict[str, Any]:
        if df.empty:
            return {
                "total_objectives": 0,
                "total_goals": 0,
                "total_measures": 0,
                "avg_completion_rate": 0.0,
                "completed_measures": 0
            }

        df_calc = df.copy()

        # 1. Đếm Objectives (O)
        total_objectives = 0
        obj_col = next((c for c in df_calc.columns if "objective" in c.lower() or "mục tiêu" in c.lower()), None)
        if obj_col:
            valid_o = df_calc[obj_col].dropna().astype(str).str.strip()
            valid_o = valid_o[~valid_o.isin(["", "nan", "None"])]
            total_objectives = valid_o.nunique()

        # 2. Đếm Goals / Strategies (G)
        total_goals = 0
        goal_col = next((c for c in df_calc.columns if any(k in c.lower() for k in ["goal", "strategy", "chiến lược", "chỉ tiêu"])), None)
        if goal_col:
            valid_g = df_calc[goal_col].dropna().astype(str).str.strip()
            valid_g = valid_g[~valid_g.isin(["", "nan", "None"])]
            total_goals = valid_g.nunique()

        # 3. Đếm Measures / KPIs (M)
        total_measures = len(df_calc)

        # 4. Tính phần trăm hoàn thành
        status_col = next((c for c in df_calc.columns if "status" in c.lower() or "trạng thái" in c.lower() or "tiến độ" in c.lower()), None)
        completed_measures = 0
        if status_col:
            status_clean = df_calc[status_col].dropna().astype(str).str.strip().str.lower()
            completed_measures = len(status_clean[status_clean == "hoàn thành"])

        avg_completion_rate = (completed_measures / total_measures * 100) if total_measures > 0 else 0.0

        return {
            "total_objectives": total_objectives,
            "total_goals": total_goals,
            "total_measures": total_measures,
            "avg_completion_rate": round(avg_completion_rate, 1),
            "completed_measures": completed_measures
        }

    @staticmethod
    def get_status_distribution(df: pd.DataFrame) -> pd.DataFrame:
        if df.empty:
            return pd.DataFrame(columns=["Status", "Count"])

        status_col = next((c for c in df.columns if "status" in c.lower() or "trạng thái" in c.lower() or "tiến độ" in c.lower()), None)
        if not status_col:
            return pd.DataFrame(columns=["Status", "Count"])

        counts = df[status_col].dropna().astype(str).str.strip().value_counts().reset_index()
        counts.columns = ["Status", "Count"]
        return counts
