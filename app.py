import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO

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

st.markdown("""
<div style='background:#005b96;color:white;padding:20px;border-radius:12px;'>
<h1>OGSM PORTAL UMP</h1>
<p>Kế hoạch chiến lược 2025-2030</p>
</div>
""", unsafe_allow_html=True)

menu = st.radio(
    '',
    [
        'Dashboard',
        'Tải mẫu OGSM',
        'Upload dữ liệu',
        'Đơn vị',
        'KPI',
        'Báo cáo'
    ],
    horizontal=True
)

if 'all_units' not in st.session_state:
    st.session_state.all_units = {}

# =====================================================
# TẢI MẪU
# =====================================================

if menu == "Tải mẫu OGSM":

    st.subheader("Tải mẫu OGSM chuẩn UMP")

    st.info("""
    Đây là mẫu OGSM chuẩn của UMP.

    Mẫu hiện được xây dựng từ biểu mẫu của
    Phòng Hành chính Tổng hợp.

    Các đơn vị chỉ được cập nhật Goal,
    KPI và các chỉ tiêu đã được Ban Giám hiệu
    phê duyệt trước khi tải lên hệ thống.
    """)

    try:

        with open(
            "OGSM_TEMPLATE.xlsx",
            "rb"
        ) as f:

            st.download_button(
                "Tải mẫu OGSM",
                f,
                file_name="OGSM_TEMPLATE.xlsx"
            )

    except:

        st.error(
            "Chưa tìm thấy file OGSM_TEMPLATE.xlsx"
        )

# =====================================================
# UPLOAD
# =====================================================

elif menu == 'Upload dữ liệu':

    unit_code = st.selectbox(
        "Đơn vị",
        list(UNITS.keys()),
        format_func=lambda x: f"{x} - {UNITS[x]}"
    )

    uploaded_file = st.file_uploader(
        'Chọn file OGSM',
        type=['xlsx']
    )

    if uploaded_file:

        df = pd.read_excel(
            uploaded_file,
            sheet_name='Data',
            engine='openpyxl'
        )

        df = df.dropna(
            subset=['Measure (KPI)']
        )

        df["Mã đơn vị"] = unit_code
        df["Tên đơn vị"] = UNITS[unit_code]

        st.session_state.all_units[
            unit_code
        ] = df

        st.success(
            f'Đã nạp {len(df)} KPI cho {UNITS[unit_code]}'
        )

# =====================================================
# DASHBOARD TOÀN TRƯỜNG
# =====================================================

elif menu == 'Dashboard':

    st.subheader(
        "Dashboard Toàn trường UMP"
    )

    if len(
        st.session_state.all_units
    ) == 0:

        st.info(
            'Vào Upload dữ liệu để nạp file OGSM.'
        )

    else:

        df = pd.concat(
            st.session_state.all_units.values(),
            ignore_index=True
        )

        total = len(df)

        completed = len(
            df[
                df['Trạng thái']
                == 'Hoàn thành'
            ]
        )

        progress = len(
            df[
                df['Trạng thái']
                == 'Đang thực hiện'
            ]
        )

        failed = len(
            df[
                df['Trạng thái']
                == 'Không đạt'
            ]
        )

        not_due = len(
            df[
                df['Trạng thái']
                == 'Chưa đến hạn'
            ]
        )

        uploaded_units = len(
            st.session_state.all_units
        )

        not_uploaded = (
            29 - uploaded_units
        )

        cols = st.columns(7)

        metrics = [
            total,
            completed,
            progress,
            failed,
            not_due,
            uploaded_units,
            not_uploaded
        ]

        labels = [
            'Tổng KPI',
            'Hoàn thành',
            'Đang thực hiện',
            'Không đạt',
            'Chưa đến hạn',
            'Đã nộp',
            'Chưa nộp'
        ]

        for c, l, v in zip(
            cols,
            labels,
            metrics
        ):
            c.metric(l, v)

        left, right = st.columns(2)

        with left:

            obj = (
                df.groupby('No')
                ['Tỷ lệ đạt (%)']
                .mean()
                .reset_index()
            )

            fig = px.bar(
                obj,
                x='No',
                y='Tỷ lệ đạt (%)',
                title='Tỷ lệ hoàn thành theo Objective'
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        with right:

            status = (
                df['Trạng thái']
                .value_counts()
                .reset_index()
            )

            status.columns = [
                'Trạng thái',
                'Số lượng'
            ]

            fig2 = px.pie(
                status,
                values='Số lượng',
                names='Trạng thái',
                title='Phân bố trạng thái KPI'
            )

            st.plotly_chart(
                fig2,
                use_container_width=True
            )

# =====================================================
# ĐƠN VỊ
# =====================================================

elif menu == 'Đơn vị':

    if len(
        st.session_state.all_units
    ) == 0:

        st.info(
            'Chưa có dữ liệu.'
        )

    else:

        unit = st.selectbox(
            'Chọn đơn vị',
            sorted(
                st.session_state.all_units.keys()
            ),
            format_func=lambda x:
            f"{x} - {UNITS[x]}"
        )

        unit_df = st.session_state.all_units[
            unit
        ]

        st.subheader(
            f"Dashboard - {UNITS[unit]}"
        )

        st.dataframe(
            unit_df,
            use_container_width=True
        )

# =====================================================
# KPI
# =====================================================

elif menu == 'KPI':

    if len(
        st.session_state.all_units
    ) == 0:

        st.info(
            'Chưa có dữ liệu.'
        )

    else:

        df = pd.concat(
            st.session_state.all_units.values(),
            ignore_index=True
        )

        objective = st.multiselect(
            'Objective',
            sorted(
                df['No']
                .dropna()
                .unique()
            )
        )

        status = st.multiselect(
            'Trạng thái',
            sorted(
                df['Trạng thái']
                .dropna()
                .unique()
            )
        )

        goal = st.multiselect(
            'Goal UMP',
            sorted(
                df['Goals UMP']
                .dropna()
                .unique()
            )
        )

        search = st.text_input(
            'Tìm KPI'
        )

        view = df.copy()

        if objective:

            view = view[
                view['No']
                .isin(objective)
            ]

        if status:

            view = view[
                view['Trạng thái']
                .isin(status)
            ]

        if goal:

            view = view[
                view['Goals UMP']
                .isin(goal)
            ]

        if search:

            view = view[
                view['Measure (KPI)']
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

# =====================================================
# BÁO CÁO
# =====================================================

elif menu == 'Báo cáo':

    if len(
        st.session_state.all_units
    ) == 0:

        st.info(
            'Chưa có dữ liệu.'
        )

    else:

        df = pd.concat(
            st.session_state.all_units.values(),
            ignore_index=True
        )

        output = BytesIO()

        with pd.ExcelWriter(
            output,
            engine="openpyxl"
        ) as writer:

            df.to_excel(
                writer,
                sheet_name="Data",
                index=False
            )

        st.download_button(
            label="Xuất Excel",
            data=output.getvalue(),
            file_name="OGSM_UMP.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        st.dataframe(
            df,
            use_container_width=True
        )
