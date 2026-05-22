import streamlit as st
import pandas as pd
import plotly.express as px

# Cấu hình giao diện Medical Tech
st.set_page_config(page_title="SGM Medical Tech Dashboard", layout="wide")

st.markdown("""
    <style>
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; border-left: 5px solid #F58220; box-shadow: 2px 2px 5px #eee; }
    </style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=600)
def load_data():
    sheet_id = st.secrets["spreadsheet_id"]
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=xlsx"
    
    # Đọc 2 sheet
    df_tonghop = pd.read_excel(url, sheet_name='Tổng hợp', header=1)
    df_xuatban = pd.read_excel(url, sheet_name='Xuất bán') 
    
    # FIX LỖI: Rename an toàn (chỉ đổi những cột cần thiết, không ép toàn bộ)
    mapping = {
        'Nganh hàng': 'Nganh_Hang', 'Chủng loại': 'Chung_Loai', 'Hãng': 'Hang',
        'SKU': 'SKU', 'Xuất bán': 'Xuat_Ban_SL', 'Tồn kho': 'Ton_Kho_SL',
        'Giá trị tồn': 'Ton_Kho_Value', 'Hết HSD (SL)': 'Het_HSD_SL', 'Hết HSD (Giá)': 'Het_HSD_Value'
    }
    df_tonghop = df_tonghop.rename(columns=mapping)
    
    # Xử lý dữ liệu Xuất bán (Tính số lượng khách hàng active)
    # Đảm bảo cột trong sheet Xuất bán là 'SKU' và 'Khách hàng'
    active_customers = df_xuatban.groupby('SKU')['Khách hàng'].nunique().reset_index()
    active_customers = active_customers.rename(columns={'Khách hàng': 'Khach_Hang_Active'})
    
    # Merge dữ liệu
    df = pd.merge(df_tonghop, active_customers, on='SKU', how='left').fillna(0)
    
    # Ép kiểu số cho các cột tính toán
    num_cols = ['Ton_Kho_SL', 'Ton_Kho_Value', 'Xuat_Ban_SL', 'Het_HSD_SL', 'Het_HSD_Value']
    for col in num_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    return df

df = load_data()

# --- SIDEBAR: CẤU HÌNH ---
st.sidebar.header("⚙️ Supply Chain Parameters")
doi_target = st.sidebar.slider("DOI - Ngày tồn kho mục tiêu", 15, 120, 45)
lead_time = st.sidebar.slider("Lead Time - Thời gian nhập (Ngày)", 10, 90, 30)

# --- THUẬT TOÁN TÍNH TOÁN ---
df['Daily_Sales'] = df['Xuat_Ban_SL'] / 150 # Giả định 5 tháng = 150 ngày
df['ROP'] = (lead_time * df['Daily_Sales']) + (doi_target * df['Daily_Sales'])
df['De_Xuat_Mua'] = (df['ROP'] - df['Ton_Kho_SL']).apply(lambda x: max(int(x), 0))

def classify_status(row):
    if row['Ton_Kho_SL'] <= (lead_time * row['Daily_Sales']): return "🔴 ĐỨT HÀNG"
    if row['Ton_Kho_SL'] < row['ROP']: return "🟡 CẦN NHẬP"
    return "🟢 AN TOÀN"

df['Trang_Thai'] = df.apply(classify_status, axis=1)

# --- GIAO DIỆN CHÍNH ---
tab1, tab2 = st.tabs(["📋 VẬN HÀNH & DỰ TRÙ", "📊 PHÂN TÍCH TƯƠNG QUAN"])

with tab1:
    col1, col2, col3 = st.columns(3)
    col1.metric("Tổng vốn tồn kho", f"{df['Ton_Kho_Value'].sum():,.0f} đ")
    col2.metric("Số SKU cần nhập", len(df[df['De_Xuat_Mua'] > 0]))
    col3.metric("Trạng thái chung", "Đang theo dõi")
    
    st.dataframe(df[['SKU', 'Hang', 'Ton_Kho_SL', 'Khach_Hang_Active', 'Daily_Sales', 'ROP', 'De_Xuat_Mua', 'Trang_Thai']], use_container_width=True)

with tab2:
    st.subheader("Tương quan Khách hàng - Tốc độ bán")
    fig = px.scatter(df, x="Khach_Hang_Active", y="Daily_Sales", size="Ton_Kho_SL", color="Trang_Thai",
                     hover_name="SKU", title="Scatter Plot: Khách hàng vs Sản lượng bán")
    st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("Hàng hóa rủi ro (Hết Date)")
    fig_bar = px.bar(df[df['Het_HSD_SL'] > 0], x='SKU', y='Het_HSD_Value', color='Hang', title="Giá trị thiệt hại do quá hạn")
    st.plotly_chart(fig_bar, use_container_width=True)
