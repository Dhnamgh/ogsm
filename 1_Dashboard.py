"""
Trang Executive Dashboard - Đại học Y Dược TP.HCM
Khôi phục hiển thị dữ liệu và hỗ trợ upload tệp Excel báo cáo trực tiếp.
"""

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import re
import datetime
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Dashboard OGSM - Đại học Y Dược TP.HCM", layout="wide")

st.markdown("""
<style>
    [data-testid="stSidebarNav"] ul li a svg { display: none !important; }
    [data-testid="stSidebarNav"] ul li a {
        border-radius: 8px !important;
        padding: 10px 14px !important;
        margin: 3px 0px !important;
        font-weight: 600 !important;
    }
    .main-banner-blue {
        display: inline-block;
        background: #1877F2;
        color: #ffffff !important;
        padding: 10px 24px;
        border-radius: 8px;
        font-size: 22px;
        font-weight: 700;
        margin-bottom: 20px;
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
    }
</style>
""", unsafe_allow_html=True)


def normalize_code(code_val) -> str:
    if pd.isna(code_val) or code_val is None:
        return ""
    s = str(code_val).upper().replace(".XLSX", "").strip()
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

    service = OGSMService()
    df_all = service.get_full_ogsm_data()

    if isinstance(df_all, pd.DataFrame) and not df_all.empty:
        UNIT_GROUPS = {
            "Tất cả đơn vị": [],
            "Khối Phòng chức năng": ["HCTH", "QTGT", "TCCB", "CTSV", "KHCN", "HTQT", "KHTC", "TTPC", "DTSDH", "DTDH", "DBCL"],
            "Khối Trường / Khoa": ["TRUONGY", "DUOC", "DDKTYH", "KHCB", "YHCT", "YTCC", "RHM"],
            "Khối Bệnh viện / Phòng khám": ["BVDHYD", "PKCKRHM", "PKRHM"],
            "Khối Trung tâm": ["TTKCCLXN", "TTKC", "TTKHCNUMP", "TTGDYH", "TTCNTT", "TTYSHPT", "TTDTNLYT"],
            "Đơn vị khác": ["KTX", "TCYH", "THUVIEN"]
        }

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

        df_filtered = df_all.copy()
        if selected_group != "Tất cả đơn vị":
            target_norm_codes = UNIT_GROUPS[selected_group]
            df_filtered = df_all[df_all["Norm_Code"].isin(target_norm_codes)]

        # Hiển thị số liệu KPIs
        kpis = OGSMAnalyticsService.compute_summary_kpis(df_filtered)
        render_metrics_cards(kpis)

        st.markdown("---")

        col_left, col_right = st.columns([0.8, 1.2])

        with col_left:
            df_status = OGSMAnalyticsService.get_status_distribution(df_filtered)
            fig_donut = create_status_donut_chart(df_status)
            st.plotly_chart(fig_donut, use_container_width=True)

        with col_right:
            fig_obj = create_objective_progress_chart(df_filtered)
            st.plotly_chart(fig_obj, use_container_width=True)

        st.markdown("---")
        fig_bar_all = create_stacked_kpi_by_unit_chart(df_filtered, current_year_only=False)
        st.plotly_chart(fig_bar_all, use_container_width=True)

    else:
        st.info("💡 Chưa có tệp dữ liệu báo cáo nào trong bộ nhớ. Thầy vui lòng tải lên các file Excel báo cáo dưới đây:")
        uploaded_files = st.file_uploader(
            "Chọn một hoặc nhiều file Excel (.xlsx) để nạp vào hệ thống:",
            type=["xlsx"],
            accept_multiple_files=True,
            key="dashboard_direct_uploader"
        )
        if uploaded_files:
            success_count = 0
            for file in uploaded_files:
                if service.upload_unit_file(file.name, file.getvalue()):
                    success_count += 1
            if success_count > 0:
                st.success(f"Đã nạp thành công {success_count} file báo cáo!")
                st.rerun()

except Exception as e:
    st.error(f"Lỗi nạp trang Dashboard: {e}")
