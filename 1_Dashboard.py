"""
Trang Executive Dashboard - Đại học Y Dược TP.HCM
Chuẩn hóa Unicode (NFC/NFD) và đối soát đa chiều đảm bảo nạp đủ 100% 29 đơn vị.
"""

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import re
import unicodedata
import datetime
import streamlit as st

st.set_page_config(page_title="Dashboard OGSM - Đại học Y Dược TP.HCM", layout="wide")

# CSS giao diện
st.markdown("""
<style>
    [data-testid="stSidebarNav"] ul li a svg { display: none !important; }
    [data-testid="stSidebarNav"] ul li a {
        border-radius: 8px !important;
        padding: 10px 14px !important;
        margin: 3px 0px !important;
        font-weight: 600 !important;
        transition: all 0.2s ease-in-out !important;
    }
    [data-testid="stSidebarNav"] ul li a:hover {
        background-color: #e7f3ff !important;
        color: #1877F2 !important;
        transform: translateX(4px);
    }
    [data-testid="stSidebarNav"] ul li a[aria-current="page"] {
        background-color: #1877F2 !important;
        color: #ffffff !important;
        box-shadow: 0 3px 8px rgba(24, 119, 242, 0.35) !important;
    }
    .main-banner-blue {
        display: inline-block;
        background: #1877F2;
        color: #ffffff !important;
        padding: 10px 24px;
        border-radius: 8px;
        font-size: 22px;
        font-weight: 700;
        box-shadow: 0 4px 10px rgba(24, 119, 242, 0.3);
        margin-bottom: 20px;
    }
    .section-banner-blue {
        display: inline-block;
        background-color: #1877F2;
        color: #ffffff !important;
        padding: 10px 20px;
        border-radius: 8px;
        font-size: 16px;
        font-weight: 700;
        margin: 14px 0px 14px 0px;
        box-shadow: 0 2px 6px rgba(24, 119, 242, 0.25);
    }
    .subsection-header-blue {
        background-color: #ffffff;
        color: #1877F2;
        padding: 8px 14px;
        border-radius: 8px;
        border: 1px solid #e4e6eb;
        font-size: 15px;
        font-weight: 700;
        margin: 8px 0px 10px 0px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.03);
    }
    div[data-testid="stRadio"] > div {
        background-color: #f0f2f5;
        padding: 6px;
        border-radius: 10px;
        border: 1px solid #e4e6eb;
    }
    div[data-testid="stRadio"] label {
        background-color: #ffffff !important;
        border-radius: 8px !important;
        padding: 8px 16px !important;
        margin-right: 6px !important;
        font-weight: 600 !important;
        border: 1px solid #e4e6eb !important;
        transition: all 0.2s ease-in-out !important;
        cursor: pointer !important;
    }
    div[data-testid="stRadio"] label:hover {
        background-color: #e7f3ff !important;
        color: #1877F2 !important;
        border-color: #1877F2 !important;
    }
</style>
""", unsafe_allow_html=True)


def clean_text(text: str) -> str:
    """Đưa chuỗi về dạng chuẩn NFC và loại bỏ khoảng trắng dư thừa"""
    if not text:
        return ""
    # Chuẩn hóa về NFC
    s = unicodedata.normalize('NFC', str(text))
    s = re.sub(r'\.xlsx$', '', s, flags=re.IGNORECASE).strip()
    return s


def get_ascii_key(text: str) -> str:
    """Chuyển chuỗi về dạng ký tự ASCII không dấu thuần túy để so sánh chính xác 100%"""
    s = unicodedata.normalize('NFD', str(text))
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')
    s = s.replace('đ', 'd').replace('Đ', 'D').upper()
    return re.sub(r'[^A-Z0-9]', '', s)


