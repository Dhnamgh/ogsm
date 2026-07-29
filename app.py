import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_option_menu import option_menu

st.set_page_config(
    page_title="OGSM Portal UMP",
    layout="wide"
)

# =========================
# CSS
# =========================

st.markdown("""
<style>

.block-container{
    padding-top:1rem;
}

.portal-header{
    background:#005B96;
    color:white;
    padding:20px;
    border-radius:12px;
    margin-bottom:20px;
}

.portal-header h1{
    margin:0;
}

.metric-card{
    background:white;
    border-radius:12px;
    padding:16px;
    border:1px solid #E2E8F0;
}

</style>
""", unsafe_allow_html=True)

# =========================
# HEADER
# =========================

st.markdown("""
<div class="portal-header">
    <h1>OGSM PORTAL UMP</h1>
    <div>Kế hoạch chiến lược 2025-2030</div>
</div>
""", unsafe_allow_html=True)

# =========================
# MENU
# =========================

selected = option_menu(
    menu_title=None,
    options=[
        "Dashboard",
        "Upload dữ liệu",
        "Đơn vị",
        "KPI"
    ],
    orientation="horizontal"
)

# =========================
# SESSION
# =========================

if "master_df" not in st.session_state:
    st.session_state.master_df = None

# =========================
# UPLOAD
# =========================

if selected == "Upload dữ liệu":

    st.subheader("Upload dữ liệu OGSM")

    uploaded_files = st.file_uploader(
        "Chọn nhiều file OGSM",
        type=["xlsx"],
        accept_multiple_files=True
    )

    if uploaded_files:

        all_data = []

        for file in uploaded_files:

            try:

                df = pd.read_excel(
                    file,
                    sheet_name="Data",
                    engine="openpyxl"
                )

                df = df.dropna(
                    subset=["Measure (KPI)"]
                )

                unit_name = (
                    file.name
                    .replace(".xlsx", "")
                )

                df["Đơn vị"] = unit_name

                all_data.append(df)

            except Exception as e:

                st.error(
                    f"Lỗi file {file.name}: {e}"
                )

        if all_data:

            master_df = pd.concat(
                all_data,
                ignore_index=True
            )

            st.session_state.master_df = master_df

            st.success(
                f"Đã nạp {len(master_df)} KPI từ {len(uploaded_files)} đơn vị"
            )

# =========================
# DASHBOARD
# =========================

elif selected == "Dashboard":

    if st.session_state.master_df is None:

        st.info(
            "Vào Upload dữ liệu để nạp file OGSM."
        )

    else:

        df = st.session_state.master_df

        total_kpi = len(df)

        completed = len(
            df[df["Trạng thái"]=="Hoàn thành"]
        )

        in_progress = len(
            df[df["Trạng thái"]=="Đang thực hiện"]
        )

        failed = len(
            df[df["Trạng thái"]=="Không đạt"]
        )

        not_due = len(
            df[df["Trạng thái"]=="Chưa đến hạn"]
        )

        c1,c2,c3,c4,c5 = st.columns(5)

        c1.metric("Tổng KPI", total_kpi)
        c2.metric("Hoàn thành", completed)
        c3.metric("Đang thực hiện", in_progress)
        c4.metric("Không đạt", failed)
        c5.metric("Chưa đến hạn", not_due)

        st.divider()

        left,right = st.columns(2)

        with left:

            objective_df = (
                df.groupby("No")
                ["Tỷ lệ đạt (%)"]
                .mean()
                .reset_index()
            )

            fig1 = px.bar(
                objective_df,
                x="No",
                y="Tỷ lệ đạt (%)",
                title="Tỷ lệ hoàn thành theo Objective"
            )

            st.plotly_chart(
                fig1,
                use_container_width=True
            )

        with right:

            status_df = (
                df["Trạng thái"]
                .value_counts()
                .reset_index()
            )

            status_df.columns = [
                "Trạng thái",
                "Số lượng"
            ]

            fig2 = px.pie(
                status_df,
                values="Số lượng",
                names="Trạng thái",
                title="Phân bố trạng thái KPI"
            )

            st.plotly_chart(
                fig2,
                use_container_width=True
            )

# =========================
# ĐƠN VỊ
# =========================

elif selected == "Đơn vị":

    if st.session_state.master_df is None:

        st.info(
            "Chưa có dữ liệu."
        )

    else:

        df = st.session_state.master_df

        units = sorted(
            df["Đơn vị"]
            .unique()
        )

        unit = st.selectbox(
            "Chọn đơn vị",
            units
        )

        unit_df = df[
            df["Đơn vị"] == unit
        ]

        c1,c2,c3,c4,c5 = st.columns(5)

        c1.metric(
            "Tổng KPI",
            len(unit_df)
        )

        c2.metric(
            "Hoàn thành",
            len(
                unit_df[
                    unit_df["Trạng thái"]=="Hoàn thành"
                ]
            )
        )

        c3.metric(
            "Đang thực hiện",
            len(
                unit_df[
                    unit_df["Trạng thái"]=="Đang thực hiện"
                ]
            )
        )

        c4.metric(
            "Không đạt",
            len(
                unit_df[
                    unit_df["Trạng thái"]=="Không đạt"
                ]
            )
        )

        c5.metric(
            "Chưa đến hạn",
            len(
                unit_df[
                    unit_df["Trạng thái"]=="Chưa đến hạn"
                ]
            )
        )

        st.dataframe(
            unit_df,
            use_container_width=True
        )

# =========================
# KPI
# =========================

elif selected == "KPI":

    if st.session_state.master_df is None:

        st.info(
            "Chưa có dữ liệu."
        )

    else:

        df = st.session_state.master_df

        objective_filter = st.multiselect(
            "Objective",
            sorted(
                df["No"].unique()
            )
        )

        status_filter = st.multiselect(
            "Trạng thái",
            sorted(
                df["Trạng thái"].unique()
            )
        )

        search_text = st.text_input(
            "Tìm KPI"
        )

        view = df.copy()

        if objective_filter:

            view = view[
                view["No"].isin(
                    objective_filter
                )
            ]

        if status_filter:

            view = view[
                view["Trạng thái"].isin(
                    status_filter
                )
            ]

        if search_text:

            view = view[
                view["Measure (KPI)"]
                .str.contains(
                    search_text,
                    case=False,
                    na=False
                )
            ]

        st.dataframe(
            view,
            use_container_width=True
        )
