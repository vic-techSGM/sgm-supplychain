import streamlit as st
import pandas as pd
import plotly.express as px

# ==========================================
# 1. CẤU HÌNH GIAO DIỆN SGM MEDICAL TECH
# ==========================================
st.set_page_config(page_title="SGM Supply Chain Intel", page_icon="🏥", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    /* Nền tổng thể */
    .main { background-color: #f4f7f9; }
    
    /* Thiết kế Thẻ KPI (Glassmorphism + Border Cam SGM) */
    div[data-testid="stMetric"] {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        border-left: 6px solid #F58220; 
        transition: transform 0.2s ease-in-out;
    }
    div[data-testid="stMetric"]:hover {
        transform: translateY(-5px);
    }
    
    /* Font và Tabs */
    button[data-baseweb="tab"] { font-size: 16px; font-weight: 600; color: #555; }
    button[aria-selected="true"] { color: #F58220 !important; border-bottom-color: #F58220 !important; }
    
    /* Nút Download Xanh lá Medical */
    .stDownloadButton button {
        background-color: #388e3c !important; 
        color: white !important;
        border-radius: 8px !important;
        font-weight: bold;
        border: none !important;
        width: 100%;
    }
    .stDownloadButton button:hover { background-color: #2e7d32 !important; }
    
    /* Sidebar */
    [data-testid="stSidebar"] { background-color: #ffffff; border-right: 1px solid #e0e0e0; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. HỆ THỐNG XỬ LÝ DỮ LIỆU (BULLETPROOF)
# ==========================================
@st.cache_data(ttl=600)
def load_data():
    sheet_id = st.secrets["spreadsheet_id"]
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=xlsx"
    
    # --- A. XỬ LÝ SHEET TỔNG HỢP ---
    df_th_raw = pd.read_excel(url, sheet_name='Tổng hợp', header=1)
    
    # Nhặt chính xác cột theo số thứ tự (Index) để tránh lỗi đổi tên/gộp ô
    # 1: Ngành hàng | 3: Hãng | 4: SKU | 10: Xuất bán | 14: Tồn kho | 15: Giá trị tồn
    df_th = df_th_raw.iloc[:, [1, 3, 4, 10, 14, 15]].copy()
    df_th.columns = ['Nganh_Hang', 'Hang', 'SKU', 'Xuat_Ban_SL', 'Ton_Kho_SL', 'Ton_Kho_Value']
    
    # Làm sạch dữ liệu
    df_th = df_th.dropna(subset=['SKU'])
    df_th['SKU'] = df_th['SKU'].astype(str).str.strip()
    df_th['Nganh_Hang'] = df_th['Nganh_Hang'].fillna('Khác').astype(str)
    df_th['Hang'] = df_th['Hang'].fillna('Khác').astype(str)
    
    for col in ['Xuat_Ban_SL', 'Ton_Kho_SL', 'Ton_Kho_Value']:
        df_th[col] = pd.to_numeric(df_th[col], errors='coerce').fillna(0)

    # --- B. XỬ LÝ SHEET XUẤT BÁN ---
    df_xb_raw = pd.read_excel(url, sheet_name='Xuất bán', header=1)
    
    # Ép buộc cột số 2 (Index 1) luôn là SKU
    cols = df_xb_raw.columns.tolist()
    cols[1] = 'SKU'
    df_xb_raw.columns = cols
    
    # Tìm cột Khách hàng
    kh_cols = [c for c in df_xb_raw.columns if 'Khách hàng' in str(c)]
    kh_col_name = kh_cols[0] if kh_cols else df_xb_raw.columns[5]
    
    df_xb_raw['SKU'] = df_xb_raw['SKU'].astype(str).str.strip()
    
    # Tính Khách hàng Active
    active_kh = df_xb_raw.groupby('SKU')[kh_col_name].nunique().reset_index()
    active_kh.rename(columns={kh_col_name: 'Khach_Hang_Active'}, inplace=True)
    
    # --- C. MERGE & HOÀN THIỆN ---
    df = pd.merge(df_th, active_kh, on='SKU', how='left').fillna(0)
    return df

# ==========================================
# 3. ĐIỀU HƯỚNG & GIAO DIỆN CHÍNH
# ==========================================
try:
    df_full = load_data()
    
    # --- SIDEBAR CONTROLS ---
    st.sidebar.image("https://raw.githubusercontent.com/vic-techSGM/sgm-supplychain/main/logo.png", use_container_width=True)
    st.sidebar.markdown("---")
    
    st.sidebar.header("🎯 Chiến thuật Cung ứng")
    doi_target = st.sidebar.slider("DOI (Tồn kho mục tiêu - Ngày)", 15, 120, 45, help="Số ngày hàng hoá đủ bán")
    lead_time = st.sidebar.slider("Lead Time (Thời gian nhập - Ngày)", 10, 90, 30, help="Thời gian từ lúc đặt đến lúc hàng về")
    
    st.sidebar.header("📂 Bộ lọc Dữ liệu")
    list_nganh = df_full['Nganh_Hang'].unique().tolist()
    list_hang = df_full['Hang'].unique().tolist()
    
    # Lọc đa tầng
    selected_nganh = st.sidebar.multiselect("Lọc theo Ngành hàng", list_nganh, default=list_nganh)
    
    # Cập nhật danh sách Hãng theo Ngành hàng đã chọn
    df_filtered_nganh = df_full[df_full['Nganh_Hang'].isin(selected_nganh)]
    valid_hangs = df_filtered_nganh['Hang'].unique().tolist()
    selected_hang = st.sidebar.multiselect("Lọc theo Hãng cung cấp", valid_hangs, default=valid_hangs)

    # --- ÁP DỤNG BỘ LỌC VÀ TÍNH TOÁN ROP ---
    df = df_filtered_nganh[df_filtered_nganh['Hang'].isin(selected_hang)].copy()
    
    df['Daily_Sales'] = df['Xuat_Ban_SL'] / 150 # Trung bình 5 tháng (150 ngày)
    df['ROP'] = (lead_time * df['Daily_Sales']) + (doi_target * df['Daily_Sales'])
    df['De_Xuat_Mua'] = (df['ROP'] - df['Ton_Kho_SL']).apply(lambda x: max(int(x), 0))

    def get_status(row):
        if row['Ton_Kho_SL'] < (lead_time * row['Daily_Sales']): return "🔴 ĐỨT HÀNG (Rủi ro cao)"
        if row['Ton_Kho_SL'] < row['ROP']: return "🟡 CẦN NHẬP (Dưới DOI)"
        return "🟢 AN TOÀN"
    
    df['Trang_Thai'] = df.apply(get_status, axis=1)

    # --- MAIN DASHBOARD HEADER ---
    st.title("🏥 Hệ thống Quản trị Cung ứng SGM")
    st.markdown("Nền tảng kiểm soát tồn kho thông minh tích hợp Active Customers & Thuật toán ROP.")
    
    # --- TABS ---
    tab1, tab2, tab3 = st.tabs(["📋 TỔNG QUAN & DỰ TRÙ", "👥 TƯƠNG QUAN KHÁCH HÀNG", "📊 CƠ CẤU TÀI SẢN"])

    with tab1:
        # KPI Tầng 1
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Tổng Vốn Tồn Kho (Lọc)", f"{df['Ton_Kho_Value'].sum():,.0f} ₫")
        m2.metric("Số SKU Cần Nhập", len(df[df['De_Xuat_Mua'] > 0]))
        m3.metric("Tổng KH Active", int(df['Khach_Hang_Active'].sum()))
        m4.metric("SKU Đang Cảnh Báo Đỏ", len(df[df['Trang_Thai'] == "🔴 ĐỨT HÀNG (Rủi ro cao)"]))

        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader("🛒 Bảng Kế hoạch Đặt hàng tự động")
        
        display_cols = ['SKU', 'Hang', 'Ton_Kho_SL', 'Khach_Hang_Active', 'Daily_Sales', 'ROP', 'De_Xuat_Mua', 'Trang_Thai']
        st.dataframe(df[display_cols].sort_values(by=['Trang_Thai', 'De_Xuat_Mua'], ascending=[True, False]), use_container_width=True, height=400)
        
        csv = df[display_cols].to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 XUẤT FILE ĐẶT HÀNG KẾ HOẠCH (CSV)", data=csv, file_name='SGM_Purchase_Plan.csv')

    with tab2:
        st.subheader("Phân tích Mức độ Ưu tiên dựa trên Tệp Khách Hàng (S2S)")
        fig_scatter = px.scatter(
            df, x="Khach_Hang_Active", y="Daily_Sales", size="Ton_Kho_SL", color="Trang_Thai",
            hover_name="SKU", 
            labels={"Khach_Hang_Active": "Số Lượng Khách Hàng Active", "Daily_Sales": "Tốc Độ Bán / Ngày", "Ton_Kho_SL": "Hiện Tồn"},
            color_discrete_map={"🔴 ĐỨT HÀNG (Rủi ro cao)": "#d32f2f", "🟡 CẦN NHẬP (Dưới DOI)": "#fbc02d", "🟢 AN TOÀN": "#388e3c"}
        )
        fig_scatter.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_scatter, use_container_width=True)

    with tab3:
        st.subheader("Cơ cấu Vốn Tồn Kho")
        col_pie1, col_pie2 = st.columns(2)
        
        with col_pie1:
            fig_pie1 = px.pie(df, values='Ton_Kho_Value', names='Nganh_Hang', title="Tỷ trọng Vốn theo Ngành Hàng", hole=0.4, color_discrete_sequence=px.colors.qualitative.Set2)
            st.plotly_chart(fig_pie1, use_container_width=True)
            
        with col_pie2:
            fig_pie2 = px.pie(df, values='Ton_Kho_Value', names='Hang', title="Tỷ trọng Vốn theo Hãng", hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
            st.plotly_chart(fig_pie2, use_container_width=True)

except Exception as e:
    st.error(f"Lỗi khởi tạo hệ thống: {e}")
