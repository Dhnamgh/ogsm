"""
OGSM Charts Module - Xử lý vẽ các biểu đồ Plotly cho Dashboard.
Đã kiểm tra kỹ lưỡng kiểu dữ liệu để tránh lỗi 'DataFrame' object has no attribute 'str'.
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def create_status_donut_chart(df_status: pd.DataFrame):
    """Vẽ biểu đồ tròn phân bố trạng thái thực hiện."""
    if df_status is None or df_status.empty or "Status" not in df_status.columns:
        fig = go.Figure()
        fig.add_annotation(text="Chưa có dữ liệu trạng thái", showarrow=False, font=dict(size=14))
        fig.update_layout(height=350)
        return fig

    # Màu sắc cố định cho từng trạng thái
    color_map = {
        "Hoàn thành": "#1b4d3e",        # Xanh lục đậm
        "Chưa đến hạn": "#0099e6",      # Xanh dương
        "Đang thực hiện": "#e67e22",     # Cam
        "Không đạt": "#c0392b"          # Đỏ
    }

    fig = px.pie(
        df_status,
        names="Status",
        values="Count",
        hole=0.5,
        title="<b>Biểu đồ: Phân bố trạng thái thực hiện Measures</b>",
        color="Status",
        color_discrete_map=color_map
    )

    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(
        height=380,
        margin=dict(l=20, r=20, t=50, b=20),
        legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.05)
    )
    return fig


def create_objective_progress_chart(df: pd.DataFrame):
    """Vẽ biểu đồ tiến độ thực hiện theo từng Mục tiêu chiến lược (Objectives)."""
    if df is None or df.empty:
        fig = go.Figure()
        fig.add_annotation(text="Chưa có dữ liệu Mục tiêu chiến lược", showarrow=False, font=dict(size=14))
        fig.update_layout(height=380)
        return fig

    # Lấy tên cột Objective
    obj_col = next((c for c in df.columns if any(k in str(c).lower() for k in ["objective", "mục tiêu chiến lược", "mã o", "objective_id"])), None)
    status_col = next((c for c in df.columns if any(k in str(c).lower() for k in ["status", "trạng thái", "tiến độ"])), None)

    if not obj_col or not status_col:
        fig = go.Figure()
        fig.add_annotation(text="Chưa có dữ liệu Mục tiêu chiến lược", showarrow=False, font=dict(size=14))
        fig.update_layout(height=380)
        return fig

    df_plot = df.copy()
    # Chuyển đổi an toàn cột dữ liệu thành chuỗi trước khi gọi .str
    df_plot[obj_col] = df_plot[obj_col].astype(str).str.strip()
    df_plot[status_col] = df_plot[status_col].astype(str).str.strip()

    # Bỏ dòng trống
    df_plot = df_plot[~df_plot[obj_col].isin(["", "nan", "None", "NaN"])]

    if df_plot.empty:
        fig = go.Figure()
        fig.add_annotation(text="Chưa có dữ liệu Mục tiêu chiến lược", showarrow=False, font=dict(size=14))
        fig.update_layout(height=380)
        return fig

    # Nhóm dữ liệu theo Objective và Status
    grouped = df_plot.groupby([obj_col, status_col]).size().reset_index(name="Count")

    color_map = {
        "Hoàn thành": "#1b4d3e",
        "Chưa đến hạn": "#0099e6",
        "Đang thực hiện": "#e67e22",
        "Không đạt": "#c0392b"
    }

    fig = px.bar(
        grouped,
        x=obj_col,
        y="Count",
        color=status_col,
        title="<b>Biểu đồ: Tiến độ thực hiện theo từng Mục tiêu chiến lược (Objectives)</b>",
        color_discrete_map=color_map,
        barmode="stack"
    )

    fig.update_layout(
        height=380,
        xaxis_title="Mục tiêu chiến lược",
        yaxis_title="Số lượng Measures",
        margin=dict(l=20, r=20, t=50, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    return fig


def create_stacked_kpi_by_unit_chart(df: pd.DataFrame, current_year_only: bool = False):
    """Vẽ biểu đồ cột chồng tiến độ thực hiện theo đơn vị."""
    if df is None or df.empty:
        fig = go.Figure()
        fig.add_annotation(text="Chưa có dữ liệu đơn vị", showarrow=False, font=dict(size=14))
        fig.update_layout(height=400)
        return fig

    unit_col = "Unit_Code" if "Unit_Code" in df.columns else None
    status_col = next((c for c in df.columns if any(k in str(c).lower() for k in ["status", "trạng thái", "tiến độ"])), None)

    if not unit_col or not status_col:
        fig = go.Figure()
        fig.add_annotation(text="Chưa có dữ liệu đơn vị", showarrow=False, font=dict(size=14))
        fig.update_layout(height=400)
        return fig

    df_plot = df.copy()
    df_plot[unit_col] = df_plot[unit_col].astype(str).str.strip()
    df_plot[status_col] = df_plot[status_col].astype(str).str.strip()

    grouped = df_plot.groupby([unit_col, status_col]).size().reset_index(name="Count")

    color_map = {
        "Hoàn thành": "#1b4d3e",
        "Chưa đến hạn": "#0099e6",
        "Đang thực hiện": "#e67e22",
        "Không đạt": "#c0392b"
    }

    title_text = "<b>Biểu đồ: Cơ cấu trạng thái thực hiện OGSM theo đơn vị</b>"
    if current_year_only:
        title_text = "<b>Biểu đồ: Cơ cấu trạng thái thực hiện OGSM theo đơn vị (Năm hiện hành)</b>"

    fig = px.bar(
        grouped,
        x=unit_col,
        y="Count",
        color=status_col,
        title=title_text,
        color_discrete_map=color_map,
        barmode="stack"
    )

    fig.update_layout(
        height=450,
        xaxis_title="Đơn vị báo cáo",
        yaxis_title="Số lượng Chỉ số (Measures)",
        margin=dict(l=20, r=20, t=50, b=50),
        xaxis=dict(tickangle=-45)
    )
    return fig
