import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from datetime import datetime

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

st.set_page_config(
    page_title="OGSM Portal UMP",
    layout="wide"
)

# =========================
# DATABASE
# =========================

def get_conn():
    return sqlite3.connect(DB_NAME)

def init_db():

    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
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
        status TEXT,
        upload_date TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()

# =========================
# SIDEBAR
# =========================

menu = st.sidebar.selectbox(
    "Chức năng",
    [
        "Dashboard toàn trường",
        "Dashboard đơn vị",
        "Upload OGSM"
    ]
)

# =========================
# UPLOAD
# =========================

if menu == "Upload OGSM":

    st.title("Upload OGSM")

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
                    status,
                    upload_date
                )
                VALUES (?,?,?,?,?,?,?,?,?,?)
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
                    row["Trạng thái"],
                    datetime.now().strftime("%Y-%m-%d %H:%M")
                )
            )

        conn.commit()
        conn.close()

        st.success(
            f"Đã tải {len(df)} KPI của {unit}"
        )

# =========================
# DASHBOARD TOÀN TRƯỜNG
# =========================

elif menu == "Dashboard toàn trường":

    st.title("Dashboard toàn trường")

    conn = get_conn()

    df = pd.read_sql(
        "SELECT * FROM kpis",
        conn
    )

    conn.close()

    if len(df) == 0:

        st.warning("Chưa có dữ liệu")

    else:

        completed = len(
            df[df["status"] == "Hoàn thành"]
        )

        progress = len(
            df[df["status"] == "Đang thực hiện"]
        )

        failed = len(
            df[df["status"] == "Không đạt"]
        )

        not_due = len(
            df[df["status"] == "Chưa đến hạn"]
        )

        c1,c2,c3,c4,c5 = st.columns(5)

        c1.metric(
            "Tổng KPI",
            len(df)
        )

        c2.metric(
            "Hoàn thành",
            completed
        )

        c3.metric(
            "Đang thực hiện",
            progress
        )

        c4.metric(
            "Không đạt",
            failed
        )

        c5.metric(
            "Chưa đến hạn",
            not_due
        )

        st.subheader(
            "KPI theo đơn vị"
        )

        unit_df = (
            df.groupby("unit_name")
            .size()
            .reset_index(name="KPI")
        )

        fig = px.bar(
            unit_df,
            x="unit_name",
            y="KPI"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        st.subheader(
            "Tỷ lệ hoàn thành theo Objective"
        )

        objective_df = (
            df.groupby("objective")
            ["percent"]
            .mean()
            .reset_index()
        )

        fig2 = px.bar(
            objective_df,
            x="objective",
            y="percent"
        )

        st.plotly_chart(
            fig2,
            use_container_width=True
        )

# =========================
# DASHBOARD ĐƠN VỊ
# =========================

elif menu == "Dashboard đơn vị":

    st.title("Dashboard đơn vị")

    unit = st.selectbox(
        "Chọn đơn vị",
        UNITS
    )

    conn = get_conn()

    df = pd.read_sql(
        """
        SELECT *
        FROM kpis
        WHERE unit_name=?
        """,
        conn,
        params=(unit,)
    )

    conn.close()

    if len(df) == 0:

        st.warning(
            "Đơn vị chưa upload dữ liệu"
        )

    else:

        c1,c2,c3,c4,c5 = st.columns(5)

        c1.metric(
            "Tổng KPI",
            len(df)
        )

        c2.metric(
            "Hoàn thành",
            len(df[df["status"]=="Hoàn thành"])
        )

        c3.metric(
            "Đang thực hiện",
            len(df[df["status"]=="Đang thực hiện"])
        )

        c4.metric(
            "Không đạt",
            len(df[df["status"]=="Không đạt"])
        )

        c5.metric(
            "Chưa đến hạn",
            len(df[df["status"]=="Chưa đến hạn"])
        )

        st.dataframe(
            df,
            use_container_width=True
        )
