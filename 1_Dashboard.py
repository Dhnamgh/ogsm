"""
Executive Dashboard Page.
"""

import streamlit as st
from services.ogsm_service import OGSMService
from services.analytics_service import OGSMAnalyticsService
from components.metrics_cards import render_metrics_cards
from components.charts import create_status_donut_chart, create_owner_progress_bar_chart

st.set_page_config(page_title="Dashboard | OGSM Portal", layout="wide")

st.title("Tổng Quan Thực Hiện OGSM")
st.caption("Đại học Y Dược TP. Hồ Chí Minh - Hệ Thống Quản Trị Chiến Lược")

try:
    service = OGSMService()
    df = service.get_full_ogsm_data()

    if not df.empty:
        # Render high level KPIs
        kpis = OGSMAnalyticsService.compute_summary_kpis(df)
        render_metrics_cards(kpis)

        st.markdown("---")

        # Render charts layout
        col_left, col_right = st.columns(2)

        with col_left:
            df_status = OGSMAnalyticsService.get_status_distribution(df)
            fig_donut = create_status_donut_chart(df_status)
            st.plotly_chart(fig_donut, use_container_width=True)

        with col_right:
            fig_bar = create_owner_progress_bar_chart(df)
            st.plotly_chart(fig_bar, use_container_width=True)

    else:
        st.warning("Dữ liệu OGSM từ OneDrive đang trống hoặc chưa được cấu hình.")

except Exception as e:
    st.error(f"Không thể tải dữ liệu Dashboard từ OneDrive: {e}")
