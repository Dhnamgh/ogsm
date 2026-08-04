"""
OGSM Dynamic Cascade Tree Page.
"""

import streamlit as st
from services.ogsm_service import OGSMService

st.set_page_config(page_title="Cấu Trúc OGSM | OGSM Portal", layout="wide")

st.title("Sơ Đồ Cấu Trúc OGSM (Cascade Hierarchy)")

try:
    service = OGSMService()
    df = service.get_full_ogsm_data()

    if not df.empty:
        objectives = df["Objective_ID"].dropna().unique()

        selected_obj = st.selectbox("Chọn Objective (Mục Tiêu Tổng Thể):", objectives)

        if selected_obj:
            df_obj = df[df["Objective_ID"] == selected_obj]
            obj_title = df_obj["Objective_Title"].iloc[0] if "Objective_Title" in df_obj else ""
            
            st.subheader(f"Mục Tiêu: {selected_obj} - {obj_title}")

            goals = df_obj["Goal_ID"].dropna().unique()
            for g in goals:
                df_g = df_obj[df_obj["Goal_ID"] == g]
                g_desc = df_g["Goal_Desc"].iloc[0] if "Goal_Desc" in df_g else ""
                
                with st.expander(f"Goal: {g} - {g_desc}", expanded=True):
                    strategies = df_g["Strategy_ID"].dropna().unique()
                    for s in strategies:
                        df_s = df_g[df_g["Strategy_ID"] == s]
                        s_desc = df_s["Strategy_Desc"].iloc[0] if "Strategy_Desc" in df_s else ""
                        st.markdown(f"**Strategy [{s}]:** {s_desc}")

                        # Measures Table
                        m_cols = ["Measure_ID", "Measure_Desc", "Unit", "Target", "Actual", "Owner", "Status"]
                        available_m = [c for c in m_cols if c in df_s.columns]
                        st.table(df_s[available_m])
    else:
        st.info("Chưa có dữ liệu OGSM.")

except Exception as e:
    st.error(f"Lỗi truy xuất sơ đồ OGSM: {e}")
