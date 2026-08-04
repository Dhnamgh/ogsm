import streamlit as st
import pandas as pd
import plotly.express as px
import requests

from io import BytesIO
from datetime import datetime

from config import (
    TENANT_ID,
    CLIENT_ID,
    CLIENT_SECRET,
    DRIVE_ID,
    DATA_FOLDER_ID,
    TEMPLATE_FOLDER_ID,
    EXPORT_FOLDER_ID,
    ARCHIVE_FOLDER_ID
)

from graph_client import (
    get_access_token,
    graph_headers,
    get_folder_items,
    upload_file
)

st.set_page_config(
    page_title="OGSM Portal UMP",
    layout="wide"
)

UNITS = {
    "P.HCTH": "Phòng Hành chính Tổng hợp",
    "P.QTGT": "Phòng Quản trị Giáo tài",
    "TT.KCCLXN": "Trung tâm Kiểm chuẩn Chất lượng Xét nghiệm",
    "TT.KHCN UMP": "Trung tâm Khoa học Công nghệ UMP",
    "TT.GDYH": "Trung tâm Giáo dục Y học",
    "TT.CNTT": "Trung tâm Công nghệ Thông tin",
    "KTX": "Ký túc xá",
    "K.KHCB": "Khoa Khoa học Cơ bản",
    "TRƯỜNG Y": "Trường Y",
    "TCYH": "Tạp chí Y học",
    "K.YHCT": "Khoa Y học Cổ truyền",
    "P.TCCB": "Phòng Tổ chức Cán bộ",
    "P.CTSV": "Phòng Công tác Sinh viên",
    "P.KHCN": "Phòng Khoa học Công nghệ",
    "P.HTQT": "Phòng Hợp tác Quốc tế",
    "PKCK RHM": "Phòng khám Chuyên khoa Răng Hàm Mặt",
    "T.DƯỢC": "Trường Dược",
    "P.KHTC": "Phòng Kế hoạch Tài chính",
    "K.YTCC": "Khoa Y tế Công cộng",
    "P.TTPC": "Phòng Thanh tra Pháp chế",
    "THƯ VIỆN": "Thư viện",
    "P.ĐTSĐH": "Phòng Đào tạo Sau đại học",
    "BV ĐHYD": "Bệnh viện Đại học Y Dược",
    "TT.YSHPT": "Trung tâm Y Sinh học Phân tử",
    "P.ĐTĐH": "Phòng Đào tạo Đại học",
    "T.ĐD-KTYH": "Trường Điều dưỡng Kỹ thuật Y học",
    "K.RHM": "Khoa Răng Hàm Mặt",
    "P.ĐBCL": "Phòng Đảm bảo Chất lượng giáo dục và Khảo thí",
    "TT.ĐTNLYT": "Trung tâm Đào tạo Nhân lực Y tế theo nhu cầu xã hội"
}

st.markdown(
    """
    <div style="
        background:#005B96;
        color:white;
        padding:20px;
        border-radius:12px;
    ">
        <h1>OGSM PORTAL UMP</h1>
        <p>Kế hoạch chiến lược 2025-2030</p>
    </div>
    """,
    unsafe_allow_html=True
)

menu = st.radio(
    "",
    [
        "Dashboard Toàn trường",
        "Dashboard Đơn vị",
        "Tải mẫu OGSM",
        "Upload dữ liệu",
        "KPI Explorer",
        "Báo cáo"
    ],
    horizontal=True
)


def get_template_file():

    files = get_folder_items(
        TEMPLATE_FOLDER_ID
    )

    if len(files) == 0:
        return None

    return files[0]


def get_data_files():

    return get_folder_items(
        DATA_FOLDER_ID
    )


