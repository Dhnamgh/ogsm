"""
Plotly Chart Builders for OGSM Portal.
Includes Status Donut Chart & 100% Stacked Bar Charts by Unit.
"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import datetime


def create_status_donut_chart(df_status: pd.DataFrame) -> go.Figure:
    if df_status.empty:
        fig = go.Figure()
        fig.update_layout(title="Chưa có dữ liệu trạng thái")
        return fig

    color_map = {
        "Hoàn thành": "#0f4c5c",      # Xanh lam đậm
        "Đang thực hiện": "#fb8b24",  # Cam
        "Không đạt": "#1f5f3e",       # Xanh lá
        "Chưa đến hạn": "#00a8e8",    # Xanh dương
    }

    fig = px.pie(
        df_status,
        names="Status",
        values="Count",
        hole=0.4,
        color="Status",
        color_discrete_map=color_map,
        title="Phân Bố Trạng Thái Thực Hiện Measures",
    )
    fig.update_traces(textinfo="percent+label")
    fig.update_layout(showlegend=True, margin=dict(t=40, b=10, l=10, r=10))
    return fig


def create_stacked_kpi_by_unit_chart(df: pd.DataFrame, current_year_only: bool = False) -> go.Figure:
    """
    Tạo biểu đồ cột chồng 100% (Stacked Bar Chart 100%) theo Đơn vị.
    - current_year_only = False: Biểu đồ cơ cấu KPI giai đoạn 2025–2029
    - current_year_only = True: Biểu đồ tiến độ KPI đến hạn năm hiện hành
    """
    if df.empty or "Unit_Code" not in df.columns:
        fig = go.Figure()
        fig.update_layout(title="Chưa có dữ liệu biểu đồ")
        return fig

    df_calc = df.copy()
    current_year = datetime.datetime.now().year

    # Lọc theo năm đích nếu chọn hiển thị đến năm hiện hành
    if current_year_only and "Target_Year" in df_calc.columns:
        df_calc["Target_Year_Num"] = pd.to_numeric(df_calc["Target_Year"], errors="coerce").fillna(2029)
        df_calc = df_calc[df_calc["Target_Year_Num"] <= current_year]

    if df_calc.empty:
        fig = go.Figure()
        fig.update_layout(title=f"Không có KPI nào có hạn đến năm {current_year}")
        return fig

    status_order = ["Hoàn thành", "Đang thực hiện", "Không đạt", "Chưa đến hạn"]
    
    color_map = {
        "Hoàn thành": "#0f4c5c",      # Xanh lam đậm / Navy
        "Đang thực hiện": "#fb8b24",  # Cam
        "Không đạt": "#1f5f3e",       # Xanh lá đậm
        "Chưa đến hạn": "#00a8e8",    # Xanh da trời
    }

    # Gom nhóm theo Đơn vị và Trạng thái
    unit_status = df_calc.groupby(["Unit_Code", "Status"]).size().unstack(fill_value=0)
    
    # Quy đổi sang tỷ lệ % (100% Stacked Bar)
    unit_pct = unit_status.div(unit_status.sum(axis=1), axis=0) * 100

    fig = go.Figure()

    for status in status_order:
        if status in unit_pct.columns:
            fig.add_trace(go.Bar(
                name=f"KPI {status.lower()}",
                x=unit_pct.index,
                y=unit_pct[status],
                marker_color=color_map.get(status, "#757575")
            ))

    # Đổi tiêu đề bỏ số thứ tự biểu đồ
    chart_title = (
        f"Biểu đồ: Tiến độ thực hiện KPI đến hạn theo đơn vị (đến năm {current_year})"
        if current_year_only
        else "Biểu đồ: Cơ cấu thực hiện KPI giai đoạn 2025–2029 theo đơn vị"
    )

    fig.update_layout(
        barmode="stack",
        title=dict(text=f"<b>{chart_title}</b>", font=dict(size=15, color="#1877F2")),
        xaxis_title=None,
        yaxis_title=None,
        yaxis=dict(ticksuffix="%", range=[0, 100]),
        legend=dict(orientation="h", yanchor="bottom", y=-0.35, xanchor="center", x=0.5),
        margin=dict(t=50, b=80, l=10, r=10),
        height=480
    )

    return fig
