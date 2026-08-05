"""
Data Management Page with Dropdown Unit Selection & Dynamic Instructions.
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

# Danh sách chuẩn các Đơn vị thuộc UMP
UMP_UNITS = [
    "P.HCTH - Phòng Hành chính Tổng hợp",
    "P.QTGT - Phòng Quản trị Gia tăng",
    "P.KHTH - Phòng Kế hoạch Tổng hợp",
    "P.TCCB - Phòng Tổ chức Cán bộ",
    "P.CTSV - Phòng Công tác Sinh viên",
    "P.KHCN - Phòng Khoa học Công nghệ",
    "P.HTQT - Phòng Hợp tác Quốc tế",
    "P.KHTC - Phòng Kế hoạch Tài chính",
    "P.TTPC - Phòng Thanh tra Pháp chế",
    "P.ĐTSĐH - Phòng Đào tạo Sau đại học",
    "P.ĐTĐH - Phòng Đào tạo Đại học",
    "P.ĐBCL - Phòng Đảm bảo Chất lượng",
    "K.KHCB - Khoa Khoa học Cơ bản",
    "K.Y TCC - Khoa Y tế Công cộng",
    "K.RHM - Khoa Răng Hàm Mặt",
    "K.YHCT - Khoa Y học Cổ truyền",
    "T.DƯỢC - Khoa Dược",
    "TRƯỜNG Y - Trường Y",
    "TT.KCXN - Trung tâm Kiểm chuẩn Xét nghiệm",
    "TT.KHCN UMP - Trung tâm KHCN UMP",
    "TT.GDYH - Trung tâm Giáo dục Y học",
    "TT.CNTT - Trung tâm Công nghệ Thông tin",
    "TT.YSHPT - Trung tâm Y sinh học Phân tử",
    "T.ĐĐ-KTYH - Khoa Điều dưỡng - Kỹ thuật Y học",
    "TT.ĐTNLYT - Trung tâm Đào tạo Năng lực Y tế",
    "BV.ĐHYD - Bệnh viện Đại học Y Dược",
    "KTX - Ký túc xá",
    "TV - Thư viện",
    "PK.RHM - Phòng khám Răng Hàm Mặt",
    "TCYH - Tạp chí Y học"
]

try:
    service = OGSMService()
    
    st.markdown("---")
    st.subheader("📤 Cập Nhật Báo Cáo Cho Đơn Vị")
    
    col_upload, col_guide = st.columns([1, 1])

    with col_upload:
        # Dropdown chọn Đơn vị thay vì gõ tay
        selected_unit_raw = st.selectbox(
            "📍 Chọn Đơn Vị Báo Cáo:",
            options=UMP_UNITS,
            index=0
        )
        
        # Tách mã đơn vị (ví dụ: "P.HCTH - Phòng..." -> "HCTH")
        unit_code_clean = selected_unit_raw.split(" - ")[0].replace("P.", "").replace("T.", "").replace("K.", "").replace("TT.", "").replace("BV.", "").strip()

        uploaded_file = st.file_uploader(
            "Chọn file Excel báo cáo (.xlsx) của đơn vị:",
            type=["xlsx"]
        )

        if st.button("🚀 Tải Lên & Cập Nhật Báo Cáo", type="primary"):
            if not uploaded_file:
                st.error("Vui lòng chọn file Excel (.xlsx) báo cáo trước khi tải lên.")
            else:
                with st.spinner(f"Đang ghi đè báo cáo cho đơn vị {unit_code_clean} lên OneDrive..."):
                    try:
                        file_bytes = uploaded_file.read()
                        
                        # Kiểm tra định dạng file
                        df_check = pd.read_excel(io.BytesIO(file_bytes), engine="openpyxl")
                        
                        target_filename = f"P.{unit_code_clean}.xlsx"
                        success = service.upload_unit_file(target_filename, file_bytes)
                        
                        if success:
                            st.success(f"🎉 Đã cập nhật thành công báo cáo cho đơn vị **{unit_code_clean}** (`{target_filename}`)!")
                            st.info("💡 Bạn có thể quay lại mục **Dashboard** để xem các biểu đồ tiến độ vừa được tự động tính toán lại.")
                            st.cache_data.clear()
                        else:
                            st.error("Không thể ghi đè file lên OneDrive. Vui lòng kiểm tra lại cấu hình kết nối.")
                    except Exception as ex:
                        st.error(f"Lỗi đọc định dạng file Excel: {ex}")

    with col_guide:
        st.info("""
        ### 📋 Hướng dẫn cập nhật định kỳ:
        1. Sử dụng file Excel khung mẫu OGSM 2025–2029 của Nhà trường.
        2. Cập nhật kết quả thực hiện vào cột **`Tỷ lệ đạt (%)`** (Trạng thái sẽ tự động được tính theo công thức sẵn trong file Excel).
        3. Chọn đúng **Tên Đơn Vị** từ danh sách thả xuống và bấm nút **Tải Lên & Cập Nhật Báo Cáo**.
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
