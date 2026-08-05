"""
OGSM Analytics Service - Thuật toán đếm linh hoạt các chỉ số OGSM.
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

        # 1. Thuật toán đếm Objectives an toàn
        total_objectives = 0
        for col in ["Objective_ID", "Objective_ID_1"]:
            if col in df.columns:
                valid_objs = df[col].dropna().astype(str).str.strip()
                valid_objs = valid_objs[valid_objs != ""]
                if not valid_objs.empty:
                    total_objectives = valid_objs.nunique()
                    break

        # 2. Thuật toán đếm Goals / Strategies an toàn
        total_goals = 0
        for col in ["Goal_ID", "Goal_ID_1", "Strategy_ID"]:
            if col in df.columns:
                valid_goals = df[col].dropna().astype(str).str.strip()
                valid_goals = valid_goals[valid_goals != ""]
                if not valid_goals.empty:
                    total_goals = valid_goals.nunique()
                    break

        # 3. Đếm tổng số Measures (KPIs)
        meas_col = "Measure_ID" if "Measure_ID" in df.columns else df.columns[0]
        valid_meas = df[meas_col].dropna().astype(str).str.strip()
        total_measures = len(valid_meas[valid_meas != ""])
        if total_measures == 0:
            total_measures = len(df)

        # 4. Thống kê tiến độ hoàn thành
        completed_measures = 0
        if "Status" in df.columns:
            status_clean = df["Status"].dropna().astype(str).str.strip().str.lower()
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
        if df.empty or "Status" not in df.columns:
            return pd.DataFrame(columns=["Status", "Count"])

        counts = df["Status"].dropna().astype(str).str.strip().value_counts().reset_index()
        counts.columns = ["Status", "Count"]
        return counts
