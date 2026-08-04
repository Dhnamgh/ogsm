"""
OGSM Portal Main Application Router & Entrypoint.
"""

import streamlit as st
from core.config import load_config
from core.logger import get_logger

logger = get_logger()

# Streamlit Page Configuration
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
        Hệ thống quản trị chiến trị và theo dõi chỉ số **OGSM (Objectives, Goals, Strategies, Measures)**
        được kết nối trực tiếp thời gian thực với **Microsoft OneDrive for Business**.

        ### Hướng Dẫn Sử Dụng
        * **Dashboard:** Xem tổng quan chỉ số KPI và biểu đồ tiến độ.
        * **OGSM Tree:** Xem phân cấp cây mục tiêu chiến lược.
        * **Strategy Tracker:** Cập nhật kết quả thực hiện cho từng chỉ số.
        * **Data Management:** Kiểm tra bảng dữ liệu thô và xuất báo cáo Excel.
        """
    )


if __name__ == "__main__":
    main()
