import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="OGSM Portal UMP",
    layout="wide"
)

# =====================
# CSS
# =====================

st.markdown("""
<style>

.main {
    background-color: #f5f7fa;
}

.header {
    background-color: #005b96;
    color: white;
    padding: 15px;
    border-radius: 10px;
    margin-bottom: 20px;
}

</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="header">
    <h2>OGSM PORTAL UMP</h2>
    <p>Kế hoạch chiến lược 2025-2030</p>
</div>
""", unsafe_allow_html=True)

# =====================
# UPLOAD
# =====================

uploaded_file = st.file_uploader(
    "Tải file OGSM",
    type=["xlsx"]
)

if uploaded_file:

    try:

        df = pd.read_excel(
            uploaded_file,
            sheet_name="Data",
            engine="openpyxl"
        )

        df = df.dropna(
            subset=["Measure (KPI)"]
        )

        total_kpi = len(df)

        completed = len(
            df[df["Trạng thái"] == "Hoàn thành"]
        )

        in_progress = len(
            df[df["Trạng thái"] == "Đang thực hiện"]
        )

        failed = len(
            df[df["Trạng thái"] == "Không đạt"]
        )

        not_due = len(
            df[df["Trạng thái"] == "Chưa đến hạn"]
        )

        c1, c2, c3, c4, c5 = st.columns(5)

        c1.metric("Tổng KPI", total_kpi)
        c2.metric("Hoàn thành", completed)
        c3.metric("Đang thực hiện", in_progress)
        c4.metric("Không đạt", failed)
        c5.metric("Chưa đến hạn", not_due)

        st.divider()

        st.subheader(
            "Tỷ lệ hoàn thành theo Objective"
        )

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
            color="No"
        )

        st.plotly_chart(
            fig1,
            use_container_width=True
        )

        st.subheader(
            "Phân bố trạng thái KPI"
        )

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
            names="Trạng thái"
        )

        st.plotly_chart(
            fig2,
            use_container_width=True
        )

        st.subheader(
            "Chi tiết KPI"
        )

        objective_filter = st.multiselect(
            "Objective",
            sorted(df["No"].unique())
        )

        if objective_filter:

            df_view = df[
                df["No"].isin(
                    objective_filter
                )
            ]

        else:

            df_view = df

        st.dataframe(
            df_view,
            use_container_width=True,
            height=600
        )

    except Exception as e:

        st.error(str(e))

else:

    st.info(
        "Hãy tải file OGSM Excel để bắt đầu."
    )