# BẢNG DỮ LIỆU CHUẨN 29 ĐƠN VỊ CỦA TRƯỜNG
MASTER_UNITS_DATA = {
    # Khối Phòng chức năng (11 Đơn vị)
    "PHCTH": ("P.HCTH", "Khối Phòng chức năng"),
    "PQTGT": ("P.QTGT", "Khối Phòng chức năng"),
    "PTCCB": ("P.TCCB", "Khối Phòng chức năng"),
    "PCTSV": ("P.CTSV", "Khối Phòng chức năng"),
    "PKHCN": ("P.KHCN", "Khối Phòng chức năng"),
    "PHTQT": ("P.HTQT", "Khối Phòng chức năng"),
    "PKHTC": ("P.KHTC", "Khối Phòng chức năng"),
    "PTTPC": ("P.TTPC", "Khối Phòng chức năng"),
    "PDTSDH": ("P.ĐTSĐH", "Khối Phòng chức năng"),
    "PDTDH": ("P.ĐTĐH", "Khối Phòng chức năng"),
    "PDBCL": ("P.ĐBCL", "Khối Phòng chức năng"),

    # Khối Trường / Khoa (7 Đơn vị)
    "TRUONGY": ("TRƯỜNG Y", "Khối Trường / Khoa"),
    "TDUOC": ("T.DƯỢC", "Khối Trường / Khoa"),
    "TDDKTYH": ("T.ĐD-KTYH", "Khối Trường / Khoa"),
    "KKHCB": ("K.KHCB", "Khối Trường / Khoa"),
    "KYHCT": ("K.YHCT", "Khối Trường / Khoa"),
    "KYTCC": ("K.YTCC", "Khối Trường / Khoa"),
    "KRHM": ("K.RHM", "Khối Trường / Khoa"),

    # Khối Trung tâm (6 Đơn vị)
    "TTKCCLXN": ("TT.KCCLXN", "Khối Trung tâm"),
    "TTKHCNUMP": ("TT.KHCN UMP", "Khối Trung tâm"),
    "TTKHCN": ("TT.KHCN UMP", "Khối Trung tâm"),
    "TTGDYH": ("TT.GDYH", "Khối Trung tâm"),
    "TTCNTT": ("TT.CNTT", "Khối Trung tâm"),
    "TTYSHPT": ("TT.YSHPT", "Khối Trung tâm"),
    "TTDTNLYT": ("TT.ĐTNLYT", "Khối Trung tâm"),

    # Khối Bệnh viện / Phòng khám (2 Đơn vị)
    "PKCKRHM": ("PKCK RHM", "Khối Bệnh viện / Phòng khám"),
    "BVDHYD": ("BV ĐHYD", "Khối Bệnh viện / Phòng khám"),

    # Đơn vị khác (3 Đơn vị)
    "TCYH": ("TCYH", "Đơn vị khác"),
    "THUVIEN": ("THƯ VIỆN", "Đơn vị khác"),
    "KTX": ("KTX", "Đơn vị khác"),
}


def map_unit_row(row):
    """
    Xác định Tên Đơn Vị Chuẩn & Khối dựa trên ASCII Key của Source_File hoặc Unit_Code.
    """
    src_file = str(row.get("Source_File", ""))
    unit_code = str(row.get("Unit_Code", ""))

    key_src = get_ascii_key(src_file)
    key_unit = get_ascii_key(unit_code)

    # 1. Tra cứu chính xác theo Key ASCII
    for key in [key_src, key_unit]:
        if key in MASTER_UNITS_DATA:
            return MASTER_UNITS_DATA[key]

    # 2. Tìm tương đối nếu có tiền tố / hậu tố
    for target_key, info in MASTER_UNITS_DATA.items():
        if target_key in key_src or target_key in key_unit or key_src in target_key:
            return info

    return (clean_text(unit_code or src_file), "Đơn vị khác")


