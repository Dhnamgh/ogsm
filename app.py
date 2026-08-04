"""
OGSM Portal Main Application Router.
"""

import os
import sys
from pathlib import Path

# 1. Đảm bảo đường dẫn tuyệt đối của dự án luôn được nạp vào sys.path
FILE_PATH = Path(__file__).resolve()
ROOT_DIR = FILE_PATH.parent

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Đổi working directory về thư mục gốc
os.chdir(ROOT_DIR)

import streamlit as st

# 2. Import các module nội bộ
try:
    from core.config import load_config
    from core.logger import get_logger
except ModuleNotFoundError as e:
    st.error(
        f"Lỗi Import Module: {e}\n\n"
        f"**Đường dẫn gốc hiện tại:** `{ROOT_DIR}`\n\n"
        f"**Danh sách file/thư mục trong root:** `{os.listdir(ROOT_DIR)}`"
    )
    st.stop()

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
