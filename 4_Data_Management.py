"""
Data Sync, Export, & Health Management Page.
"""

import streamlit as st
from services.ogsm_service import OGSMService
from services.report_service import ReportService
from components.tables import render_ogsm_table

st.set_page_config(page_title="Quản Lý Dữ Liệu | OGSM Portal", layout="wide")

st.title("Quản Lý Dữ Liệu & Xuất Báo Cáo")

try:
    service = OGSMService()
    df = service.get_full_ogsm_data()

    tab1, tab2 = st.tabs(["Xem Dữ Liệu Toàn Phần", "Xuất Báo Cáo Excel"])

    with tab1:
        st.subheader("Bảng Dữ Liệu OGSM Master")
        render_ogsm_table(df)

    with tab2:
        st.subheader("Tải Báo Cáo Bằng File Excel Stream")
        st.write("File Excel được tạo trực tiếp với định dạng doanh nghiệp UMP chuẩn.")

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
