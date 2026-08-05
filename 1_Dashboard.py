"""
Trang Executive Dashboard - Đại học Y Dược TP.HCM
Khôi phục gọi dữ liệu gốc từ OneDrive qua OGSMService / ExcelRepository.
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


def normalize_code(code_str: str) -> str:
    """Rút gọn mã đơn vị để khớp dữ liệu OneDrive chính xác tuyệt đối."""
    if not code_str:
        return ""
    s = str(code_str).upper().replace(".XLSX", "").strip()
    s = re.sub(r"^(P\.|T\.|K\.|TT\.|PK\.|BV\.)", "", s)
    s = re.sub(r"[^\w]", "", s)
    return s


try:
    from ogsm_service import OGSMService
    from analytics_service import OGSMAnalyticsService
    from metrics_cards import render_metrics_cards
    from charts import (
        create_status_donut_chart, 
        create_objective_progress_chart, 
        create_stacked_kpi_by_unit_chart
    )

    st.markdown('<div class="main-banner-blue">Tổng Quan Thực Hiện OGSM - Đại học Y Dược TP.HCM</div>', unsafe_allow_html=True)

    UNIT_GROUPS = {
        "Tất cả đơn vị": [],
        "Khối Phòng chức năng": ["HCTH", "QTGT", "TCCB", "CTSV", "KHCN", "HTQT", "KHTC", "TTPC", "DTSDH", "DTDH", "DBCL"],
        "Khối Trường / Khoa": ["TRUONGY", "DUOC", "DDKTYH", "KHCB", "YHCT", "YTCC", "RHM"],
        "Khối Bệnh viện / Phòng khám": ["BVDHYD", "PKCKRHM", "PKRHM"],
        "Khối Trung tâm": ["TTKCCLXN", "TTKC", "TTKHCNUMP", "TTGDYH", "TTCNTT", "TTYSHPT", "TTDTNLYT"],
        "Đơn vị khác": ["KTX", "TCYH", "THUVIEN"]
    }

    # Nạp dữ liệu từ OGSMService
    service = OGSMService()
    df_all = service.get_full_ogsm_data()

    if df_all is not None and not df_all.empty:
        # Tạo cột mã chuẩn hóa để so sánh chính xác với khối
        if "Unit_Code" in df_all.columns:
            df_all["Norm_Code"] = df_all["Unit_Code"].apply(normalize_code)
        else:
            df_all["Norm_Code"] = ""

        st.markdown('<div class="subsection-header-blue">Chọn Khối Đơn Vị Báo Cáo</div>', unsafe_allow_html=True)
        
        selected_group = st.radio(
            "Chọn Khối:",
            options=list(UNIT_GROUPS.keys()),
            horizontal=True,
            label_visibility="collapsed",
            key="dash_main_group_radio"
        )

        selected_unit = "Tất cả đơn vị"

        if selected_group == "Tất cả đơn vị":
            selected_unit = "Tất Cả Đơn Vị (Toàn Trường)"
            st.caption("Đại học Y Dược TP. Hồ Chí Minh - Báo Cáo Tổng Hợp Toàn Trường")
        else:
            group_targets = UNIT_GROUPS[selected_group]
            df_group_available = df_all[df_all["Norm_Code"].isin(group_targets)]
            available_units_real = sorted(list(df_group_available["Unit_Code"].unique())) if "Unit_Code" in df_group_available.columns else []
            
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
                selected_unit = f"GROUP:{selected_group}"

        # Lọc dữ liệu
        df_filtered = df_all.copy()
        if selected_unit == "Tất Cả Đơn Vị (Toàn Trường)":
            pass
        elif selected_unit.startswith("GROUP:"):
            g_name = selected_unit.replace("GROUP:", "")
            target_norm_codes = UNIT_GROUPS[g_name]
            df_filtered = df_all[df_all["Norm_Code"].isin(target_norm_codes)]
            st.caption(f"Báo Cáo Tổng Hợp: **{g_name}**")
        else:
            df_filtered = df_all[df_all["Unit_Code"] == selected_unit]
            st.caption(f"Báo Cáo Tiến Độ Đơn Vị: **{selected_unit}**")

        # Hiển thị số liệu tổng quan
        kpis = OGSMAnalyticsService.compute_summary_kpis(df_filtered)
        render_metrics_cards(kpis)

        st.markdown("---")

        # Hiển thị biểu đồ trạng thái và biểu đồ Objectives (O)
        col_left, col_right = st.columns([0.8, 1.2])

        with col_left:
            df_status = OGSMAnalyticsService.get_status_distribution(df_filtered)
            fig_donut = create_status_donut_chart(df_status)
            st.plotly_chart(fig_donut, use_container_width=True)

        with col_right:
            fig_obj = create_objective_progress_chart(df_filtered)
            st.plotly_chart(fig_obj, use_container_width=True)

        st.markdown("---")

        # Biểu đồ cơ cấu thực hiện giai đoạn 2025-2029
        fig_bar_all = create_stacked_kpi_by_unit_chart(df_filtered, current_year_only=False)
        st.plotly_chart(fig_bar_all, use_container_width=True)

        st.markdown("---")

        # Biểu đồ tiến độ đến hạn năm hiện hành
        current_yr = datetime.datetime.now().year
        st.markdown(f'<div class="section-banner-blue">Thống Kê Tiến Độ Đến Hạn Năm Hiện Hành ({current_yr})</div>', unsafe_allow_html=True)
        
        fig_bar_current = create_stacked_kpi_by_unit_chart(df_filtered, current_year_only=True)
        st.plotly_chart(fig_bar_current, use_container_width=True)

    else:
        st.warning("Không tìm thấy file dữ liệu đơn vị nào từ OneDrive.")

except Exception as e:
    st.error(f"Lỗi nạp trang Dashboard: {e}")