try:
    from ogsm_service import OGSMService
    from analytics_service import OGSMAnalyticsService
    from metrics_cards import render_metrics_cards
    from charts import (
        create_status_donut_chart, 
        create_objective_progress_chart, 
        create_stacked_kpi_by_unit_chart,
        create_total_kpis_by_unit_chart,
        create_completion_rate_by_unit_chart
    )

    st.markdown('<div class="main-banner-blue">Tổng Quan Thực Hiện OGSM - Đại học Y Dược TP.HCM</div>', unsafe_allow_html=True)

    service = OGSMService()
    df_all = service.get_full_ogsm_data()

    if not df_all.empty:
        # Ánh xạ chuẩn hóa thông tin Đơn vị và Khối
        mapped_data = df_all.apply(map_unit_row, axis=1)
        df_all["Unit_Code"] = [m[0] for m in mapped_data]
        df_all["Unit_Group"] = [m[1] for m in mapped_data]

        GROUPS_LIST = [
            "Tất cả đơn vị",
            "Khối Phòng chức năng",
            "Khối Trường / Khoa",
            "Khối Bệnh viện / Phòng khám",
            "Khối Trung tâm",
            "Đơn vị khác"
        ]

        st.markdown('<div class="subsection-header-blue">Chọn Khối Đơn Vị Báo Cáo</div>', unsafe_allow_html=True)
        
        selected_group = st.radio(
            "Chọn Khối:",
            options=GROUPS_LIST,
            horizontal=True,
            label_visibility="collapsed",
            key="dash_main_group_radio"
        )

        selected_unit = "Tất cả đơn vị"

        if selected_group == "Tất cả đơn vị":
            selected_unit = "Tất Cả Đơn Vị (Toàn Trường)"
            st.caption("Đại học Y Dược TP. Hồ Chí Minh - Báo Cáo Tổng Hợp Toàn Trường (29 Đơn Vị)")
        else:
            df_group_available = df_all[df_all["Unit_Group"] == selected_group]
            available_units_real = sorted(list(df_group_available["Unit_Code"].unique()))
            
            if available_units_real:
                sub_selected = st.radio(
                    f"Chọn đơn vị thuộc [{selected_group}]:",
                    options=[f"Tất cả {selected_group}"] + available_units_real,
                    horizontal=True,
                    key="dash_sub_unit_radio"
                )
                if sub_selected != f"Tất cả {selected_group}":
                    selected_unit = sub_selected
                else:
                    selected_unit = f"GROUP:{selected_group}"
            else:
                st.info(f"Chưa có tệp dữ liệu nào thuộc {selected_group}.")
                selected_unit = f"GROUP:{selected_group}"

        # Lọc dữ liệu chính xác
        df_filtered = df_all.copy()
        if selected_unit == "Tất Cả Đơn Vị (Toàn Trường)":
            pass
        elif selected_unit.startswith("GROUP:"):
            g_name = selected_unit.replace("GROUP:", "")
            df_filtered = df_all[df_all["Unit_Group"] == g_name]
            st.caption(f"Báo Cáo Tổng Hợp: **{g_name}**")
        else:
            df_filtered = df_all[df_all["Unit_Code"] == selected_unit]
            st.caption(f"Báo Cáo Tiến Độ Đơn Vị: **{selected_unit}**")

        kpis = OGSMAnalyticsService.compute_summary_kpis(df_filtered)
        render_metrics_cards(kpis)

        st.markdown("---")

        col_donut, col_obj = st.columns([0.8, 1.2])
        with col_donut:
            df_status = OGSMAnalyticsService.get_status_distribution(df_filtered)
            fig_donut = create_status_donut_chart(df_status)
            st.plotly_chart(fig_donut, use_container_width=True)

        with col_obj:
            fig_obj = create_objective_progress_chart(df_filtered)
            st.plotly_chart(fig_obj, use_container_width=True)

        st.markdown("---")

        fig_bar_all = create_stacked_kpi_by_unit_chart(df_filtered, current_year_only=False)
        st.plotly_chart(fig_bar_all, use_container_width=True)

        st.markdown("---")

        fig_bar_current = create_stacked_kpi_by_unit_chart(df_filtered, current_year_only=True)
        st.plotly_chart(fig_bar_current, use_container_width=True)

        st.markdown("---")

        st.markdown('<div class="section-banner-blue">Thống Kê Chi Tiết Số Lượng & Tỷ Lệ Hoàn Thành Theo Đơn Vị</div>', unsafe_allow_html=True)

        fig_total_kpis = create_total_kpis_by_unit_chart(df_filtered)
        st.plotly_chart(fig_total_kpis, use_container_width=True)

        st.markdown("---")

        fig_rate_current = create_completion_rate_by_unit_chart(df_filtered, current_year_only=True)
        st.plotly_chart(fig_rate_current, use_container_width=True)

        st.markdown("---")

        fig_rate_all = create_completion_rate_by_unit_chart(df_filtered, current_year_only=False)
        st.plotly_chart(fig_rate_all, use_container_width=True)

    else:
        st.warning("Không tìm thấy file dữ liệu đơn vị nào trong thư mục DATA trên OneDrive.")

except Exception as e:
    st.error(f"Lỗi nạp trang Dashboard: {e}")
