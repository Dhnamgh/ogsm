import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

DB = "ogsm.db"

def get_conn():
    return sqlite3.connect(DB, check_same_thread=False)

def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS objectives (code TEXT PRIMARY KEY,name TEXT)""")
    cur.execute("""CREATE TABLE IF NOT EXISTS ump_goals (goal_code TEXT PRIMARY KEY,objective_code TEXT,goal_name TEXT)""")
    cur.execute("""CREATE TABLE IF NOT EXISTS unit_goals (id INTEGER PRIMARY KEY AUTOINCREMENT,unit_name TEXT,goal_code TEXT,unit_goal_name TEXT)""")
    cur.execute("""CREATE TABLE IF NOT EXISTS kpis (id INTEGER PRIMARY KEY AUTOINCREMENT,unit_name TEXT,objective_code TEXT,goal_code TEXT,kpi_code TEXT,kpi_name TEXT,start_year INTEGER,target_year INTEGER,progress REAL,status TEXT)""")

    cur.execute('SELECT COUNT(*) FROM objectives')
    if cur.fetchone()[0] == 0:
        objectives=[('O1','Giáo dục: Hội nhập và đạt chuẩn quốc tế'),('O2','Nghiên cứu khoa học: Sáng tạo và học thuật'),('O3','Phục vụ cộng đồng: Tinh thần phụng sự và nâng tầm ảnh hưởng'),('O4','Trí tuệ nhân tạo: Thúc đẩy và ứng dụng'),('O5','Quản trị đại học: Hiệu quả, hợp tác và cải tiến liên tục')]
        cur.executemany('INSERT INTO objectives VALUES (?,?)',objectives)
    conn.commit(); conn.close()

def calc_status(progress,target_year):
    y=datetime.now().year
    if progress>=100: return 'Hoàn thành'
    if 0<progress<100: return 'Đang thực hiện'
    if progress==0 and target_year>y: return 'Chưa đến hạn'
    return 'Không đạt'

st.set_page_config(page_title='OGSM UMP',layout='wide')
init_db()

st.title('OGSM UMP MVP')
menu=st.sidebar.radio('Menu',['Dashboard','Thêm KPI','KPI'])

if menu=='Dashboard':
    conn=get_conn()
    df=pd.read_sql('select * from kpis',conn)
    conn.close()
    st.metric('Tổng KPI',len(df))
    st.dataframe(df,use_container_width=True)

elif menu=='Thêm KPI':
    unit=st.text_input('Đơn vị')
    objective=st.selectbox('Objective',['O1','O2','O3','O4','O5'])
    goal=st.text_input('Goal UMP')
    kpi_code=st.text_input('Mã KPI')
    kpi_name=st.text_area('Tên KPI')
    start_year=st.number_input('Năm bắt đầu',2025,2035,2025)
    target_year=st.number_input('Năm đích',2025,2035,2026)
    progress=st.slider('% hoàn thành',0,100,0)
    if st.button('Lưu KPI'):
        conn=get_conn()
        conn.execute('INSERT INTO kpis(unit_name,objective_code,goal_code,kpi_code,kpi_name,start_year,target_year,progress,status) VALUES (?,?,?,?,?,?,?,?,?)',
                     (unit,objective,goal,kpi_code,kpi_name,start_year,target_year,progress,calc_status(progress,target_year)))
        conn.commit(); conn.close()
        st.success('Đã lưu KPI')
else:
    conn=get_conn(); df=pd.read_sql('select * from kpis',conn); conn.close()
    st.dataframe(df,use_container_width=True)
