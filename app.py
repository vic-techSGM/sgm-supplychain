import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="SGM Medical Tech", layout="wide")

@st.cache_data(ttl=600)
def load_data():
    sheet_id = st.secrets["spreadsheet_id"]
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=xlsx"
    
    # 1. Đọc sheet "Tổng hợp" với header=1 (dòng 2 là tiêu đề)
    df_tonghop = pd.read_excel(url, sheet_name='Tổng hợp', header=1)
    
    # Map tên cột dựa trên danh sách debug bạn gửi
    mapping_tonghop = {
        'Ngành hàng': 'Nganh_Hang', 
        'Chủng loại': 'Chung_Loai', 
        'Hãng': 'Hang',
        'Tên hàng': 'SKU', 
        'Tồn kho': 'Ton_Kho_SL',
        'Xuất bán': 'Xuat_Ban_SL'
    }
    df_tonghop = df_tonghop.rename(columns=mapping_tonghop)
    
    # 2. Đọc sheet "Xuất bán" với header=2 (dòng 3 là tiêu đề)
    df_xuatban = pd.read_excel(url, sheet_name='Xuất bán', header=2)
    
    # Tính số khách hàng unique theo SKU
    # Dựa vào screenshot, cột chứa SKU là 'SKU', cột chứa khách hàng là 'Khách hàng'
    active_customers = df_xuatban.groupby('SKU')['Khách hàng'].nunique().reset_index()
    active_customers = active_customers.rename(columns={'Khách hàng': 'Khach_Hang_Active'})
    
    # Merge dữ liệu
    df = pd.merge(df_tonghop, active_customers, on='SKU', how='left').fillna(0)
    
    # Clean data (ép kiểu số)
    num_cols = ['Ton_Kho_SL', 'Xuat_Ban_SL']
    for col in num_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            
    return df

# --- GIAO DIỆN ---
df = load_data()
st.title("🏥 SGM Medical Tech Dashboard")

# Cấu hình tham số
doi_target = st.sidebar.slider("DOI - Ngày tồn kho mục tiêu", 15, 120, 45)
lead_time = st.sidebar.slider("Lead Time - Thời gian nhập (Ngày)", 10, 90, 30)

# Thuật toán
df['Daily_Sales'] = df['Xuat_Ban_SL'] / 150 
df['ROP'] = (lead_time * df['Daily_Sales']) + (doi_target * df['Daily_Sales'])
df['De_Xuat_Mua'] = (df['ROP'] - df['Ton_Kho_SL']).apply(lambda x: max(int(x), 0))

st.dataframe(df[['SKU', 'Hang', 'Ton_Kho_SL', 'Khach_Hang_Active', 'Daily_Sales', 'ROP', 'De_Xuat_Mua']], use_container_width=True)

fig = px.scatter(df, x="Khach_Hang_Active", y="Daily_Sales", size="Ton_Kho_SL", title="Tương quan Khách hàng - Tốc độ bán")
st.plotly_chart(fig)
