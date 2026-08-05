"""
OGSM Analytics Service - Tính toán các chỉ số KPI, tỷ lệ hoàn thành và phân bố trạng thái.
Bao gồm bẫy lỗi an toàn cho các cột Goal_ID / Strategy_ID.
"""

import pandas as pd
from typing import Dict, Any


class OGSMAnalyticsService:
    @staticmethod
    def compute_summary_kpis(df: pd.DataFrame) -> Dict[str, Any]:
        """Tính toán tổng số Objectives, Goals/Strategies, Measures và % Hoàn thành."""
        if df.empty:
            return {
                "total_objectives": 0,
                "total_goals": 0,
                "total_measures": 0,
                "avg_completion_rate": 0.0,
                "completed_measures": 0
            }

        # 1. Đếm số Objectives
        obj_col = "Objective_ID" if "Objective_ID" in df.columns else df.columns[0]
        total_objectives = df[obj_col].dropna().astype(str).str.strip().nunique()

        # 2. Đếm số Goals / Strategies an toàn
        total_goals = 0
        for g_col in ["Goal_ID", "Strategy_ID", "Goal_ID_1"]:
            if g_col in df.columns:
                total_goals = df[g_col].dropna().astype(str).str.strip().nunique()
                if total_goals > 0:
                    break

        # 3. Đếm số Measures
        meas_col = "Measure_ID" if "Measure_ID" in df.columns else df.columns[0]
        total_measures = len(df[meas_col].dropna())

        # 4. Đếm số câu trả lời / tiến độ hoàn thành
        status_col = "Status" if "Status" in df.columns else None
        completed_measures = 0
        if status_col:
            completed_measures = len(df[df[status_col].astype(str).str.strip() == "Hoàn thành"])

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
        """Thống kê số lượng theo từng trạng thái thực hiện."""
        if df.empty or "Status" not in df.columns:
            return pd.DataFrame(columns=["Status", "Count"])

        counts = df["Status"].astype(str).str.strip().value_counts().reset_index()
        counts.columns = ["Status", "Count"]
        return counts
