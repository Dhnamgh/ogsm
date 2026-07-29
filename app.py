import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3

# ==========================
# CONFIG
# ==========================

st.set_page_config(
    page_title="OGSM Portal UMP",
    layout="wide"
)

DB_NAME = "ogsm.db"

UNITS = [
    "P.HCTH",
    "P.QTGT",
    "TT.KCCLXN",
    "TT.KHCN UMP",
    "TT.GDYH",
    "TT.CNTT",
    "KTX",
    "K.KHCB",
    "TRƯỜNG Y",
    "TCYH",
    "P.TCCB",
    "P.CTSV",
    "P.KHCN",
    "P.HTQT",
    "PKCK RHM",
    "T.DƯỢC",
    "P.KHTC",
    "K.YTCC",
    "P.TTPC",
    "THƯ VIỆN",
    "P.ĐTSĐH",
    "BV ĐHYD",
    "TT.YSHPT",
    "P.ĐTĐH",
    "T.ĐD-KTYH",
    "K.RHM",
    "P.ĐBCL",
    "TT.ĐTNLYT"
]

# ==========================
# DATABASE
# ==========================

def get_conn():
    return sqlite3.connect(DB_NAME)

def init_db():

    conn = get_conn()

    conn.execute("""
    CREATE TABLE IF NOT EXISTS kpis(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        unit_name TEXT,

        objective TEXT,

        objective_name TEXT,

        goal_ump TEXT,

        goal_unit TEXT,

        kpi TEXT,

        target_year INTEGER,

        percent REAL,

        status TEXT

    )
    """)

    conn.commit()
    conn.close()

init_db()

# ==========================
# CSS
# ==========================

st.markdown("""
<style>

.block-container{
    padding-top:1rem;
}

.portal-header{
    background:#005b96;
    color:white;
    padding:20px;
    border-radius:12px;
    margin-bottom:20px;
}

.portal-header h1{
    margin:0;
}

</style>
""", unsafe_allow_html=True)

# ==========================
# HEADER
# ==========================

st.markdown("""
<div class="portal-header">
<h1>OGSM PORTAL UMP</h1>
<div>Kế hoạch chiến lược 2025-2030</div>
</div>
""", unsafe_allow_html=True)

# ==========================
# MENU
# ==========================

selected = st.radio(
    "",
    [
        "Dashboard",
        "Upload dữ liệu",
        "Đơn vị",
        "KPI"
    ],
    horizontal=True
)

# ==========================
# DASHBOARD
# ==========================

if selected == "Dashboard":

    conn = get_conn()

    df = pd.read_sql(
        "SELECT * FROM kpis",
        conn
    )

    conn.close()

    if len(df) == 0:

        st.info(
            "Vào Upload dữ liệu để nạp file OGSM."
        )
        st.stop()

    total_kpi = len(df)

    completed = len(
        df[df["status"] == "Hoàn thành"]
    )

    in_progress = len(
        df[df["status"] == "Đang thực hiện"]
    )

    failed = len(
        df[df["status"] == "Không đạt"]
    )

    not_due = len(
        df[df["status"] == "Chưa đến hạn"]
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
            df.groupby("objective")
            ["percent"]
            .mean()
            .reset_index()
        )

        fig1 = px.bar(
            objective_df,
            x="objective",
            y="percent",
            title="Tỷ lệ hoàn thành theo Objective"
        )

        st.plotly_chart(
            fig1,
            use_container_width=True
        )

    with right:

        status_df = (
            df["status"]
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

# ==========================
# UPLOAD
# ==========================

elif selected == "Upload dữ liệu":

    st.subheader("Upload dữ liệu OGSM")

    unit = st.selectbox(
        "Đơn vị",
        UNITS
    )

    uploaded_file = st.file_uploader(
        "Chọn file OGSM",
        type=["xlsx"]
    )

    if uploaded_file:

        df = pd.read_excel(
            uploaded_file,
            sheet_name="Data",
            engine="openpyxl"
        )

        df = df.dropna(
            subset=["Measure (KPI)"]
        )

        conn = get_conn()

        conn.execute(
            "DELETE FROM kpis WHERE unit_name=?",
            (unit,)
        )

        for _, row in df.iterrows():

            conn.execute(
                """
                INSERT INTO kpis
                (
                    unit_name,
                    objective,
                    objective_name,
                    goal_ump,
                    goal_unit,
                    kpi,
                    target_year,
                    percent,
                    status
                )
                VALUES
                (
                    ?,?,?,?,?,?,?,?,?
                )
                """,
                (
                    unit,
                    row["No"],
                    row["Objects"],
                    row["Goals UMP"],
                    row["Goals HCTH"],
                    row["Measure (KPI)"],
                    row["Năm đích"],
                    row["Tỷ lệ đạt (%)"],
                    row["Trạng thái"]
                )
            )

        conn.commit()
        conn.close()

        st.success(
            f"Đã cập nhật {len(df)} KPI cho {unit}"
        )

# ==========================
# ĐƠN VỊ
# ==========================

elif selected == "Đơn vị":

    conn = get_conn()

    df = pd.read_sql(
        "SELECT * FROM kpis",
        conn
    )

    conn.close()

    if len(df) == 0:

        st.info(
            "Chưa có dữ liệu."
        )

    else:

        unit = st.selectbox(
            "Chọn đơn vị",
            sorted(
                df["unit_name"].unique()
            )
        )

        unit_df = df[
            df["unit_name"] == unit
        ]

        st.dataframe(
            unit_df,
            use_container_width=True
        )

# ==========================
# KPI
# ==========================

elif selected == "KPI":

    conn = get_conn()

    df = pd.read_sql(
        "SELECT * FROM kpis",
        conn
    )

    conn.close()

    if len(df) == 0:

        st.info(
            "Chưa có dữ liệu."
        )

    else:

        objective_filter = st.multiselect(
            "Objective",
            sorted(
                df["objective"].unique()
            )
        )

        status_filter = st.multiselect(
            "Trạng thái",
            sorted(
                df["status"].unique()
            )
        )

        search = st.text_input(
            "Tìm KPI"
        )

        view = df.copy()

        if objective_filter:

            view = view[
                view["objective"]
                .isin(objective_filter)
            ]

        if status_filter:

            view = view[
                view["status"]
                .isin(status_filter)
            ]

        if search:

            view = view[
                view["kpi"]
                .str.contains(
                    search,
                    case=False,
                    na=False
                )
            ]

        st.dataframe(
            view,
            use_container_width=True
        )
