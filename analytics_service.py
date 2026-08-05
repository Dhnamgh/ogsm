"""
Analytics engine for KPI calculation.
Supports Vietnamese status values from OGSM Excel files.
"""

import re
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

        # 1. Đếm Objectives (O1 -> O5)
        total_objs = 0
        if "Objective_ID" in df.columns:
            objs = df["Objective_ID"].dropna().astype(str).str.strip().str.upper()
            # Trích xuất dạng O1, O2... hoặc O01
            objs_extracted = objs.str.extract(r'(O\d+)', expand=False).dropna()
            total_objs = objs_extracted.nunique() if not objs_extracted.empty else objs.nunique()

        # 2. Đếm Goals / Strategies chuẩn (G1 -> G15)
        total_strats = 0
        goal_col = None
        for col in ["Goal_ID", "Strategy_ID"]:
            if col in df.columns:
                goal_col = col
                break

        if goal_col:
            goals = df[goal_col].dropna().astype(str).str.strip().str.upper()
            # Trích xuất mã Goal chuẩn dạng G1, G2... G15 (bỏ qua các ký tự phụ hoặc dòng rỗng)
            goals_extracted = goals.str.extract(r'(G\d+)', expand=False).dropna()
            if not goals_extracted.empty:
                total_strats = goals_extracted.nunique()
            else:
                total_strats = goals.nunique()

        # 3. Đếm Measures
        total_measures = 0
        if "Measure_ID" in df.columns:
            measures = df["Measure_ID"].dropna().astype(str).str.strip()
            measures = measures[~measures.isin(["", "nan", "None", "null"])]
            total_measures = measures.nunique()

        # 4. Tính tỷ lệ hoàn thành trung bình
        df_calc = df.copy()
        if "Actual" in df_calc.columns:
            df_calc["Completion"] = pd.to_numeric(df_calc["Actual"], errors="coerce").fillna(0.0).clip(lower=0.0, upper=100.0)
            avg_completion = float(df_calc["Completion"].mean())
        else:
            avg_completion = 0.0

        # 5. Đếm số lượng Hoàn thành
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
