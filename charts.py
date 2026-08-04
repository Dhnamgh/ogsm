"""
Plotly Chart Builder components for OGSM visual analysis.
"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd


def create_status_donut_chart(df_status: pd.DataFrame) -> go.Figure:
    """Creates a clean status breakdown pie/donut chart."""
    if df_status.empty:
        fig = go.Figure()
        fig.update_layout(title="Chưa có dữ liệu trạng thái")
        return fig

    color_map = {
        "Completed": "#2e7d32",
        "In Progress": "#0288d1",
        "Not Started": "#757575",
        "Delayed": "#c62828"
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


def create_owner_progress_bar_chart(df: pd.DataFrame) -> go.Figure:
    """Creates a horizontal bar chart comparing measure completion rate by owner/department."""
    if df.empty:
        return go.Figure()

    df_calc = df.copy()
    targets = df_calc["Target"].replace(0, 1.0)
    df_calc["Completion"] = (df_calc["Actual"] / targets) * 100.0
    df_calc["Completion"] = df_calc["Completion"].clip(0.0, 100.0)

    grouped = df_calc.groupby("Owner")["Completion"].mean().reset_index()
    grouped = grouped.sort_values(by="Completion", ascending=True)

    fig = px.bar(
        grouped,
        x="Completion",
        y="Owner",
        orientation="h",
        labels={"Completion": "Tỷ Lệ Hoàn Thành (%)", "Owner": "Đơn Vị Phụ Trách"},
        title="Tỷ Lệ Hoàn Thành Theo Đơn Vị Phụ Trách",
        color="Completion",
        color_continuous_scale="Blues",
    )
    fig.update_layout(xaxis_range=[0, 100], margin=dict(t=40, b=10, l=10, r=10))
    return fig
