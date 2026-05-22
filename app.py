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
    
    # Debug: Cho phép xem các cột đang có
    st.write("--- DANH SÁCH CỘT THỰC TẾ TRONG FILE ---")
    st.write(df_tonghop.columns.tolist())
    st.write("-------------------------------------------")

    # Hàm lấy cột an toàn (nếu không có thì trả về cột 0)
    def get_col(df, possible_names, default_name):
        for name in possible_names:
            if name in df.columns:
                return df[name]
        return pd.Series(0, index=df.index)

    # Xây dựng DataFrame sạch
    df = pd.DataFrame()
    df['SKU'] = get_col(df_tonghop, ['Tên hàng', 'SKU', 'Mã hàng'], 'SKU')
    df['Hang'] = get_col(df_tonghop, ['Hãng', 'Nhà cung cấp'], 'Hãng')
    df['Xuat_Ban_SL'] = pd.to_numeric(get_col(df_tonghop, ['Xuất bán', 'Sản lượng bán'], 'Xuat_Ban_SL'), errors='coerce').fillna(0)
    df['Ton_Kho_SL'] = pd.to_numeric(get_col(df_tonghop, ['Tồn kho', 'Số lượng tồn'], 'Ton_Kho_SL'), errors='coerce').fillna(0)
    df['Ton_Kho_Value'] = pd.to_numeric(get_col(df_tonghop, ['Giá trị tồn', 'Giá trị tồn kho', 'Tiền tồn'], 'Ton_Kho_Value'), errors='coerce').fillna(0)
    df['Het_HSD_Value'] = pd.to_numeric(get_col(df_tonghop, ['Hết HSD (Giá)', 'Giá trị quá hạn'], 'Het_HSD_Value'), errors='coerce').fillna(0)

    # 2. Đọc sheet 'Xuất bán'
    df_xuatban = pd.read_excel(url, sheet_name='Xuất bán', header=1)
    df_xuatban.columns = df_xuatban.columns.str.strip()
    
    # Tìm cột SKU và Khách hàng trong sheet xuất bán
    sku_col = [c for c in df_xuatban.columns if 'SKU' in str(c)][0]
    khach_col = [c for c in df_xuatban.columns if 'Khách hàng' in str(c)][0]
    
    active_customers = df_xuatban.groupby(sku_col)[khach_col].nunique().reset_index()
    active_customers.columns = ['SKU', 'Khach_Hang_Active']
    
    df = pd.merge(df, active_customers, on='SKU', how='left').fillna(0)
    return df

# --- GIAO DIỆN ---
try:
    df = load_data()
    st.title("🏥 SGM Medical Tech Dashboard")
    
    # Tính toán
    df['Daily_Sales'] = df['Xuat_Ban_SL'] / 150
    st.dataframe(df, use_container_width=True)
    
except Exception as e:
    st.error(f"Lỗi: {e}")
