"""
Trang Quản lý dữ liệu OGSM - Đại học Y Dược TP.HCM
Cập nhật đơn vị tải file liên kết thời gian thực và thiết kế Banner khung xanh bo góc chữ trắng.
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

# CSS Thiết kế Banner chữ trắng nền xanh bo 8px & Khung tiêu đề con
st.markdown("""
<style>
    /* 1. Banner Tiêu Đề Chính: Khung nền xanh Facebook bo 8px, chữ trắng nổi bật */
    .main-banner-blue {
        background: linear-gradient(135deg, #1877F2 0%, #0b51c5 100%);
        color: #ffffff !important;
        padding: 16px 24px;
        border-radius: 8px;
        font-size: 24px;
        font-weight: 700;
        text-align: center;
        box-shadow: 0 4px 12px rgba(24, 119, 242, 0.35);
        margin-bottom: 24px;
    }

    /* 2. Banner Tiêu Đề Mục lớn */
    .section-banner-blue {
        background-color: #1877F2;
        color: #ffffff !important;
        padding: 12px 20px;
        border-radius: 8px;
        font-size: 17px;
        font-weight: 700;
        margin: 16px 0px 16px 0px;
        box-shadow: 0 2px 8px rgba(24, 119, 242, 0.25);
    }

    /* 3. Khung Tiêu Đề Con: Nền trắng chữ xanh bo góc */
    .subsection-header-blue {
        background-color: #ffffff;
        color: #1877F2;
        padding: 10px 16px;
        border-radius: 8px;
        border: 1px solid #e4e6eb;
        font-size: 15px;
        font-weight: 700;
        margin: 10px 0px 12px 0px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.03);
    }

    /* Style nút chọn Khối đơn vị kiểu thẻ bo góc mượt mà */
    div[data-testid="stSegmentedControl"] button {
        border-radius: 8px !important;
        font-weight: 600 !important;
    }

    /* Styling nút bấm Tải lên */
    .stButton > button {
        background-color: #1877F2;
        color: white;
        border-radius: 8px;
        font-weight: bold;
        border: none;
        padding: 12px 28px;
        font-size: 16px;
        transition: all 0.2s;
        box-shadow: 0 4px 10px rgba(24, 119, 242, 0.3);
    }
    .stButton > button:hover {
        background-color: #166fe5;
        box-shadow: 0 6px 16px rgba(22, 111, 229, 0.45);
    }
</style>
""", unsafe_allow_html=True)

# BANNER TIÊU ĐỀ CHÍNH CỦA TRANG
st.markdown('<div class="main-banner-blue">Quản Lý và Cập Nhật Dữ Liệu Báo Cáo OGSM</div>', unsafe_allow_html=True)

# Phân loại chuẩn 29 đơn vị UMP
UNIT_GROUPS = {
    "Khối Phòng chức năng": {
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
    
    st.markdown('<div class="section-banner-blue">Cập Nhật Báo Cáo Cho Đơn Vị</div>', unsafe_allow_html=True)
    
    col_upload, col_guide = st.columns([1.2, 0.8])

    with col_upload:
        st.markdown('<div class="subsection-header-blue">Bước 1: Chọn Khối Đơn Vị Báo Cáo</div>', unsafe_allow_html=True)
        
        # Thẻ chọn Khối đơn vị trực quan
        selected_group = st.segmented_control(
            "Chọn Khối:",
            options=list(UNIT_GROUPS.keys()),
            default="Khối Phòng chức năng",
            label_visibility="collapsed"
        )
        
        if not selected_group:
            selected_group = "Khối Phòng chức năng"

        st.markdown(f'<div class="subsection-header-blue">Bước 2: Chọn Đơn vị thuộc [{selected_group}]</div>', unsafe_allow_html=True)
        
        units_dict = UNIT_GROUPS[selected_group]
        unit_options = [f"{k} - {v}" for k, v in units_dict.items()]
        
        # Ô chọn đơn vị thuộc Khối đang active
        selected_unit_label = st.selectbox(
            "Tên Đơn Vị Báo Cáo:",
            options=unit_options,
            key=f"selectbox_active_unit_{selected_group}"
        )
        
        selected_unit_code = selected_unit_label.split(" - ")[0]

        st.markdown("---")
        
        # Khung tải file liên kết thời gian thực 100% với lựa chọn ở Bước 2
        uploaded_file = st.file_uploader(
            f"Chọn file Excel báo cáo (.xlsx) cho đơn vị [{selected_unit_label}]:",
            type=["xlsx"]
        )

        if st.button("Tải Lên và Cập Nhật Báo Cáo", type="primary"):
            if not uploaded_file:
                st.error(f"Vui lòng chọn file Excel (.xlsx) báo cáo cho đơn vị [{selected_unit_label}] trước khi tải lên.")
            else:
                with st.spinner(f"Đang lưu báo cáo cho đơn vị {selected_unit_code} lên OneDrive..."):
                    try:
                        file_bytes = uploaded_file.read()
                        df_check = pd.read_excel(io.BytesIO(file_bytes), engine="openpyxl")
                        
                        target_filename = f"{selected_unit_code}.xlsx"
                        success = service.upload_unit_file(target_filename, file_bytes)
                        
                        if success:
                            st.success(f"Đã cập nhật thành công báo cáo cho đơn vị **{selected_unit_label}**.")
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
        3. Chọn đúng **Khối Đơn Vị** và **Tên Đơn Vị**, hệ thống sẽ tự động liên kết đúng 100% tên đơn vị vào mục tải file Excel bên dưới.
        4. Bấm **Tải Lên và Cập Nhật Báo Cáo** để hoàn tất.
        """)

    st.markdown("---")
    st.markdown('<div class="section-banner-blue">Xem Dữ Liệu Báo Cáo Đã Tải Lên</div>', unsafe_allow_html=True)

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
