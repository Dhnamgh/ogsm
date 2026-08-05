"""
Trang Quản lý dữ liệu OGSM - Đại học Y Dược TP.HCM
Tên đơn vị tải lên liên kết tự động theo thời gian thực với Tab được chọn.
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

# CSS Tiêu đề chữ xanh nền trắng & Tab chữ trắng nền xanh bo 4 góc
st.markdown("""
<style>
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background-color: transparent;
        padding: 6px 0px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 44px;
        background-color: #1877F2 !important;
        color: #ffffff !important;
        border-radius: 8px !important;
        font-size: 15px;
        font-weight: 600;
        padding: 10px 20px;
        border: none !important;
        transition: all 0.25s ease-in-out;
        box-shadow: 0 2px 5px rgba(24, 119, 242, 0.2);
    }
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #166fe5 !important;
        color: #ffffff !important;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(22, 111, 229, 0.4);
        cursor: pointer;
    }
    .stTabs [aria-selected="true"] {
        background-color: #0b51c5 !important;
        color: #ffffff !important;
        box-shadow: 0 4px 10px rgba(11, 81, 197, 0.5) !important;
    }

    .section-header-blue {
        background-color: #ffffff;
        color: #1877F2;
        padding: 12px 18px;
        border-radius: 8px;
        border: 1px solid #e4e6eb;
        font-size: 18px;
        font-weight: 700;
        margin: 14px 0px 14px 0px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.04);
    }

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

# Khởi tạo giá trị mặc định cho Đơn vị được chọn trong Session State
if "selected_unit_label" not in st.session_state:
    st.session_state["selected_unit_label"] = "P.HCTH - Phòng Hành chính Tổng hợp"

def update_selected_unit(key_name):
    """Callback hàm tự động cập nhật đơn vị khi chọn thay đổi ở bất kỳ Tab nào"""
    st.session_state["selected_unit_label"] = st.session_state[key_name]

try:
    service = OGSMService()
    
    st.markdown("---")
    st.markdown('<div class="section-header-blue">Cập Nhật Báo Cáo Cho Đơn Vị</div>', unsafe_allow_html=True)
    
    col_upload, col_guide = st.columns([1.2, 0.8])

    with col_upload:
        st.markdown('<div class="subsection-header-blue">Bước 1: Chọn Khối Đơn Vị Báo Cáo</div>', unsafe_allow_html=True)
        
        group_tabs = st.tabs(list(UNIT_GROUPS.keys()))
        
        for i, (group_name, units_dict) in enumerate(UNIT_GROUPS.items()):
            with group_tabs[i]:
                st.markdown(f'<div class="subsection-header-blue">Bước 2: Danh sách Đơn vị thuộc [{group_name}]</div>', unsafe_allow_html=True)
                
                unit_options = [f"{k} - {v}" for k, v in units_dict.items()]
                
                selectbox_key = f"select_tab_unit_{i}"
                st.selectbox(
                    "Tên Đơn Vị Báo Cáo:",
                    options=unit_options,
                    key=selectbox_key,
                    on_change=update_selected_unit,
                    args=(selectbox_key,)
                )

        st.markdown("---")
        
        # Tự động lấy Đơn vị đang được chọn trực tiếp
        active_unit_label = st.session_state["selected_unit_label"]
        selected_unit_code = active_unit_label.split(" - ")[0]

        uploaded_file = st.file_uploader(
            f"Chọn file Excel báo cáo (.xlsx) cho đơn vị [{active_unit_label}]:",
            type=["xlsx"]
        )

        if st.button("Tải Lên và Cập Nhật Báo Cáo", type="primary"):
            if not uploaded_file:
                st.error(f"Vui lòng chọn file Excel (.xlsx) báo cáo cho đơn vị [{active_unit_label}] trước khi tải lên.")
            else:
                with st.spinner(f"Đang lưu báo cáo cho đơn vị {selected_unit_code} lên OneDrive..."):
                    try:
                        file_bytes = uploaded_file.read()
                        df_check = pd.read_excel(io.BytesIO(file_bytes), engine="openpyxl")
                        
                        target_filename = f"{selected_unit_code}.xlsx"
                        success = service.upload_unit_file(target_filename, file_bytes)
                        
                        if success:
                            st.success(f"Đã cập nhật thành công báo cáo cho đơn vị **{active_unit_label}**.")
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
        3. Chọn đúng **Khối Đơn Vị** từ các Tab và chọn **Tên Đơn Vị**, hệ thống sẽ tự động liên kết tên đơn vị vào khung tải file bên dưới.
        4. Bấm **Tải Lên và Cập Nhật Báo Cáo** để hoàn tất.
        """)

    st.markdown("---")
    st.markdown('<div class="section-header-blue">Xem Dữ Liệu Báo Cáo Đã Tải Lên</div>', unsafe_allow_html=True)

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
