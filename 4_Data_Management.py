"""
Trang Quan ly du lieu OGSM - Dai hoc Y Duoc TP.HCM
Giao dien phan khoi don vi hai cap, khong emoji.
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

st.set_page_config(page_title="Quan Ly Du Lieu - OGSM Portal", layout="wide")

# CSS tuy chinh giao dien the chon khoi don vi (Hover/Active Highlight màu xanh)
st.markdown("""
<style>
    /* CSS dinh dang danh sach chon don vi kieu the noi noi bat */
    div[data-baseweb="select"] > div {
        border-radius: 8px;
        border: 1px solid #0066cc;
    }
    .stButton > button {
        border-radius: 8px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

st.title("Quan Ly va Cap Nhat Du Lieu Bao Cao OGSM")

# Phan loai 29 don vi theo khoi chuc nang
UNIT_GROUPS = {
    "Khoi Phong Ban": {
        "P.HCTH": "Phong Hanh chinh Tong hop",
        "P.QTGT": "Phong Quan tri Giao tai",
        "P.TCCB": "Phong To chuc Can bo",
        "P.CTSV": "Phong Cong tac Sinh vien",
        "P.KHCN": "Phong Khoa hoc Cong nghe",
        "P.HTQT": "Phong Hop tac Quoc te",
        "P.KHTC": "Phong Ke hoach Tai chinh",
        "P.TTPC": "Phong Thanh tra Phap che",
        "P.ĐTSĐH": "Phong Dao tao Sau dai hoc",
        "P.ĐTĐH": "Phong Dao tao Dai hoc",
        "P.ĐBCL": "Phong Dam bao Chat luong Giao duc va Khao thi"
    },
    "Khoi Truong / Khoa": {
        "TRƯỜNG Y": "Truong Y",
        "T.DƯỢC": "Truong Duoc",
        "T.ĐD-KTYH": "Truong Dieu duong Ky thuat Y hoc",
        "K.KHCB": "Khoa Khoa hoc Co ban",
        "K.YHCT": "Khoa Y hoc Co truyen",
        "K.YTCC": "Khoa Y te Cong cong",
        "K.RHM": "Khoa Rang Ham Mat"
    },
    "Khoi Benh vien / Phong kham": {
        "BV ĐHYD": "Benh vien Dai hoc Y Duoc",
        "PKCK RHM": "Phong kham Chuyen khoa Rang Ham Mat"
    },
    "Khoi Trung tam": {
        "TT.KCCLXN": "Trung tam Kiem chuan Chat luong Xet nghiem",
        "TT.KHCN UMP": "Trung tam Khoa hoc Cong nghe UMP",
        "TT.GDYH": "Trung tam Giao duc Y hoc",
        "TT.CNTT": "Trung tam Cong nghe Thong tin",
        "TT.YSHPT": "Trung tam Y Sinh hoc Phan tu",
        "TT.ĐTNLYT": "Trung tam Dao tao Nhan luc Y te theo nhu cau xa hoi"
    },
    "Don vi khac": {
        "KTX": "Ky tuc xa",
        "TCYH": "Tap chi Y hoc",
        "THƯ VIỆN": "Thu vien"
    }
}

try:
    service = OGSMService()
    
    st.markdown("---")
    st.subheader("Cap Nhat Bao Cao Cho Don Vi")
    
    col_upload, col_guide = st.columns([1.2, 0.8])

    with col_upload:
        st.write("**Buoc 1: Chon Khoi Don Vi**")
        group_tabs = st.tabs(list(UNIT_GROUPS.keys()))
        
        selected_unit_code = None
        
        for i, (group_name, units_dict) in enumerate(UNIT_GROUPS.items()):
            with group_tabs[i]:
                st.write(f"**Buoc 2: Chon Don Vi thuoc {group_name}**")
                unit_options = [f"{k} - {v}" for k, v in units_dict.items()]
                selected_item = st.radio(
                    "Danh sach don vi:",
                    options=unit_options,
                    key=f"radio_{i}",
                    label_visibility="collapsed"
                )
                selected_unit_code = selected_item.split(" - ")[0]

        st.markdown("---")
        uploaded_file = st.file_uploader(
            f"Chon file Excel bao cao (.xlsx) cho don vi [{selected_unit_code}]:",
            type=["xlsx"]
        )

        if st.button("Tai Len va Cap Nhat Bao Cao", type="primary"):
            if not uploaded_file:
                st.error("Vui long chon file Excel (.xlsx) bao cao truoc khi tai len.")
            else:
                with st.spinner(f"Dang luu bao cao cho don vi {selected_unit_code} len OneDrive..."):
                    try:
                        file_bytes = uploaded_file.read()
                        df_check = pd.read_excel(io.BytesIO(file_bytes), engine="openpyxl")
                        
                        target_filename = f"{selected_unit_code}.xlsx"
                        success = service.upload_unit_file(target_filename, file_bytes)
                        
                        if success:
                            st.success(f"Da cap nhat thanh cong bao cao cho don vi {selected_unit_code}.")
                            st.cache_data.clear()
                        else:
                            st.error("Khong the ghi de file len OneDrive. Vui long kiem tra lai cau hinh ket noi.")
                    except Exception as ex:
                        st.error(f"Loi doc dinh dang file Excel: {ex}")

    with col_guide:
        st.info("""
        **Huong dan cap nhat dinh ky:**
        1. Su dung file Excel khung mau OGSM 2025-2029 cua Nha truong.
        2. Cap nhat ket qua thuc hien vao cot Tyle dat (%) (Trang thai se tu dong duoc tinh theo cong thuc san trong file Excel).
        3. Chon dung Khoi Don Vi va Don Vi tu cac Tab phan cap, sau do bam Tai Len va Cap Nhat Bao Cao.
        4. He thong se tu dong tong hop vao bao cao chung cua Dai hoc Y Duoc TP.HCM.
        """)

    st.markdown("---")
    st.subheader("Xem Du Lieu Bao Cao Da Tai Len")

    df_master = service.get_full_ogsm_data()

    if not df_master.empty:
        available_units = sorted(list(df_master["Unit_Code"].unique()))
        selected_unit_view = st.selectbox("Chon don vi de xem chi tiet du lieu:", ["Tat ca don vi"] + available_units)

        df_display = df_master.copy()
        if selected_unit_view != "Tat ca don vi":
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
        st.warning("Hien chua co du lieu don vi nao tren he thong.")

except Exception as e:
    st.error(f"Loi nap trang Quan Ly Du Lieu: {e}")
