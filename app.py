import streamlit as st
import pandas as pd
import plotly.express as px

# Cấu hình giao diện Medical Tech
st.set_page_config(page_title="SGM Supply Chain Intel", layout="wide")

st.markdown("""
    <style>
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; border-left: 5px solid #F58220; box-shadow: 2px 2px 5px #eee; }
    </style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=600)
def load_data():
    sheet_id = st.secrets["spreadsheet_id"]
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=xlsx"
    
    # Đọc dữ liệu
    df_tonghop = pd.read_excel(url, sheet_name='Tổng hợp', header=1)
    df_xuatban = pd.read_excel(url, sheet_name='Xuất bán') 
    
    # --- PHẦN QUAN TRỌNG NHẤT ---
    # Hãy đảm bảo các chữ trong ngoặc đơn bên trái khớp 100% với danh sách cột bạn chụp màn hình
    mapping = {
        'Ngành hàng': 'Nganh_Hang', 
        'Chủng loại': 'Chung_Loai', 
        'Hãng': 'Hang',
        'SKU': 'SKU', 
        'Xuất bán': 'Xuat_Ban_SL', 
        'Tồn kho': 'Ton_Kho_SL',
        'Giá trị tồn': 'Ton_Kho_Value', 
        'Hết HSD (SL)': 'Het_HSD_SL', 
        'Hết HSD (Giá)': 'Het_HSD_Value'
    }
    df_tonghop = df_tonghop.rename(columns=mapping)
    
    # Tính toán khách hàng active
    active_customers = df_xuatban.groupby('SKU')['Khách hàng'].nunique().reset_index()
    active_customers = active_customers.rename(columns={'Khách hàng': 'Khach_Hang_Active'})
    
    # Merge dữ liệu
    df = pd.merge(df_tonghop, active_customers, on='SKU', how='left').fillna(0)
    
    # Xử lý số liệu
    num_cols = ['Ton_Kho_SL', 'Ton_Kho_Value', 'Xuat_Ban_SL', 'Het_HSD_SL', 'Het_HSD_Value']
    for col in num_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    return df

df = load_data()

# --- TÍNH TOÁN CUNG ỨNG ---
st.sidebar.header("⚙️ Supply Chain Parameters")
doi_target = st.sidebar.slider("DOI - Ngày tồn kho mục tiêu", 15, 120, 45)
lead_time = st.sidebar.slider("Lead Time - Thời gian nhập (Ngày)", 10, 90, 30)

df['Daily_Sales'] = df['Xuat_Ban_SL'] / 150 
df['ROP'] = (lead_time * df['Daily_Sales']) + (doi_target * df['Daily_Sales'])
df['De_Xuat_Mua'] = (df['ROP'] - df['Ton_Kho_SL']).apply(lambda x: max(int(x), 0))
df['Trang_Thai'] = df.apply(lambda row: "🔴 ĐỨT HÀNG" if row['Ton_Kho_SL'] <= (lead_time * row['Daily_Sales']) else ("🟡 CẦN NHẬP" if row['Ton_Kho_SL'] < row['ROP'] else "🟢 AN TOÀN"), axis=1)

# --- GIAO DIỆN ---
st.title("🏥 SGM Medical Tech Dashboard")
tab1, tab2 = st.tabs(["📋 VẬN HÀNH", "📊 PHÂN TÍCH"])

with tab1:
    st.dataframe(df[['SKU', 'Hang', 'Ton_Kho_SL', 'Khach_Hang_Active', 'ROP', 'De_Xuat_Mua', 'Trang_Thai']], use_container_width=True)

with tab2:
    fig = px.scatter(df, x="Khach_Hang_Active", y="Daily_Sales", size="Ton_Kho_SL", color="Trang_Thai")
    st.plotly_chart(fig, use_container_width=True)
