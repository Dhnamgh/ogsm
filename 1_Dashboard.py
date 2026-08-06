"""
Trang Executive Dashboard - Đại học Y Dược TP.HCM
Chuẩn hóa 100% tên tệp về Bảng 29 Mã Đơn Vị chính thức (Khắc phục triệt để lỗi khoảng trắng, Unicode Đ/đ).
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

# BẢNG TRA CỨU KHÓA SIÊU SẠCH CHO ĐÚNG 29 ĐƠN VỊ CỦA NHÀ TRƯỜNG
CANONICAL_LOOKUP = {
    # 1. Khối Phòng chức năng (11 Đơn vị)
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

    # 2. Khối Trường / Khoa (7 Đơn vị)
    "TRUONGY": ("TRƯỜNG Y", "Khối Trường / Khoa"),
    "TDUOC": ("T.DƯỢC", "Khối Trường / Khoa"),
    "TDDKTYH": ("T.ĐĐ-KTYH", "Khối Trường / Khoa"),
    "KKHCB": ("K.KHCB", "Khối Trường / Khoa"),
    "KYHCT": ("K.YHCT", "Khối Trường / Khoa"),
    "KYTCC": ("K.YTCC", "Khối Trường / Khoa"),
    "KRHM": ("K.RHM", "Khối Trường / Khoa"),

    # 3. Khối Trung tâm (6 Đơn vị)
    "TTKCCLXN": ("TT.KCCLXN", "Khối Trung tâm"),
    "TTKHCNUMP": ("TT.KHCN UMP", "Khối Trung tâm"),
    "TTGDYH": ("TT.GDYH", "Khối Trung tâm"),
    "TTCNTT": ("TT.CNTT", "Khối Trung tâm"),
    "TTYSHPT": ("TT.YSHPT", "Khối Trung tâm"),
    "TTDTNLYT": ("TT.ĐTNLYT", "Khối Trung tâm"),

    # 4. Khối Bệnh viện / Phòng khám (2 Đơn vị)
    "PKCKRHM": ("PKCK RHM", "Khối Bệnh viện / Phòng khám"),
    "BVDHYD": ("BV ĐHYD", "Khối Bệnh viện / Phòng khám"),

    # 5. Khối Đơn vị khác (3 Đơn vị)
    "TCYH": ("TCYH", "Đơn vị khác"),
    "THUVIEN": ("THƯ VIỆN", "Đơn vị khác"),
    "KTX": ("KTX", "Đơn vị khác"),
}

def parse_unit_info(raw_filename: str):
    """
    Rút gọn tên tệp bất kỳ về chuỗi ký tự Anh và trả về (Mã_Đơn_Vị_Chuẩn, Khối)
    """
    if not raw_filename:
        return ("Chưa rõ", "Đơn vị khác")
    
    # 1. Bỏ đuôi file .xlsx
    s = re.sub(r'\.xlsx$', '', str(raw_filename).strip(), flags=re.IGNORECASE)
    
    # 2. Xóa toàn bộ dấu tiếng Việt & ép chữ Đ -> D
    clean = unicodedata.normalize('NFD', s)
    clean = ''.join(c for c in clean if unicodedata.category(c) != 'Mn')
    clean = clean.replace('đ', 'd').replace('Đ', 'D').upper()
    
    # 3. Chỉ giữ lại chữ cái A-Z và số 0-9
    key = re.sub(r'[^A-Z0-9]', '', clean)
    
    # Tra cứu chính xác key
    if key in CANONICAL_LOOKUP:
        return CANONICAL_LOOKUP[key]
        
    # Tra cứu tìm từ khóa phụ
    for k, val in CANONICAL_LOOKUP.items():
        if k in key or key in k:
            return val
            
    return (s, "Đơn vị khác")


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
        # Gán Mã chuẩn & Khối chính xác 100%
        parsed_data = df_all["Unit_Code"].apply(parse_unit_info)
        df_all["Unit_Code"] = [p[0] for p in parsed_data]
        df_all["Unit_Group"] = [p[1] for p in parsed_data]

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

        # Lọc dữ liệu hiển thị
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

        # 1. Biểu đồ tròn Trạng thái & Biểu đồ Objectives (O)
        col_donut, col_obj = st.columns([0.8, 1.2])
        with col_donut:
            df_status = OGSMAnalyticsService.get_status_distribution(df_filtered)
            fig_donut = create_status_donut_chart(df_status)
            st.plotly_chart(fig_donut, use_container_width=True)

        with col_obj:
            fig_obj = create_objective_progress_chart(df_filtered)
            st.plotly_chart(fig_obj, use_container_width=True)

        st.markdown("---")

        # 2. Biểu đồ Cơ cấu thực hiện KPI giai đoạn 2025-2030 theo đơn vị
        fig_bar_all = create_stacked_kpi_by_unit_chart(df_filtered, current_year_only=False)
        st.plotly_chart(fig_bar_all, use_container_width=True)

        st.markdown("---")

        # 3. Biểu đồ Tiến độ thực hiện KPI đến hạn năm hiện hành
        current_yr = datetime.datetime.now().year
        fig_bar_current = create_stacked_kpi_by_unit_chart(df_filtered, current_year_only=True)
        st.plotly_chart(fig_bar_current, use_container_width=True)

        st.markdown("---")

        # 4. THÊM 3 BIỂU ĐỒ NGANG THEO ĐƠN VỊ
        st.markdown('<div class="section-banner-blue">Thống Kê Chi Tiết Số Lượng & Tỷ Lệ Hoàn Thành Theo Đơn Vị</div>', unsafe_allow_html=True)

        # Biểu đồ 4.1: Tổng số KPI theo đơn vị
        fig_total_kpis = create_total_kpis_by_unit_chart(df_filtered)
        st.plotly_chart(fig_total_kpis, use_container_width=True)

        st.markdown("---")

        # Biểu đồ 4.2: Tỷ lệ hoàn thành theo đơn vị năm hiện hành
        fig_rate_current = create_completion_rate_by_unit_chart(df_filtered, current_year_only=True)
        st.plotly_chart(fig_rate_current, use_container_width=True)

        st.markdown("---")

        # Biểu đồ 4.3: Tỷ lệ hoàn thành theo đơn vị cả giai đoạn 2025–2030
        fig_rate_all = create_completion_rate_by_unit_chart(df_filtered, current_year_only=False)
        st.plotly_chart(fig_rate_all, use_container_width=True)

    else:
        st.warning("Không tìm thấy file dữ liệu đơn vị nào trong thư mục DATA trên OneDrive.")

except Exception as e:
    st.error(f"Lỗi nạp trang Dashboard: {e}")
