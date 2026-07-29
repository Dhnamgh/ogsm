import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="OGSM UMP",
    layout="wide"
)

st.title("OGSM UMP")

uploaded_file = st.file_uploader(
    "Tải file OGSM (.xlsx)",
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

        st.success("Đọc dữ liệu thành công")

        # ======================
        # KPI CARDS
        # ======================

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

        col1, col2, col3, col4, col5 = st.columns(5)

        col1.metric(
            "Tổng KPI",
            total_kpi
        )

        col2.metric(
            "Hoàn thành",
            completed
        )

        col3.metric(
            "Đang thực hiện",
            in_progress
        )

        col4.metric(
            "Không đạt",
            failed
        )

        col5.metric(
            "Chưa đến hạn",
            not_due
        )

        # ======================
        # OBJECTIVE
        # ======================

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
            y="Tỷ lệ đạt (%)"
        )

        st.plotly_chart(
            fig1,
            use_container_width=True
        )

        # ======================
        # STATUS PIE
        # ======================

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

        # ======================
        # DETAIL
        # ======================

        st.subheader(
            "Chi tiết KPI"
        )

        objective_filter = st.multiselect(
            "Lọc Objective",
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
            use_container_width=True
        )

    except Exception as e:

        st.error(
            f"Lỗi: {str(e)}"
        )

else:

    st.info(
        "Chọn file OGSM để bắt đầu."
    )
