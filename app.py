import streamlit as st
import pandas as pd
import plotly.express as px

# --- 1. CẤU HÌNH GIAO DIỆN MEDICAL TECH ---
st.set_page_config(page_title="SGM Medical Tech - Supply Chain", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    .main { background-color: #f4f7f9; }
    div[data-testid="stMetric"] {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        border-left: 6px solid #F58220; 
    }
    button[data-baseweb="tab"] { font-size: 18px; font-weight: bold; color: #555; }
    button[aria-selected="true"] { color: #F58220 !important; border-bottom-color: #F58220 !important; }
    [data-testid="stSidebar"] { background-color: #ffffff; border-right: 1px solid #e0e0e0; }
    </style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=600)
def load_data():
    sheet_id = st.secrets["spreadsheet_id"]
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=xlsx"
    
    # --- XỬ LÝ SHEET TỔNG HỢP (BULLETPROOF BẰNG INDEX) ---
    df_th_raw = pd.read_excel(url, sheet_name='Tổng hợp', header=1)
    
    # Lấy chính xác các cột theo số thứ tự bạn đã cung cấp, bỏ qua tên gọi
    # 1: Ngành hàng | 3: Hãng | 4: SKU | 10: Xuất bán | 14: Tồn kho | 15: Giá trị tồn
    df_th = df_th_raw.iloc[:, [1, 3, 4, 10, 14, 15]].copy()
    df_th.columns = ['Nganh_Hang', 'Hang', 'SKU', 'Xuat_Ban_SL', 'Ton_Kho_SL', 'Ton_Kho_Value']
    
    # Làm sạch: Bỏ dòng trống và ép kiểu số
    df_th = df_th.dropna(subset=['SKU'])
    df_th['SKU'] = df_th['SKU'].astype(str).str.strip()
    
    for col in ['Xuat_Ban_SL', 'Ton_Kho_SL', 'Ton_Kho_Value']:
        df_th[col] = pd.to_numeric(df_th[col], errors='coerce').fillna(0)

    # --- XỬ LÝ SHEET XUẤT BÁN ---
    df_xb_raw = pd.read_excel(url, sheet_name='Xuất bán', header=1)
    
    # Cột B (Index 1) luôn là SKU. Cột F (Index 5) thường là Khách hàng.
    # Để an toàn nhất, nhặt đúng cột số 1 làm SKU.
    cols = df_xb_raw.columns.tolist()
    cols[1] = 'SKU'
    df_xb_raw.columns = cols
    
    # Tìm cột Khách hàng bằng chữ, nếu không thấy thì mặc định lấy cột số 5 (Cột F)
    kh_cols = [c for c in df_xb_raw.columns if 'Khách hàng' in str(c)]
    kh_col_name = kh_cols[0] if kh_cols else df_xb_raw.columns[5]
    
    df_xb_raw['SKU'] = df_xb_raw['SKU'].astype(str).str.strip()
    
    # Đếm số khách hàng active
    active_kh = df_xb_raw.groupby('SKU')[kh_col_name].nunique().reset_index()
    active_kh.rename(columns={kh_col_name: 'Khach_Hang_Active'}, inplace=True)
    
    # --- MERGE DỮ LIỆU ---
    df = pd.merge(df_th, active_kh, on='SKU', how='left').fillna(0)
    return df

# --- 2. THỰC THI & GIAO DIỆN ---
try:
    df = load_data()
    
    # Sidebar
    st.sidebar.image("https://raw.githubusercontent.com/vic-techSGM/sgm-supplychain/main/logo.png", width=180)
    st.sidebar.markdown("---")
    st.sidebar.header("⚙️ Tham số Chuỗi cung ứng")
    
    doi_target = st.sidebar.slider("DOI - Tồn kho mục tiêu (Ngày)", 15, 120, 45)
    lead_time = st.sidebar.slider("Lead Time - Thời gian nhập (Ngày)", 10, 90, 30)

    # Thuật toán
    df['Daily_Sales'] = df['Xuat_Ban_SL'] / 150 # Trung bình 5 tháng
    df['ROP'] = (lead_time * df['Daily_Sales']) + (doi_target * df['Daily_Sales'])
    df['De_Xuat_Mua'] = (df['ROP'] - df['Ton_Kho_SL']).apply(lambda x: max(int(x), 0))

    def check_status(row):
        if row['Ton_Kho_SL'] < (lead_time * row['Daily_Sales']): return "🔴 ĐỨT HÀNG (Dưới Lead Time)"
        if row['Ton_Kho_SL'] < row['ROP']: return "🟡 CẦN NHẬP (Dưới DOI)"
        return "🟢 AN TOÀN"
    
    df['Trang_Thai'] = df.apply(check_status, axis=1)

    # Main Dashboard
    st.title("🏥 SGM Medical Tech - Hệ thống Quản trị Cung ứng")
    
    tab1, tab2 = st.tabs(["📋 BẢNG ĐIỀU KHIỂN & DỰ TRÙ", "📊 PHÂN TÍCH TƯƠNG QUAN"])

    with tab1:
        # Metrics
        m1, m2, m3 = st.columns(3)
        m1.metric("Tổng Vốn Đang Tồn", f"{df['Ton_Kho_Value'].sum():,.0f} đ")
        m2.metric("Số Mã SKU Cần Nhập", len(df[df['De_Xuat_Mua'] > 0]))
        m3.metric("Tổng KH Active", int(df['Khach_Hang_Active'].sum()))

        st.subheader("Danh sách Dự trù Mua hàng tự động")
        display_cols = ['SKU', 'Hang', 'Ton_Kho_SL', 'Khach_Hang_Active', 'Daily_Sales', 'ROP', 'De_Xuat_Mua', 'Trang_Thai']
        st.dataframe(df[display_cols].sort_values('De_Xuat_Mua', ascending=False), use_container_width=True)

    with tab2:
        st.subheader("Tương quan Khách hàng & Tốc độ tiêu thụ")
        
        fig = px.scatter(
            df, x="Khach_Hang_Active", y="Daily_Sales", size="Ton_Kho_SL", color="Trang_Thai",
            hover_name="SKU", 
            labels={"Khach_Hang_Active": "Số KH Active", "Daily_Sales": "Sản lượng bán/ngày", "Ton_Kho_SL": "Tồn kho"},
            color_discrete_map={"🔴 ĐỨT HÀNG (Dưới Lead Time)": "#d32f2f", "🟡 CẦN NHẬP (Dưới DOI)": "#fbc02d", "🟢 AN TOÀN": "#388e3c"}
        )
        st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error(f"Lỗi không xác định: {e}")
    st.info("Vui lòng chụp thông báo lỗi này cho tôi, đây là bước cuối cùng.")
