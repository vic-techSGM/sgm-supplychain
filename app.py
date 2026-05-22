import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="SGM Medical Tech", layout="wide")

@st.cache_data(ttl=600)
def load_data():
    sheet_id = st.secrets["spreadsheet_id"]
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=xlsx"
    
    # 1. Đọc sheet Tổng hợp: Bỏ qua 3 dòng đầu (index 0,1,2 - vì đã bị trộn ô)
    # Sau đó tự đặt lại tên cột
    df_tonghop = pd.read_excel(url, sheet_name='Tổng hợp', header=None, skiprows=3)
    # Đặt tên cột theo đúng thứ tự (Bạn hãy kiểm tra lại file của bạn, nếu cột ở vị trí khác hãy sửa ở đây)
    df_tonghop.columns = ['STT', 'Nganh_Hang', 'Chung_Loai', 'Hang', 'SKU', 'x1', 'x2', 'x3', 'x4', 'x5', 'Xuat_Ban_SL', 'x6', 'x7', 'x8', 'Ton_Kho_SL', 'Ton_Kho_Value', 'Het_HSD_SL', 'Het_HSD_Value']
    
    # 2. Đọc sheet Xuất bán: Bỏ qua 3 dòng đầu (ô trộn)
    df_xuatban = pd.read_excel(url, sheet_name='Xuất bán', header=None, skiprows=3)
    # Theo ảnh, dòng 4 (index 3) có tiêu đề, ta đặt thủ công
    # Giả định cột 0 là SKU, cột 1 là Khách hàng (Sửa lại chỉ số cột nếu sai)
    df_xuatban.columns = ['x', 'SKU', 'x', 'x', 'x', 'Khách hàng', 'x', 'x', 'x'] 
    # Lưu ý: Bạn cần sửa lại danh sách cột trên khớp với số lượng cột thực tế của file Xuất bán
    
    # Tính khách hàng active
    active_customers = df_xuatban.groupby('SKU')['Khách hàng'].nunique().reset_index()
    active_customers = active_customers.rename(columns={'Khách hàng': 'Khach_Hang_Active'})
    
    df = pd.merge(df_tonghop, active_customers, on='SKU', how='left').fillna(0)
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
df['Trang_Thai'] = df.apply(lambda row: "🔴 ĐỨT HÀNG" if row['Ton_Kho_SL'] <= (lead_time * row['Daily_Sales']) else ("🟡 CẦN NHẬP" if row['Ton_Kho_SL'] < row['ROP'] else "🟢 AN TOÀN"), axis=1)

st.dataframe(df[['SKU', 'Hang', 'Ton_Kho_SL', 'Khach_Hang_Active', 'ROP', 'De_Xuat_Mua', 'Trang_Thai']], use_container_width=True)