def load_all_data():

    files = get_data_files()

    all_df = []

    for file in files:

        if not (
            file["name"]
            .lower()
            .endswith(".xlsx")
        ):
            continue

        try:

            download_url = file[
                "@microsoft.graph.downloadUrl"
            ]

            temp_df = pd.read_excel(
                download_url,
                sheet_name="Data"
            )

            if "Tên đơn vị" not in temp_df.columns:

                unit_code = (
                    file["name"]
                    .replace(".xlsx", "")
                )

                temp_df[
                    "Tên đơn vị"
                ] = UNITS.get(
                    unit_code,
                    unit_code
                )

                temp_df[
                    "Mã đơn vị"
                ] = unit_code

            all_df.append(
                temp_df
            )

        except Exception as e:

            st.warning(
                f"Lỗi đọc file "
                f"{file['name']}: {e}"
            )

    if len(all_df) == 0:

        return pd.DataFrame()

    return pd.concat(
        all_df,
        ignore_index=True
    )


def get_unit_submit_status():

    files = get_data_files()

    uploaded_codes = []

    for f in files:

        if (
            f["name"]
            .endswith(".xlsx")
        ):

            uploaded_codes.append(
                f["name"]
                .replace(".xlsx", "")
            )

    rows = []

    for code, name in UNITS.items():

        rows.append(
            {
                "Mã đơn vị": code,
                "Tên đơn vị": name,
                "Trạng thái":
                (
                    "Đã nộp"
                    if code in uploaded_codes
                    else "Chưa nộp"
                )
            }
        )

    return pd.DataFrame(rows)
if menu == "Tải mẫu OGSM":

    st.subheader(
        "Tải mẫu OGSM chuẩn UMP"
    )

    st.info(
        """
        Đây là mẫu OGSM chuẩn của UMP.

        Các đơn vị sử dụng mẫu này để
        cập nhật KPI trước khi tải lên hệ thống.
        """
    )

    template_file = get_template_file()

    if template_file:

        st.link_button(
            "Tải mẫu OGSM",
            template_file["webUrl"]
        )

    else:

        st.error(
            "Không tìm thấy file mẫu."
        )


elif menu == "Upload dữ liệu":

    st.subheader(
        "Upload dữ liệu OGSM"
    )

    unit_code = st.selectbox(
        "Đơn vị",
        list(
            UNITS.keys()
        ),
        format_func=lambda x:
        f"{x} - {UNITS[x]}"
    )

    uploaded_file = st.file_uploader(
        "Chọn file Excel",
        type=["xlsx"]
    )

    if uploaded_file:

        filename = (
            unit_code + ".xlsx"
        )

        existing_files = (
            get_data_files()
        )

        existed = False

        for f in existing_files:

            if (
                f["name"]
                ==
                filename
            ):
                existed = True
                break

        if existed:

            st.warning(
                f"{UNITS[unit_code]} đã có dữ liệu."
            )

            st.info(
                "Dữ liệu mới sẽ ghi đè dữ liệu hiện tại."
            )

            confirm = st.checkbox(
                "Tôi xác nhận cập nhật dữ liệu"
            )

            if confirm:

                try:

                    upload_file(
                        DATA_FOLDER_ID,
                        filename,
                        uploaded_file.getvalue()
                    )

                    st.success(
                        "Đã cập nhật dữ liệu."
                    )

                except Exception as e:

                    st.error(str(e))

        else:

            try:

                upload_file(
                    DATA_FOLDER_ID,
                    filename,
                    uploaded_file.getvalue()
                )

                st.success(
                    "Đã tải dữ liệu lên hệ thống."
                )

            except Exception as e:

                st.error(str(e))


