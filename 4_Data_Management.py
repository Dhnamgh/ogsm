"""
Data Management Page.
Allows units to upload Excel files directly to OneDrive DATA folder and inspect raw data.
"""

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import io
import pandas as pd
import streamlit as st
from ogsm_service import OGSMService
from logger import get_logger

logger = get_logger()

st.set_page_config(page_title="Quản Lý Dữ Liệu - OGSM Portal", layout="wide")
st.title("📂 Quản Lý & Cập Nhật Dữ Liệu Báo Cáo OGSM")

st.markdown("""
Trang này dành cho đại diện các **Phòng / Khoa / Trung tâm** tải file báo cáo tiến độ OGSM định kỳ hàng tháng lên hệ thống.
""")

try:
    service = OGSMService()
    
    st.markdown("---")
    st.subheader("📤 Cập Nhật Báo Cáo Cho Đơn Vị")
    
    col_upload, col_guide = st.columns([1, 1])

    with col_upload:
        # Chọn mã đơn vị cập nhật
        unit_code_input = st.text_input(
            "📍 Mã Đơn Vị (viết tắt, ví dụ: HCTH, KHTH, TCYH, Y, DUOC...):",
            placeholder="Nhập mã đơn vị..."
        ).strip().upper()

        uploaded_file = st.file_uploader(
            "Chọn file Excel báo cáo (.xlsx) của đơn vị:",
            type=["xlsx"]
        )

        if st.button("🚀 Tải Lên & Cập Nhật Báo Cáo", type="primary"):
            if not unit_code_input:
                st.error("Vui lòng nhập Mã Đơn Vị trước khi tải lên.")
            elif not uploaded_file:
                st.error("Vui lòng chọn file Excel (.xlsx) báo cáo.")
            else:
                with st.spinner(f"Đang ghi đè báo cáo cho đơn vị {unit_code_input} lên OneDrive..."):
                    try:
                        file_bytes = uploaded_file.read()
                        
                        # Kiểm tra đọc thử file excel
                        df_check = pd.read_excel(io.BytesIO(file_bytes), engine="openpyxl")
                        
                        target_filename = f"P.{unit_code_input}.xlsx"
                        
                        # Tải lên OneDrive
                        success = service.upload_unit_file(target_filename, file_bytes)
                        
                        if success:
                            st.success(f"🎉 Đã cập nhật thành công báo cáo cho đơn vị **{unit_code_input}** (`{target_filename}`)!")
                            st.info("💡 Bạn có thể quay lại mục **Dashboard** để xem các biểu đồ tiến độ vừa được tự động tính toán lại.")
                            st.cache_data.clear()
                        else:
                            st.error("Không thể ghi đè file lên OneDrive. Vui lòng kiểm tra lại cấu hình kết nối.")
                    except Exception as ex:
                        st.error(f"Lỗi đọc định dạng file Excel: {ex}")

    with col_guide:
        st.info("""
        ### 📋 Hướng dẫn cập nhật định kỳ:
        1. Sử dụng file Excel khung mẫu OGSM 2025-2029 của Nhà trường.
        2. Cập nhật kết quả vào các cột: **`Tỷ lệ đạt (%)`** và **`Trạng thái`** (*Hoàn thành, Đang thực hiện, Chưa đến hạn, Không đạt*).
        3. Nhập chính xác **Mã đơn vị** và bấm nút **Tải Lên**.
        4. Hệ thống sẽ tự động tổng hợp vào báo cáo chung của Đại học Y Dược TP.HCM.
        """)

    st.markdown("---")
    st.subheader("🔍 Xem Dữ Liệu Báo Cáo Đã Tải Lên")

    df_master = service.get_full_ogsm_data()

    if not df_master.empty:
        available_units = sorted(list(df_master["Unit_Code"].unique()))
        selected_unit_view = st.selectbox("Chọn đơn vị để xem chi tiết dữ liệu:", ["Tất cả đơn vị"] + available_units)

        df_display = df_master.copy()
        if selected_unit_view != "Tất cả đơn vị":
            df_display = df_display[df_display["Unit_Code"] == selected_unit_view]

        st.dataframe(
            df_display[[
                "Unit_Code", "Objective_ID", "Goal_ID", "Measure_ID", 
                "Measure_Desc", "Target", "Actual", "Status"
            ]],
            use_container_width=True,
            height=400
        )
    else:
        st.warning("Hiện chưa có dữ liệu đơn vị nào trên hệ thống.")

except Exception as e:
    st.error(f"Lỗi nạp trang Quản Lý Dữ Liệu: {e}")
