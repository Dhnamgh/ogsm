"""
OGSM Analytics Service - Thuật toán đếm và thống kê chỉ số OGSM chuẩn xác.
"""

import pandas as pd
from typing import Dict, Any


class OGSMAnalyticsService:
    @staticmethod
    def compute_summary_kpis(df: pd.DataFrame) -> Dict[str, Any]:
        if df is None or df.empty:
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
        for col in df_calc.columns:
            if any(k in str(col).lower() for k in ["objective", "mục tiêu chiến lược", "mã o", "stt_o"]):
                valid_o = df_calc[col].dropna().astype(str).str.strip()
                valid_o = valid_o[~valid_o.isin(["", "nan", "None", "NaN"])]
                if not valid_o.empty:
                    total_objectives = valid_o.nunique()
                    break

        # 2. Đếm Goals / Strategies (G)
        total_goals = 0
        for col in df_calc.columns:
            if any(k in str(col).lower() for k in ["goal", "strategy", "mục tiêu cụ thể", "chiến lược", "mã g", "stt_g"]):
                valid_g = df_calc[col].dropna().astype(str).str.strip()
                valid_g = valid_g[~valid_g.isin(["", "nan", "None", "NaN"])]
                if not valid_g.empty:
                    total_goals = valid_g.nunique()
                    break

        # 3. Đếm Measures / KPIs (M)
        total_measures = len(df_calc)

        # 4. Thống kê tiến độ hoàn thành
        completed_measures = 0
        if "Status" in df_calc.columns:
            status_clean = df_calc["Status"].dropna().astype(str).str.strip().str.lower()
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
        if df is None or df.empty or "Status" not in df.columns:
            return pd.DataFrame(columns=["Status", "Count"])

        counts = df["Status"].dropna().astype(str).str.strip().value_counts().reset_index()
        counts.columns = ["Status", "Count"]
        return counts
