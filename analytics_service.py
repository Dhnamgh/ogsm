"""
Analytics and KPI aggregation calculations for OGSM performance tracking.
"""

import pandas as pd
from typing import Dict, Any


class OGSMAnalyticsService:
    """
    Computes summary metrics, completion percentages, and status breakdown.
    """

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

        # Measure level completion rate calculation
        targets = df["Target"].replace(0, 1.0) # avoid division by zero
        df_calc = df.copy()
        df_calc["Completion"] = (df_calc["Actual"] / targets) * 100.0
        df_calc["Completion"] = df_calc["Completion"].clip(lower=0.0, upper=100.0)

        avg_completion = float(df_calc["Completion"].mean())
        completed_cnt = int((df["Status"].str.lower() == "completed").sum())

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
