"""
Streamlit UI Components for Top Metrics Cards.
"""

import streamlit as st
from typing import Dict, Any


def render_metrics_cards(kpis: Dict[str, Any]) -> None:
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="Mục Tiêu Chỉ Chiến Lược (Objectives)",
            value=kpis.get("total_objectives", 0),
        )

    with col2:
        st.metric(
            label="Mục Tiêu Cụ Thể (Goals / Strategies)",
            value=kpis.get("total_strategies", 0),
        )

    with col3:
        st.metric(
            label="Chỉ Số Đo Lường (Measures)",
            value=kpis.get("total_measures", 0),
        )

    with col4:
        avg_rate = kpis.get("avg_completion_rate", 0.0)
        completed_cnt = kpis.get("completed_measures", 0)
        st.metric(
            label="Tỷ Lệ Hoàn Thành Trung Bình",
            value=f"{avg_rate}%",
            delta=f"{completed_cnt} Đã Hoàn Thành",
        )
