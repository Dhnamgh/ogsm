"""
OGSM Analytics Service - Thuật toán đếm linh hoạt và chính xác cho Objectives, Goals, Measures.
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

        # 1. Đếm Objectives (Ưu tiên đếm theo ID, nếu trống thì đếm theo cột Nội dung)
        total_objectives = 0
        obj_cols = [c for c in df_calc.columns if any(k in c.lower() for k in ["objective", "mục tiêu"])]
        for col in obj_cols:
            # Forward fill nếu dữ liệu bị trống do gộp ô Excel
            s = df_calc[col].astype(str).str.strip().replace(["nan", "None", "NaN", ""], None).ffill()
            valid_s = s.dropna()
            if not valid_s.empty:
                total_objectives = valid_s.nunique()
                break

        # 2. Đếm Goals / Strategies (Ưu tiên đếm ID, nếu trống đếm theo Nội dung)
        total_goals = 0
        goal_cols = [c for c in df_calc.columns if any(k in c.lower() for k in ["goal", "strategy", "chiến lược", "chỉ tiêu"])]
        for col in goal_cols:
            s = df_calc[col].astype(str).str.strip().replace(["nan", "None", "NaN", ""], None).ffill()
            valid_s = s.dropna()
            if not valid_s.empty:
                total_goals = valid_s.nunique()
                break

        # 3. Đếm Measures / KPIs (Đếm tổng số dòng hoạt động)
        total_measures = len(df_calc)

        # 4. Thống kê tiến độ hoàn thành
        completed_measures = 0
        status_col = None
        for col in df_calc.columns:
            if "status" in col.lower() or "trạng thái" in col.lower():
                status_col = col
                break

        if status_col:
            status_clean = df_calc[status_col].astype(str).str.strip().str.lower()
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

        status_col = None
        for col in df.columns:
            if "status" in col.lower() or "trạng thái" in col.lower():
                status_col = col
                break

        if not status_col:
            return pd.DataFrame(columns=["Status", "Count"])

        counts = df[status_col].dropna().astype(str).str.strip().value_counts().reset_index()
        counts.columns = ["Status", "Count"]
        return counts
