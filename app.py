import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="SGM Medical Tech", layout="wide")

@st.cache_data(ttl=600)
def load_data():
    sheet_id = st.secrets["spreadsheet_id"]
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=xlsx"
    
    # --- Đọc sheet 'Tổng hợp' ---
    df_tonghop = pd.read_excel(url, sheet_name='Tổng hợp', header=1)
    df_tonghop.columns = df_tonghop.columns.str.strip()
    
    # Đổi tên các cột cần dùng (đảm bảo khớp với file)
    df_tonghop = df_tonghop.rename(columns={'Tên hàng': 'SKU', 'Tồn kho': 'Ton_Kho_SL', 'Xuất bán': 'Xuat_Ban_SL'})
    
    # --- Đọc sheet 'Xuất bán' ---
    # Đọc header 1, sau đó chúng ta sẽ ép buộc cột B (index 1) là SKU
    df_xuatban = pd.read_excel(url, sheet_name='Xuất bán', header=1)
    
    # Tự động rename cột B (index 1) thành 'SKU' và tìm cột có chữ 'Khách hàng'
    # Ép buộc cột B là SKU
    cols = df_xuatban.columns.tolist()
    cols[1] = 'SKU' 
    df_xuatban.columns = cols
    
    # Tìm cột khách hàng (chọn cột nào có chữ 'Khách hàng')
    khach_col = [c for c in df_xuatban.columns if 'Khách hàng' in str(c)][0]
    
    # Tính khách hàng active
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
    
    # Tính toán
    df['Daily_Sales'] = df['Xuat_Ban_SL'] / 150
    df['ROP'] = (lead_time * df['Daily_Sales']) + (doi_target * df['Daily_Sales'])
    df['De_Xuat_Mua'] = (df['ROP'] - df['Ton_Kho_SL']).apply(lambda x: max(int(x), 0))
    
    st.dataframe(df, use_container_width=True)
    
    fig = px.scatter(df, x="Khach_Hang_Active", y="Daily_Sales", size="Ton_Kho_SL", title="Tương quan KH vs Tốc độ bán")
    st.plotly_chart(fig)
    
except Exception as e:
    st.error(f"Lỗi hệ thống: {e}")
    st.write("Dòng này giúp bạn debug: Hãy kiểm tra lại file Excel xem header có nằm đúng ở dòng 2 không nhé.")
