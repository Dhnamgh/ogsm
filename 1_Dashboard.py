"""
Trang Executive Dashboard - Đại học Y Dược TP.HCM
Sử dụng Danh sách Ánh xạ Cứng (Hardcoded Mapping) 29 Đơn vị chính thức.
"""

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import re
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

# BẢNG ÁNH XẠ CỨNG 29 ĐƠN VỊ THEO KHỐI
UNIT_MASTER_MAP = {
    # Khối Phòng chức năng (11 Đơn vị)
    "P.HCTH": "Khối Phòng chức năng",
    "P.QTGT": "Khối Phòng chức năng",
    "P.TCCB": "Khối Phòng chức năng",
    "P.CTSV": "Khối Phòng chức năng",
    "P.KHCN": "Khối Phòng chức năng",
    "P.HTQT": "Khối Phòng chức năng",
    "P.KHTC": "Khối Phòng chức năng",
    "P.TTPC": "Khối Phòng chức năng",
    "P.ĐTSĐH": "Khối Phòng chức năng",
    "P.DTSDH": "Khối Phòng chức năng",
    "P.ĐTĐH": "Khối Phòng chức năng",
    "P.DTĐH": "Khối Phòng chức năng",
    "P.ĐBCL": "Khối Phòng chức năng",
    "P.DBCL": "Khối Phòng chức năng",

    # Khối Trường / Khoa (7 Đơn vị)
    "TRƯỜNG Y": "Khối Trường / Khoa",
    "TRUONG Y": "Khối Trường / Khoa",
    "T.DƯỢC": "Khối Trường / Khoa",
    "T.DUOC": "Khối Trường / Khoa",
    "T.ĐĐ-KTYH": "Khối Trường / Khoa",
    "T.DD-KTYH": "Khối Trường / Khoa",
    "K.KHCB": "Khối Trường / Khoa",
    "K.YHCT": "Khối Trường / Khoa",
    "K.YTCC": "Khối Trường / Khoa",
    "K.RHM": "Khối Trường / Khoa",

    # Khối Trung tâm (6 Đơn vị)
    "TT.KCCLXN": "Khối Trung tâm",
    "TT.KHCN UMP": "Khối Trung tâm",
    "TT.KHCNUMP": "Khối Trung tâm",
    "TT.GDYH": "Khối Trung tâm",
    "TT.CNTT": "Khối Trung tâm",
    "TT.YSHPT": "Khối Trung tâm",
    "TT.ĐTNLYT": "Khối Trung tâm",
    "TT.DTNLYT": "Khối Trung tâm",

    # Khối Bệnh viện, Phòng khám (2 Đơn vị)
    "PKCK RHM": "Khối Bệnh viện / Phòng khám",
    "PKCKRHM": "Khối Bệnh viện / Phòng khám",
    "BV ĐHYD": "Khối Bệnh viện / Phòng khám",
    "BVDHYD": "Khối Bệnh viện / Phòng khám",

    # Đơn vị khác (3 Đơn vị)
    "TCYH": "Đơn vị khác",
    "THƯ VIỆN": "Đơn vị khác",
    "THU VIEN": "Đơn vị khác",
    "KTX": "Đơn vị khác"
}

def get_unit_group_exact(unit_code: str) -> str:
    """Tra cứu chính xác 100% Khối dựa trên Mã đơn vị"""
    u_clean = str(unit_code).replace(".xlsx", "").strip().upper()
    for key, group in UNIT_MASTER_MAP.items():
        if key.upper() == u_clean:
            return group
    # Fallback cho trường hợp tên file có dạng nhẹ khác
    for key, group in UNIT_MASTER_MAP.items():
        if key.upper() in u_clean or u_clean in key.upper():
            return group
    return "Đơn vị khác"


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
        df_all["Unit_Group"] = df_all["Unit_Code"].apply(get_unit_group_exact)

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

        # Lọc dữ liệu
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
