"""
Strategy Tracking & Progress Update Page.
"""

import streamlit as st
from services.ogsm_service import OGSMService

st.set_page_config(page_title="Cập Nhật Tiến Độ | OGSM Portal", layout="wide")

st.title("Cập Nhật Tiến Độ Chỉ Số (Measures)")

try:
    service = OGSMService()
    df = service.get_full_ogsm_data()

    if not df.empty:
        st.subheader("Cập Nhật Trực Tiếp Lên OneDrive")

        measure_ids = df["Measure_ID"].dropna().unique()
        selected_m = st.selectbox("Chọn Mã Chỉ Số (Measure ID):", measure_ids)

        if selected_m:
            row = df[df["Measure_ID"] == selected_m].iloc[0]

            st.write(f"**Mô Tả:** {row.get('Measure_Desc', '')}")
            st.write(f"**Đơn Vị Phụ Trách:** {row.get('Owner', '')}")
            st.write(f"**Chỉ Tiêu (Target):** {row.get('Target', 0)} ({row.get('Unit', '')})")

            with st.form("update_measure_form"):
                current_actual = float(row.get("Actual", 0.0))
                current_status = str(row.get("Status", "In Progress"))

                new_actual = st.number_input("Giá Trị Thực Hiện Mới (Actual):", value=current_actual)
                new_status = st.selectbox(
                    "Trạng Thái Mới:",
                    ["Not Started", "In Progress", "Completed", "Delayed"],
                    index=["Not Started", "In Progress", "Completed", "Delayed"].index(current_status)
                    if current_status in ["Not Started", "In Progress", "Completed", "Delayed"] else 1
                )

                submit = st.form_submit_button("Lưu Thay Đổi")

                if submit:
                    with st.spinner("Đang lưu dữ liệu lên Microsoft OneDrive..."):
                        success = service.update_measure_actual(selected_m, new_actual, new_status)
                        if success:
                            st.success(f"Cập nhật thành công Measure {selected_m}!")
                            st.rerun()
                        else:
                            st.error("Cập nhật thất bại. Vui lòng kiểm tra nhật ký log.")

except Exception as e:
    st.error(f"Lỗi khi tải biểu mẫu cập nhật: {e}")