elif menu == "Dashboard Toàn trường":

    st.subheader(
        "Dashboard Toàn trường UMP"
    )

    df = load_all_data()

    if len(df) == 0:

        st.info(
            "Chưa có dữ liệu."
        )

        st.stop()

    total = len(df)

    completed = len(
        df[
            df["Trạng thái"]
            ==
            "Hoàn thành"
        ]
    )

    progress = len(
        df[
            df["Trạng thái"]
            ==
            "Đang thực hiện"
        ]
    )

    failed = len(
        df[
            df["Trạng thái"]
            ==
            "Không đạt"
        ]
    )

    not_due = len(
        df[
            df["Trạng thái"]
            ==
            "Chưa đến hạn"
        ]
    )

    submit_df = (
        get_unit_submit_status()
    )

    submitted = len(
        submit_df[
            submit_df["Trạng thái"]
            ==
            "Đã nộp"
        ]
    )

    not_submitted = len(
        submit_df[
            submit_df["Trạng thái"]
            ==
            "Chưa nộp"
        ]
    )

    c1,c2,c3,c4,c5,c6,c7 = st.columns(7)

    c1.metric(
        "Tổng KPI",
        total
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

    c6.metric(
        "Đã nộp",
        submitted
    )

    c7.metric(
        "Chưa nộp",
        not_submitted
    )

    st.divider()

    if "Tên đơn vị" in df.columns:

        chart_df = (
            df.groupby(
                "Tên đơn vị"
            )
            .size()
            .reset_index(
                name="Số KPI"
            )
        )

        fig = px.bar(
            chart_df,
            x="Số KPI",
            y="Tên đơn vị",
            orientation="h",
            title=
            "Tổng KPI theo đơn vị"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    st.subheader(
        "Tình trạng nộp dữ liệu"
    )

    st.dataframe(
        submit_df,
        use_container_width=True
    )
    elif menu == "Dashboard Đơn vị":

    st.subheader(
        "Dashboard Đơn vị"
    )

    df = load_all_data()

    if len(df) == 0:

        st.info(
            "Chưa có dữ liệu."
        )

        st.stop()

    if "Tên đơn vị" not in df.columns:

        st.error(
            "Không tìm thấy cột Tên đơn vị."
        )

        st.stop()

    unit_name = st.selectbox(
        "Chọn đơn vị",
        sorted(
            df["Tên đơn vị"]
            .dropna()
            .unique()
        )
    )

    unit_df = df[
        df["Tên đơn vị"]
        ==
        unit_name
    ]

    total = len(unit_df)

    completed = len(
        unit_df[
            unit_df["Trạng thái"]
            ==
            "Hoàn thành"
        ]
    )

    progress = len(
        unit_df[
            unit_df["Trạng thái"]
            ==
            "Đang thực hiện"
        ]
    )

    failed = len(
        unit_df[
            unit_df["Trạng thái"]
            ==
            "Không đạt"
        ]
    )

    not_due = len(
        unit_df[
            unit_df["Trạng thái"]
            ==
            "Chưa đến hạn"
        ]
    )

    c1, c2, c3, c4, c5 = st.columns(5)

    c1.metric(
        "Tổng KPI",
        total
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

    left, right = st.columns(2)

    with left:

        status_df = (
            unit_df[
                "Trạng thái"
            ]
            .value_counts()
            .reset_index()
        )

        status_df.columns = [
            "Trạng thái",
            "Số lượng"
        ]

        fig = px.pie(
            status_df,
            values="Số lượng",
            names="Trạng thái",
            title="Phân bố trạng thái KPI"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    with right:

        if (
            "No" in unit_df.columns
            and
            "Tỷ lệ đạt (%)"
            in unit_df.columns
        ):

            objective_df = (
                unit_df.groupby("No")
                ["Tỷ lệ đạt (%)"]
                .mean()
                .reset_index()
            )

            fig = px.bar(
                objective_df,
                x="No",
                y="Tỷ lệ đạt (%)",
                title="Mức độ hoàn thành theo Objective"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

    delayed_df = unit_df[
        unit_df[
            "Trạng thái"
        ]
        .isin(
            [
                "Không đạt",
                "Đang thực hiện"
            ]
        )
    ]

    st.subheader(
        "KPI chậm tiến độ"
    )

    st.dataframe(
        delayed_df,
        use_container_width=True
    )
    elif menu == "KPI Explorer":

    st.subheader(
        "KPI Explorer"
    )

    df = load_all_data()

    if len(df) == 0:

        st.info(
            "Chưa có dữ liệu."
        )

        st.stop()

    unit_filter = st.multiselect(
        "Đơn vị",
        sorted(
            df["Tên đơn vị"]
            .dropna()
            .unique()
        )
    )

    objective_filter = st.multiselect(
        "Objective",
        sorted(
            df["No"]
            .dropna()
            .unique()
        )
    )

    status_filter = st.multiselect(
        "Trạng thái",
        sorted(
            df["Trạng thái"]
            .dropna()
            .unique()
        )
    )

    search = st.text_input(
        "Tìm kiếm KPI"
    )

    view = df.copy()

    if unit_filter:

        view = view[
            view["Tên đơn vị"]
            .isin(unit_filter)
        ]

    if objective_filter:

        view = view[
            view["No"]
            .isin(
                objective_filter
            )
        ]

    if status_filter:

        view = view[
            view["Trạng thái"]
            .isin(
                status_filter
            )
        ]

    if search:

        view = view[
            view[
                "Measure (KPI)"
            ]
            .astype(str)
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


elif menu == "Báo cáo":

    st.subheader(
        "Báo cáo"
    )

    df = load_all_data()

    if len(df) == 0:

        st.info(
            "Chưa có dữ liệu."
        )

        st.stop()

    export_scope = st.selectbox(
        "Phạm vi xuất",
        [
            "Toàn trường"
        ] + sorted(
            df["Tên đơn vị"]
            .dropna()
            .unique()
        ).tolist()
    )

    export_df = df.copy()

    if export_scope != "Toàn trường":

        export_df = export_df[
            export_df["Tên đơn vị"]
            ==
            export_scope
        ]

    output = BytesIO()

    with pd.ExcelWriter(
        output,
        engine="openpyxl"
    ) as writer:

        export_df.to_excel(
            writer,
            sheet_name="Data",
            index=False
        )

    st.download_button(
        label="Xuất Excel",
        data=output.getvalue(),
        file_name="OGSM_Report.xlsx",
        mime=(
            "application/"
            "vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        )
    )

    st.dataframe(
        export_df,
        use_container_width=True
    )
        st.divider()

    st.subheader(
        "Tỷ lệ hoàn thành KPI theo đơn vị"
    )

    if (
        "Tên đơn vị" in df.columns
        and
        "Trạng thái" in df.columns
    ):

        completion_df = (
            df.groupby(
                ["Tên đơn vị", "Trạng thái"]
            )
            .size()
            .unstack(fill_value=0)
            .reset_index()
        )

        if "Hoàn thành" not in completion_df.columns:
            completion_df["Hoàn thành"] = 0

        total_kpi = (
            completion_df
            .iloc[:, 1:]
            .sum(axis=1)
        )

        completion_df[
            "Tỷ lệ hoàn thành"
        ] = (
            completion_df["Hoàn thành"]
            /
            total_kpi
            * 100
        ).round(2)

        completion_df = (
            completion_df
            .sort_values(
                "Tỷ lệ hoàn thành",
                ascending=False
            )
        )

        fig = px.bar(
            completion_df,
            x="Tỷ lệ hoàn thành",
            y="Tên đơn vị",
            orientation="h",
            title="Xếp hạng tỷ lệ hoàn thành KPI"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    st.divider()

    st.subheader(
        "Cơ cấu KPI theo đơn vị"
    )

    status_by_unit = (
        df.groupby(
            [
                "Tên đơn vị",
                "Trạng thái"
            ]
        )
        .size()
        .reset_index(
            name="Số lượng"
        )
    )

    fig = px.bar(
        status_by_unit,
        x="Tên đơn vị",
        y="Số lượng",
        color="Trạng thái",
        title="Cơ cấu trạng thái KPI theo đơn vị"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.divider()

    st.subheader(
        "Mức độ hoàn thành theo Objective"
    )

    if (
        "No" in df.columns
        and
        "Tỷ lệ đạt (%)"
        in df.columns
    ):

        objective_df = (
            df.groupby("No")
            ["Tỷ lệ đạt (%)"]
            .mean()
            .reset_index()
        )

        fig = px.bar(
            objective_df,
            x="No",
            y="Tỷ lệ đạt (%)",
            title="Mức độ hoàn thành theo Objective"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    st.divider()

    st.subheader(
        "KPI chưa đạt hoặc chậm tiến độ"
    )

    delayed_df = df[
        df["Trạng thái"]
        .isin(
            [
                "Không đạt",
                "Đang thực hiện"
            ]
        )
    ]

    st.dataframe(
        delayed_df,
        use_container_width=True
    )

    st.divider()

    st.subheader(
        "Dữ liệu KPI toàn trường"
    )

    st.dataframe(
        df,
        use_container_width=True
    )
