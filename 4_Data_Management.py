"""
Data Management Page.
"""

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import streamlit as st
from ogsm_service import OGSMService
from report_service import ReportService
from tables import render_ogsm_table

st.title("Quản Lý Dữ Liệu & Xuất Báo Cáo")

try:
    service = OGSMService()
    df = service.get_full_ogsm_data()

    tab1, tab2 = st.tabs(["Xem Dữ Liệu Toàn Phần", "Xuất Báo Cáo Excel"])

    with tab1:
        st.subheader("Bảng Dữ Liệu OGSM Master Toàn Trường")
        render_ogsm_table(df)

    with tab2:
        st.subheader("Tải Báo Cáo Excel Tổng Hợp")

        if not df.empty:
            excel_bytes = ReportService.generate_excel_report(df)
            st.download_button(
                label="Tải Báo Cáo Excel (.xlsx)",
                data=excel_bytes,
                file_name="Bao_Cao_OGSM_UMP.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )

except Exception as e:
    st.error(f"Lỗi quản lý dữ liệu: {e}")
