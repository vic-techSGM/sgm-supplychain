import streamlit as st
import pandas as pd
import plotly.express as px

# Cấu hình giao diện Medical Tech Pro
st.set_page_config(page_title="QUẢN TRỊ KHO & CUNG ỨNG", layout="wide")

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
    
    # --- Xử lý df_tonghop ---
    df_tonghop.columns = ['STT', 'Nganh_Hang', 'Chung_Loai', 'Hang', 'SKU', 'x1', 'x2', 'x3', 'x4', 'x5', 'Xuat_Ban_SL', 'x6', 'x7', 'x8', 'Ton_Kho_SL', 'Ton_Kho_Value', 'Het_HSD_SL', 'Het_HSD_Value']
    df_tonghop = df_tonghop.iloc[1:].dropna(subset=['SKU'])
    
    # --- Xử lý df_xuatban (Phân tích mối quan hệ) ---
    # Giả định cột trong Sheet 'Xuất bán' là: [SKU, Khách hàng, Tháng]
    # Hãy đảm bảo tên cột trong file excel của bạn khớp với code dưới đây
    df_xuatban = df_xuatban.rename(columns={'SKU': 'SKU', 'Khách hàng': 'Khach_Hang'})
    
    # Tính số lượng khách hàng active cho từng SKU
    active_customers = df_xuatban.groupby('SKU')['Khach_Hang'].nunique().reset_index()
    active_customers.rename(columns={'Khach_Hang': 'Khach_Hang_Active'}, inplace=True)
    
    # Merge vào df chính
    df = pd.merge(df_tonghop, active_customers, on='SKU', how='left').fillna(0)
    
    return df

df = load_data()

# --- SIDEBAR: CẤU HÌNH THAM SỐ CUNG ỨNG ---
st.sidebar.image("https://raw.githubusercontent.com/vic-techSGM/sgm-supplychain/main/logo.png", width=150)
st.sidebar.header("⚙️ Supply Chain Parameters")

doi_target = st.sidebar.slider("DOI - Ngày tồn kho mục tiêu (Ngày)", 15, 90, 45)
lead_time = st.sidebar.slider("Lead Time - Thời gian nhập hàng (Ngày)", 10, 90, 30)

# --- TÍNH TOÁN CỐT LÕI ---
SO_THANG_LICH_SU = 5
df['Daily_Sales'] = df['Xuat_Ban_SL'] / (SO_THANG_LICH_SU * 30)

# Reorder Point (ROP) = (Lead Time * Nhu cầu ngày) + Safety Stock (DOI * Nhu cầu ngày)
df['ROP'] = (lead_time * df['Daily_Sales']) + (doi_target * df['Daily_Sales'])
df['Safety_Stock_Level'] = doi_target * df['Daily_Sales']
df['De_Xuat_Mua'] = (df['ROP'] - df['Ton_Kho_SL']).apply(lambda x: max(int(x), 0))

# Phân loại trạng thái
def classify_status(row):
    if row['Ton_Kho_SL'] <= (lead_time * row['Daily_Sales']): return "🔴 CỰC KỲ NGUY HIỂM (Đứt hàng)"
    if row['Ton_Kho_SL'] < row['ROP']: return "🟡 CẦN NHẬP (Dưới ROP)"
    return "🟢 AN TOÀN"

df['Trang_Thai'] = df.apply(classify_status, axis=1)

# --- GIAO DIỆN ---
tab1, tab2 = st.tabs(["📋 Bảng điều khiển vận hành", "📊 Phân tích tương quan"])

with tab1:
    st.subheader("Trạng thái tồn kho theo Lead Time")
    
    # Hiển thị bảng
    display_df = df[['SKU', 'Hang', 'Ton_Kho_SL', 'Khach_Hang_Active', 'Daily_Sales', 'ROP', 'De_Xuat_Mua', 'Trang_Thai']]
    display_df.columns = ['Mã SKU', 'Hãng', 'Tồn Kho', 'KH Active', 'Bán TB/Ngày', 'Điểm Đặt Hàng (ROP)', 'Mua Thêm', 'Trạng Thái']
    
    st.dataframe(display_df.sort_values('De_Xuat_Mua', ascending=False), use_container_width=True)
    
    if st.button("📥 Xuất báo cáo đặt hàng"):
        st.download_button("Tải file", data=display_df.to_csv(index=False), file_name="Dat_Hang.csv")

with tab2:
    st.subheader("Tương quan Khách hàng - SKU")
    fig = px.scatter(df, x="Khach_Hang_Active", y="Daily_Sales", size="Ton_Kho_SL", color="Trang_Thai",
                     hover_name="SKU", title="Mức độ rủi ro dựa trên khách hàng active")
    st.plotly_chart(fig, use_container_width=True)
