import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="SGM - QUẢN TRỊ KHO", layout="wide")

@st.cache_data(ttl=600)
def load_data():
    sheet_id = st.secrets["spreadsheet_id"]
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=xlsx"
    
    # 1. Đọc sheet 'Tổng hợp'
    df_tonghop = pd.read_excel(url, sheet_name='Tổng hợp', header=1)
    df_tonghop.columns = df_tonghop.columns.str.strip()
    # Ép kiểu dữ liệu
    df_tonghop = df_tonghop.rename(columns={'Tên hàng': 'SKU', 'Tồn kho': 'Ton_Kho_SL', 'Xuất bán': 'Xuat_Ban_SL'})
    df_tonghop['Xuat_Ban_SL'] = pd.to_numeric(df_tonghop['Xuat_Ban_SL'], errors='coerce').fillna(0)
    df_tonghop['Ton_Kho_SL'] = pd.to_numeric(df_tonghop['Ton_Kho_SL'], errors='coerce').fillna(0)
    
    # 2. Đọc sheet 'Xuất bán'
    df_xuatban = pd.read_excel(url, sheet_name='Xuất bán', header=1)
    cols = df_xuatban.columns.tolist()
    cols[1] = 'SKU' # Ép cột B là SKU
    df_xuatban.columns = cols
    
    # Tìm cột khách hàng (tìm cột có chữ Khách hàng)
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
    
    # Sidebar
    st.sidebar.header("Tham số tính toán")
    doi_target = st.sidebar.slider("DOI (Ngày tồn kho mục tiêu)", 15, 120, 45)
    lead_time = st.sidebar.slider("Lead Time (Ngày nhập hàng)", 10, 90, 30)
    
    # Tính toán
    df['Daily_Sales'] = df['Xuat_Ban_SL'] / 150
    df['ROP'] = (lead_time * df['Daily_Sales']) + (doi_target * df['Daily_Sales'])
    df['De_Xuat_Mua'] = (df['ROP'] - df['Ton_Kho_SL']).apply(lambda x: max(int(x), 0))
    
    # Layout Dashboard
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Tương quan Khách hàng & Tốc độ bán")
        fig1 = px.scatter(df, x="Khach_Hang_Active", y="Daily_Sales", size="Ton_Kho_SL", hover_name="SKU", color="Ton_Kho_SL")
        st.plotly_chart(fig1, use_container_width=True)
        
    with col2:
        st.subheader("Top sản phẩm cần nhập hàng")
        top_df = df.sort_values(by='De_Xuat_Mua', ascending=False).head(10)
        fig2 = px.bar(top_df, x="De_Xuat_Mua", y="SKU", orientation='h', color="De_Xuat_Mua")
        st.plotly_chart(fig2, use_container_width=True)
    
    # Bảng dữ liệu chi tiết
    st.subheader("Dữ liệu chi tiết")
    st.dataframe(df[['SKU', 'Ton_Kho_SL', 'Xuat_Ban_SL', 'Khach_Hang_Active', 'Daily_Sales', 'ROP', 'De_Xuat_Mua']], use_container_width=True)

except Exception as e:
    st.error(f"Lỗi hiển thị: {e}")
