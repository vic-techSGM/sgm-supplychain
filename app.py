import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="SGM Medical Tech", layout="wide")

@st.cache_data(ttl=600)
def load_data():
    sheet_id = st.secrets["spreadsheet_id"]
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=xlsx"
    
    # 1. Đọc sheet 'Tổng hợp' - Bỏ qua 2 dòng đầu, lấy dòng 3 làm tiêu đề
    df_tonghop = pd.read_excel(url, sheet_name='Tổng hợp', header=2)
    # Loại bỏ các cột 'Unnamed' và làm sạch khoảng trắng
    df_tonghop = df_tonghop.loc[:, ~df_tonghop.columns.str.contains('^Unnamed')]
    df_tonghop.columns = df_tonghop.columns.str.strip()
    
    # Đổi tên các cột cần dùng (theo danh sách debug bạn đã gửi)
    mapping = {
        'Tên hàng': 'SKU', 
        'Tồn kho': 'Ton_Kho_SL', 
        'Xuất bán': 'Xuat_Ban_SL'
    }
    df_tonghop = df_tonghop.rename(columns=mapping)
    
    # 2. Đọc sheet 'Xuất bán' - Lấy dòng 2 và 3 làm tiêu đề (MultiIndex)
    df_xuatban = pd.read_excel(url, sheet_name='Xuất bán', header=[1, 2])
    # Flatten MultiIndex: Nối các tên cột lại (ví dụ 'BÁN RA' + 'Số lượng' -> 'BAN_RA_SoLuong')
    df_xuatban.columns = ['_'.join(col).strip() for col in df_xuatban.columns.values]
    
    # Làm sạch tên cột
    df_xuatban.columns = df_xuatban.columns.str.replace(r'Unnamed: \d+_level_\d+', '', regex=True).str.strip()
    
    # Tìm cột SKU và Khách hàng dựa trên danh sách cột mới
    # Dựa vào screenshot, SKU nằm ở cột 2, Khách hàng ở cột F (index 5)
    cols = df_xuatban.columns.tolist()
    sku_col = [c for c in cols if 'SKU' in c][0]
    khach_col = [c for c in cols if 'Khách hàng' in c][0]
    
    # Tính khách hàng active
    active_customers = df_xuatban.groupby(sku_col)[khach_col].nunique().reset_index()
    active_customers.rename(columns={sku_col: 'SKU', khach_col: 'Khach_Hang_Active'}, inplace=True)
    
    # 3. Merge
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
    st.error(f"Lỗi: {e}")
    st.write("Vui lòng đảm bảo Sheet 'Xuất bán' có cột SKU và Khách hàng chính xác.")
