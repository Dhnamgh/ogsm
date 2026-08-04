"""
Executive Dashboard Page with Unit Filter.
"""

import sys
from pathlib import Path

# Nạp đường dẫn thư mục gốc (parent của thư mục pages) vào sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import streamlit as st

# Thử import các module từ thư mục gốc, hiển thị thông báo chi tiết nếu thiếu file
try:
    from ogsm_service import OGSMService
    from analytics_service import OGSMAnalyticsService
    from metrics_cards import render_metrics_cards
    from charts import create_status_donut_chart, create_owner_progress_bar_chart
except ModuleNotFoundError as err:
    st.error(f"Lỗi thiếu tập tin hỗ trợ ở thư mục gốc: {err}")
    st.info("Vui lòng đảm bảo các tệp `ogsm_service.py`, `analytics_service.py`, `metrics_cards.py`, `charts.py` đã có ở thư mục gốc của Repository.")
    st.stop()

st.set_page_config(page_title="Dashboard | OGSM Portal", layout="wide")

st.title("Tổng Quan Thực Hiện OGSM")
st.caption("Đại học Y Dược TP. Hồ Chí Minh - Hệ Thống Quản Trị Chiến Lược")

try:
    service = OGSMService()
    df_all = service.get_full_ogsm_data()

    if not df_all.empty:
        units = service.get_available_units()
        selected_unit = st.selectbox("Chọn Đơn Vị Báo Cáo:", ["Tất Cả Đơn Vị (Toàn Trường)"] + units)

        df_filtered = df_all.copy()
        if selected_unit != "Tất Cả Đơn Vị (Toàn Trường)":
            df_filtered = df_all[df_all["Unit_Code"] == selected_unit]

        kpis = OGSMAnalyticsService.compute_summary_kpis(df_filtered)
        render_metrics_cards(kpis)

        st.markdown("---")

        col_left, col_right = st.columns(2)

        with col_left:
            df_status = OGSMAnalyticsService.get_status_distribution(df_filtered)
            fig_donut = create_status_donut_chart(df_status)
            st.plotly_chart(fig_donut, use_container_width=True)

        with col_right:
            fig_bar = create_owner_progress_bar_chart(df_filtered)
            st.plotly_chart(fig_bar, use_container_width=True)

    else:
        st.warning("Không tìm thấy file dữ liệu đơn vị nào trong thư mục DATA trên OneDrive.")

except Exception as e:
    st.error(f"Lỗi kết nối dữ liệu OneDrive: {e}")
