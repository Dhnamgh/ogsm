"""
OGSM Analytics Service - Thuật toán đếm và tính toán chỉ số OGSM chuẩn xác.
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

        # 1. Tìm cột Objectives và đếm
        total_objectives = 0
        for col in df.columns:
            if any(k in col.lower() for k in ["objective", "mục tiêu chiến lược", "mục tiêu chung", "stt_o", "mã o"]):
                valid = df[col].dropna().astype(str).str.strip()
                valid = valid[~valid.isin(["", "nan", "None"])]
                if not valid.empty:
                    total_objectives = valid.nunique()
                    break

        # 2. Tìm cột Goals / Strategies và đếm
        total_goals = 0
        for col in df.columns:
            if any(k in col.lower() for k in ["goal", "strategy", "mục tiêu cụ thể", "chiến lược", "chỉ tiêu", "stt_g", "stt_s", "mã g", "mã s"]):
                valid = df[col].dropna().astype(str).str.strip()
                valid = valid[~valid.isin(["", "nan", "None"])]
                if not valid.empty:
                    total_goals = valid.nunique()
                    break

        # 3. Đếm số Measures
        total_measures = len(df)

        # 4. Tính phần trăm hoàn thành
        status_col = None
        for col in df.columns:
            if any(k in col.lower() for k in ["status", "trạng thái", "tiến độ"]):
                status_col = col
                break

        completed_measures = 0
        if status_col:
            status_clean = df[status_col].dropna().astype(str).str.strip().str.lower()
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
            if any(k in col.lower() for k in ["status", "trạng thái", "tiến độ"]):
                status_col = col
                break

        if not status_col:
            return pd.DataFrame(columns=["Status", "Count"])

        counts = df[status_col].dropna().astype(str).str.strip().value_counts().reset_index()
        counts.columns = ["Status", "Count"]
        return counts
