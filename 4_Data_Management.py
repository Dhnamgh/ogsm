"""
Trang Quản lý dữ liệu OGSM - Đại học Y Dược TP.HCM
Sử dụng Tab giao diện chuẩn với hiệu ứng Hover đổi màu xanh nổi bật khi trỏ con trỏ chuột.
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

# Bộ CSS tạo hiệu ứng Tab nổi bật: Nền xanh Facebook (#1877F2) khi Active và Đổi màu xanh nhẹ (#E7F3FF) khi Hover
st.markdown("""
<style>
    /* Khung danh sách các Tab */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #f0f2f5;
        padding: 8px;
        border-radius: 10px;
    }
    /* Thẻ Tab mặc định */
    .stTabs [data-baseweb="tab"] {
        height: 42px;
        background-color: #ffffff;
        border-radius: 8px;
        color: #1c1e21;
        font-weight: 600;
        padding: 8px 18px;
        border: 1px solid #e4e6eb;
        transition: all 0.2s ease-in-out;
    }
    /* HIỆU ỨNG NỔI MÀU XANH KHI TRỎ CON TRỎ CHUỘT VÀO TAB (HOVER) */
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #e7f3ff !important;
        color: #1877F2 !important;
        border-color: #1877F2 !important;
        cursor: pointer;
    }
    /* TAB ĐANG ĐƯỢC CHỌN (ACTIVE) */
    .stTabs [aria-selected="true"] {
        background-color: #1877F2 !important;
        color: #ffffff !important;
        border-color: #1877F2 !important;
        box-shadow: 0 3px 8px rgba(24, 119, 242, 0.35);
    }
    
    /* Hiệu ứng Hover cho nút bấm Tải Lên */
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

# Danh sách phân loại 29 đơn vị theo khối chức năng chuẩn UMP
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
    
    st.markdown("---")
    st.subheader("Cập Nhật Báo Cáo Cho Đơn Vị")
    
    col_upload, col_guide = st.columns([1.2, 0.8])

    with col_upload:
        st.write("**Bước 1: Chọn Khối Đơn Vị (Di con trỏ chuột vào Tab để xem hiệu ứng):**")
        group_tabs = st.tabs(list(UNIT_GROUPS.keys()))
        
        # Dictionary lưu mã đơn vị đang được chọn ở từng Tab
        selected_unit_by_tab = {}
        
        for i, (group_name, units_dict) in enumerate(UNIT_GROUPS.items()):
            with group_tabs[i]:
                st.write(f"**Bước 2: Chọn Đơn vị thuộc {group_name}**")
                unit_options = [f"{k} - {v}" for k, v in units_dict.items()]
                
                selected_item = st.selectbox(
                    "Tên Đơn Vị Báo Cáo:",
                    options=unit_options,
                    key=f"select_tab_unit_{i}"
                )
                selected_unit_by_tab[group_name] = selected_item

        # Lấy Tab đang mở thực tế thông qua thao tác người dùng
        # Streamlit sẽ sử dụng đơn vị từ dropdown tương ứng của Tab đang chọn
        st.markdown("---")
        
        # Chọn tổng hợp từ dropdown đại diện chính xác
        all_flatten_units = []
        for g_units in UNIT_GROUPS.values():
            for k, v in g_units.items():
                all_flatten_units.append(f"{k} - {v}")
                
        final_selected_unit = st.selectbox(
            "📍 Xác nhận Đơn Vị Tải Lên Báo Cáo:",
            options=all_flatten_units,
            key="final_confirm_unit_select"
        )
        
        selected_unit_code = final_selected_unit.split(" - ")[0]

        uploaded_file = st.file_uploader(
            f"Chọn file Excel báo cáo (.xlsx) cho đơn vị [{final_selected_unit}]:",
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
                            st.success(f"🎉 Đã cập nhật thành công báo cáo cho đơn vị **{final_selected_unit}**.")
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
        3. Chọn đúng **Khối Đơn Vị** từ các Tab và chọn **Tên Đơn Vị**, sau đó bấm **Tải Lên và Cập Nhật Báo Cáo**.
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
