import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="SGM Medical Tech", layout="wide")

@st.cache_data(ttl=600)
def load_data():
    sheet_id = st.secrets["spreadsheet_id"]
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=xlsx"
    
    # 1. Đọc sheet 'Tổng hợp'
    df_tonghop = pd.read_excel(url, sheet_name='Tổng hợp', header=1)
    df_tonghop.columns = df_tonghop.columns.str.strip()
    
    # Ép kiểu số cho cột Xuất bán và Tồn kho ngay lập tức
    # 'errors="coerce"' sẽ biến mọi thứ không phải là số thành NaN (trống)
    df_tonghop['Tên hàng'] = df_tonghop['Tên hàng'].astype(str)
    df_tonghop['Xuất bán'] = pd.to_numeric(df_tonghop['Xuất bán'], errors='coerce').fillna(0)
    df_tonghop['Tồn kho'] = pd.to_numeric(df_tonghop['Tồn kho'], errors='coerce').fillna(0)
    
    # Rename
    df_tonghop = df_tonghop.rename(columns={'Tên hàng': 'SKU', 'Tồn kho': 'Ton_Kho_SL', 'Xuất bán': 'Xuat_Ban_SL'})
    
    # 2. Đọc sheet 'Xuất bán'
    df_xuatban = pd.read_excel(url, sheet_name='Xuất bán', header=1)
    cols = df_xuatban.columns.tolist()
    # Ép buộc cột B (index 1) là SKU
    cols[1] = 'SKU'
    df_xuatban.columns = cols
    
    # Tìm cột khách hàng (tìm cột có chữ Khách hàng)
    khach_col = [c for c in df_xuatban.columns if 'Khách hàng' in str(c)][0]
    
    # Tính active customers
    active_customers = df_xuatban.groupby('SKU')[khach_col].nunique().reset_index()
    active_customers.rename(columns={khach_col: 'Khach_Hang_Active'}, inplace=True)
    
    # Merge
    df = pd.merge(df_tonghop, active_customers, on='SKU', how='left').fillna(0)
    return df

# --- GIAO DIỆN ---
try:
    df = load_data()
    st.title("🏥 SGM Medical Tech Dashboard")
    
    # Tham số
    doi_target = st.sidebar.slider("DOI (Ngày)", 15, 120, 45)
    lead_time = st.sidebar.slider("Lead Time (Ngày)", 10, 90, 30)
    
    # Tính toán (Giờ đây cột Xuất bán đã là số nên chia thoải mái)
    df['Daily_Sales'] = df['Xuat_Ban_SL'] / 150
    df['ROP'] = (lead_time * df['Daily_Sales']) + (doi_target * df['Daily_Sales'])
    df['De_Xuat_Mua'] = (df['ROP'] - df['Ton_Kho_SL']).apply(lambda x: max(int(x), 0))
    
    st.dataframe(df[['SKU', 'Ton_Kho_SL', 'Khach_Hang_Active', 'Daily_Sales', 'ROP', 'De_Xuat_Mua']], use_container_width=True)
    
except Exception as e:
    st.error(f"Lỗi: {e}")
    st.write("Nếu lỗi này vẫn còn, hãy kiểm tra xem trong cột 'Xuất bán' ở file Excel có để định dạng văn bản (text) hay không.")
