import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="OGSM Portal UMP", layout="wide")

UNITS = [
    "P.HCTH","P.QTGT","TT.KCCLXN","TT.KHCN UMP","TT.GDYH","TT.CNTT",
    "KTX","K.KHCB","TRƯỜNG Y","TCYH","P.TCCB","P.CTSV","P.KHCN",
    "P.HTQT","PKCK RHM","T.DƯỢC","P.KHTC","K.YTCC","P.TTPC",
    "THƯ VIỆN","P.ĐTSĐH","BV ĐHYD","TT.YSHPT","P.ĐTĐH",
    "T.ĐD-KTYH","K.RHM","P.ĐBCL","TT.ĐTNLYT"
]

st.markdown("""
<div style='background:#005b96;color:white;padding:20px;border-radius:12px;'>
<h1>OGSM PORTAL UMP</h1>
<p>Kế hoạch chiến lược 2025-2030</p>
</div>
""", unsafe_allow_html=True)

menu = st.radio('', ['Dashboard','Upload dữ liệu','Đơn vị','KPI','Báo cáo'], horizontal=True)

if 'all_units' not in st.session_state:
    st.session_state.all_units = {}

if menu == 'Upload dữ liệu':
    unit = st.selectbox('Đơn vị', UNITS)
    uploaded_file = st.file_uploader('Chọn file OGSM', type=['xlsx'])

    if uploaded_file:
        df = pd.read_excel(uploaded_file, sheet_name='Data', engine='openpyxl')
        df = df.dropna(subset=['Measure (KPI)'])
        df['Đơn vị'] = unit
        st.session_state.all_units[unit] = df
        st.success(f'Đã nạp {len(df)} KPI cho {unit}')

elif menu == 'Dashboard':

    if len(st.session_state.all_units) == 0:
        st.info('Vào Upload dữ liệu để nạp file OGSM.')
    else:
        df = pd.concat(st.session_state.all_units.values(), ignore_index=True)

        total = len(df)
        completed = len(df[df['Trạng thái']=='Hoàn thành'])
        progress = len(df[df['Trạng thái']=='Đang thực hiện'])
        failed = len(df[df['Trạng thái']=='Không đạt'])
        not_due = len(df[df['Trạng thái']=='Chưa đến hạn'])

        uploaded_units = len(st.session_state.all_units)
        not_uploaded = 28 - uploaded_units

        cols = st.columns(7)
        metrics = [total,completed,progress,failed,not_due,uploaded_units,not_uploaded]
        labels = ['Tổng KPI','Hoàn thành','Đang thực hiện','Không đạt','Chưa đến hạn','Đã nộp','Chưa nộp']
        for c,l,v in zip(cols,labels,metrics):
            c.metric(l,v)

        left,right = st.columns(2)

        with left:
            obj = df.groupby('No')['Tỷ lệ đạt (%)'].mean().reset_index()
            st.plotly_chart(px.bar(obj,x='No',y='Tỷ lệ đạt (%)',title='Tỷ lệ hoàn thành theo Objective'), use_container_width=True)

        with right:
            status = df['Trạng thái'].value_counts().reset_index()
            status.columns=['Trạng thái','Số lượng']
            st.plotly_chart(px.pie(status,values='Số lượng',names='Trạng thái',title='Phân bố trạng thái KPI'), use_container_width=True)

elif menu == 'Đơn vị':
    if len(st.session_state.all_units)==0:
        st.info('Chưa có dữ liệu.')
    else:
        unit = st.selectbox('Chọn đơn vị', sorted(st.session_state.all_units.keys()))
        unit_df = st.session_state.all_units[unit]
        st.dataframe(unit_df, use_container_width=True)

elif menu == 'KPI':
    if len(st.session_state.all_units)==0:
        st.info('Chưa có dữ liệu.')
    else:
        df = pd.concat(st.session_state.all_units.values(), ignore_index=True)

        objective = st.multiselect('Objective', sorted(df['No'].dropna().unique()))
        status = st.multiselect('Trạng thái', sorted(df['Trạng thái'].dropna().unique()))
        goal = st.multiselect('Goal UMP', sorted(df['Goals UMP'].dropna().unique()))
        search = st.text_input('Tìm KPI')

        view = df.copy()
        if objective:
            view = view[view['No'].isin(objective)]
        if status:
            view = view[view['Trạng thái'].isin(status)]
        if goal:
            view = view[view['Goals UMP'].isin(goal)]
        if search:
            view = view[view['Measure (KPI)'].astype(str).str.contains(search, case=False, na=False)]

        st.dataframe(view, use_container_width=True)

elif menu == 'Báo cáo':
    if len(st.session_state.all_units)==0:
        st.info('Chưa có dữ liệu.')
    else:
        df = pd.concat(st.session_state.all_units.values(), ignore_index=True)
        csv = df.to_csv(index=False).encode('utf-8-sig')
        st.download_button('Xuất CSV', csv, 'OGSM_UMP.csv', 'text/csv')
        st.dataframe(df, use_container_width=True)
