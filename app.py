"""
OGSM Portal Main Application Router.
"""

import sys
from pathlib import Path

# Thêm thư mục gốc vào sys.path để Python nhận diện các module core, services, repository...
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import streamlit as st
from core.config import load_config
from core.logger import get_logger

logger = get_logger()

st.set_page_config(
    page_title="OGSM Portal - UMP",
    layout="wide",
    initial_sidebar_state="expanded",
)

def main():
    try:
        config = load_config()
        logger.info("Initializing OGSM Portal...")
    except Exception as e:
        st.error(f"Lỗi Khởi Tạo Cấu Hình Hệ Thống: {e}")
        st.stop()

    st.sidebar.title("OGSM Portal")
    st.sidebar.caption("Đại học Y Dược TP.HCM")
    st.sidebar.markdown("---")

    st.title("Chào Mừng Đến Với Hệ Thống OGSM Portal")
    st.markdown(
        """
        Hệ thống quản trị chiến lược và theo dõi chỉ số **OGSM (Objectives, Goals, Strategies, Measures)**
        kết nối thời gian thực với **Microsoft OneDrive for Business**.

        ### Các Chức Năng Chính:
        * **Dashboard:** Báo cáo chỉ số KPI toàn trường và từng đơn vị.
        * **OGSM Tree:** Cây cấu trúc mục tiêu chiến lược.
        * **Strategy Tracker:** Cập nhật kết quả chỉ số cho từng đơn vị.
        * **Data Management:** Bảng dữ liệu thô tổng hợp và xuất file Excel.
        """
    )


if __name__ == "__main__":
    main()
