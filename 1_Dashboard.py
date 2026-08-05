"""
Trang Executive Dashboard - Đại học Y Dược TP.HCM
"""

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import traceback
import streamlit as st

st.set_page_config(page_title="Dashboard OGSM - Đại học Y Dược TP.HCM", layout="wide")

try:
    import pandas as pd
    from ogsm_service import OGSMService
    from analytics_service import OGSMAnalyticsService
    from metrics_cards import render_metrics_cards
    from charts import (
        create_status_donut_chart, 
        create_objective_progress_chart, 
        create_stacked_kpi_by_unit_chart
    )

    st.title("Tổng Quan Thực Hiện OGSM - Đại học Y Dược TP.HCM")

    service = OGSMService()
    df_all = service.get_full_ogsm_data()

    if isinstance(df_all, pd.DataFrame) and not df_all.empty:
        kpis = OGSMAnalyticsService.compute_summary_kpis(df_all)
        render_metrics_cards(kpis)

        col_left, col_right = st.columns([0.8, 1.2])
        with col_left:
            df_status = OGSMAnalyticsService.get_status_distribution(df_all)
            fig_donut = create_status_donut_chart(df_status)
            st.plotly_chart(fig_donut, use_container_width=True)

        with col_right:
            fig_obj = create_objective_progress_chart(df_all)
            st.plotly_chart(fig_obj, use_container_width=True)

        fig_bar_all = create_stacked_kpi_by_unit_chart(df_all, current_year_only=False)
        st.plotly_chart(fig_bar_all, use_container_width=True)

    else:
        st.warning("Chưa có dữ liệu báo cáo.")

except Exception as e:
    st.error(f"Lỗi nạp trang Dashboard: {e}")
    # Hiển thị chi tiết dòng code gây ra lỗi
    st.code(traceback.format_exc(), language="python")
