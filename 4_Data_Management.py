"""
Trang Quản lý dữ liệu OGSM - Đại học Y Dược TP.HCM
Giao diện phân khối đơn vị, màu xanh Facebook nổi bật, tiếng Việt có dấu đầy đủ.
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

# CSS tạo hiệu ứng màu xanh Facebook (#1877F2) cho Tab và hiệu ứng Hover nổi màu xanh
st.markdown("""
<style>
    /* Tab Khối đơn vị kiểu thẻ bo tròn */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #f0f2f5;
        padding: 8px;
        border-radius: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 42px;
        background-color: #ffffff;
        border-radius: 8px;
        color: #1c1e21;
        font-weight: 600;
        padding: 8px 16px;
        border: 1px solid #e4e6eb;
        transition: all 0.2s ease-in-out;
    }
    /* Hiệu ứng Hover con trỏ chuột trỏ vào Tab */
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #e7f3ff !important;
        color: #1877F2 !important;
        border-color: #1877F2 !important;
    }
    /* Tab đang được chọn */
    .stTabs [aria-selected="true"] {
        background-color: #1877F2 !important;
        color: #ffffff !important;
        border-color: #1877F2 !important;
        box-shadow: 0 2px 6px rgba(24, 119, 242, 0.3);
    }
    
    /* Nút bấm tải lên chuẩn màu Facebook */
    .stButton > button {
        background-color: #1877F2;
        color: white;
        border-radius: 8px;
        font-weight: bold;
        border: none;
        padding: 10px 24px;
        transition: all 0.2s;
    }
    .stButton > button:hover {
        background-color: #166fe5;
        box-shadow: 0 4px 12px rgba(22, 111, 229, 0.4);
    }
</style>
""", unsafe_allow_html=True)

st.title("Quản Lý và Cập Nhật Dữ Liệu Báo Cáo OGSM")

# Phân loại 29 đơn vị theo khối chức năng
UNIT_GROUPS = {
    "Khối Phòng Ban": {
        "P.HCTH": "Phòng Hành chính Tổng hợp",
        "P.QTGT": "Phòng Quản trị Giáo tài",
        "P.TCCB": "Phòng Tổ chức Cán bộ",
        "P.CTSV": "Phòng Công tác Sinh viên",
        "P.KHCN": "Phòng Khoa học Công nghệ",
        "P.HTQT": "Phòng Hợp tác Quốc tế",
        "P.KHTC": "Phòng Kế hoạch Tài chính",
        "P.TTPC": "Phòng Thanh tra Pháp chế",
        "P.ĐTSĐH": "Phòng Đào tạo Sau đại học",
        "P.ĐTĐH": "Phòng Đào tạo Đại học",
        "P.ĐBCL": "Phòng Đảm bảo Chất lượng Giáo dục và Khảo thí"
    },
    "Khối Trường / Khoa": {
        "TRƯỜNG Y": "Trường Y",
        "T.DƯỢC": "Trường Dược",
        "T.ĐD-KTYH": "Trường Điều dưỡng Kỹ thuật Y học",
        "K.KHCB": "Khoa Khoa học Cơ bản",
        "K.YHCT": "Khoa Y học Cổ truyền",
        "K.YTCC": "Khoa Y tế Công cộng",
        "K.RHM": "Khoa Răng Hàm Mặt"
    },
    "Khối Bệnh viện / Phòng khám": {
        "BV ĐHYD": "Bệnh viện Đại học Y Dược",
        "PKCK RHM": "Phòng khám Chuyên khoa Răng Hàm Mặt"
    },
    "Khối Trung tâm": {
        "TT.KCCLXN": "Trung tâm Kiểm chuẩn Chất lượng Xét nghiệm",
        "TT.KHCN UMP": "Trung tâm Khoa học Công nghệ UMP",
        "TT.GDYH": "Trung tâm Giáo dục Y học",
        "TT.CNTT": "Trung tâm Công nghệ Thông tin",
        "TT.YSHPT": "Trung tâm Y Sinh học Phân tử",
        "TT.ĐTNLYT": "Trung tâm Đào tạo Nhân lực Y tế theo nhu cầu xã hội"
    },
    "Đơn vị khác": {
        "KTX": "Ký túc xá",
        "TCYH": "Tạp chí Y học",
        "THƯ VIỆN": "Thư viện"
    }
}

try:
    service = OGSMService()
    
    st.markdown("---")
    st.subheader("Cập Nhật Báo Cáo Cho Đơn Vị")
    
    col_upload, col_guide = st.columns([1.2, 0.8])

    with col_upload:
        st.write("**Bước 1: Chọn Khối Đơn Vị**")
        group_tabs = st.tabs(list(UNIT_GROUPS.keys()))
        
        selected_unit_code = None
        
        for i, (group_name, units_dict) in enumerate(UNIT_GROUPS.items()):
            with group_tabs[i]:
                st.write(f"**Bước 2: Chọn Đơn vị thuộc {group_name}**")
                unit_options = [f"{k} - {v}" for k, v in units_dict.items()]
                selected_item = st.radio(
                    "Danh sách đơn vị:",
                    options=unit_options,
                    key=f"radio_mgmt_{i}",
                    label_visibility="collapsed"
                )
                selected_unit_code = selected_item.split(" - ")[0]

        st.markdown("---")
        uploaded_file = st.file_uploader(
            f"Chọn file Excel báo cáo (.xlsx) cho đơn vị [{selected_unit_code}]:",
            type=["xlsx"]
        )

        if st.button("Tải Lên và Cập Nhật Báo Cáo", type="primary"):
            if not uploaded_file:
                st.error("Vui lòng chọn file Excel (.xlsx) báo cáo trước khi tải lên.")
            else:
                with st.spinner(f"Đang lưu báo cáo cho đơn vị {selected_unit_code} lên OneDrive..."):
                    try:
                        file_bytes = uploaded_file.read()
                        df_check = pd.read_excel(io.BytesIO(file_bytes), engine="openpyxl")
                        
                        target_filename = f"{selected_unit_code}.xlsx"
                        success = service.upload_unit_file(target_filename, file_bytes)
                        
                        if success:
                            st.success(f"Đã cập nhật thành công báo cáo cho đơn vị **{selected_unit_code}**.")
                            st.cache_data.clear()
                        else:
                            st.error("Không thể ghi đè file lên OneDrive. Vui lòng kiểm tra lại cấu hình kết nối.")
                    except Exception as ex:
                        st.error(f"Lỗi đọc định dạng file Excel: {ex}")

    with col_guide:
        st.info("""
        **Hướng dẫn cập nhật định kỳ:**
        1. Sử dụng file Excel khung mẫu OGSM 2025–2029 của Nhà trường.
        2. Cập nhật kết quả thực hiện vào cột **`Tỷ lệ đạt (%)`** (Trạng thái sẽ tự động được tính theo công thức sẵn trong file Excel).
        3. Chọn đúng **Khối Đơn Vị** và **Tên Đơn Vị** từ các Tab phân cấp, sau đó bấm **Tải Lên và Cập Nhật Báo Cáo**.
        4. Hệ thống sẽ tự động tổng hợp vào báo cáo chung của Đại học Y Dược TP.HCM.
        """)

    st.markdown("---")
    st.subheader("Xem Dữ Liệu Báo Cáo Đã Tải Lên")

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
