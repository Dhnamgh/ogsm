"""
OGSM Portal Main Application Router.
"""

import os
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import streamlit as st
from config import load_config
from logger import get_logger

logger = get_logger()

st.set_page_config(
    page_title="OGSM Portal - UMP",
    layout="wide",
    initial_sidebar_state="expanded",
)


def main():
    try:
        config = load_config()
        logger.info("Khởi tạo hệ thống OGSM Portal thành công...")
    except Exception as e:
        st.error(f"Lỗi Cấu Hình Hệ Thống: {e}")
        st.stop()

    st.sidebar.title("OGSM Portal")
    st.sidebar.caption("Đại học Y Dược TP.HCM")
    st.sidebar.markdown("---")

    st.title("Hệ Thống Quản Trị Chiến Lược OGSM")
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
