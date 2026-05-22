import streamlit as st
import pandas as pd
import plotly.express as px

# --- 1. CẤU HÌNH GIAO DIỆN MEDICAL TECH (CONCEPT SGM) ---
st.set_page_config(page_title="SGM Medical Tech - Supply Chain", layout="wide")

st.markdown("""
    <style>
    /* Tổng thể */
    .main { background-color: #f4f7f9; }
    
    /* Thiết kế Metric Cards */
    div[data-testid="stMetric"] {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        border-left: 6px solid #F58220; /* Cam SGM */
    }
    
    /* Làm đẹp Tab và Button */
    button[data-baseweb="tab"] { font-size: 18px; font-weight: bold; color: #555; }
    button[aria-selected="true"] { color: #F58220 !important; border-bottom-color: #F58220 !important; }
    
    .stDownloadButton button {
        background-color: #4CAF50 !important; /* Xanh lá SGM */
        color: white !important;
        border-radius: 20px !important;
        border: none !important;
        padding: 0.5rem 2rem !important;
    }
    
    /* Sidebar chuyên nghiệp */
    [data-testid="stSidebar"] { background-color: #ffffff; border-right: 1px solid #e0e0e0; }
    </style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=600)
def load_data():
    sheet_id = st.secrets["spreadsheet_id"]
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=xlsx"
    
    # 1. Đọc sheet "Tổng hợp" (Lấy header dòng 2, skip dòng trộn)
    df_tonghop = pd.read_excel(url, sheet_name='Tổng hợp', header=1)
    df_tonghop.columns = df_tonghop.columns.str.strip()
    
    # Mapping cột khớp với thực tế file của bạn
    map_th = {
        'Ngành hàng': 'Nganh_Hang', 'Chủng loại': 'Chung_Loai', 'Hãng': 'Hang',
        'Tên hàng': 'SKU', 'Xuất bán': 'Xuat_Ban_SL', 'Tồn kho': 'Ton_Kho_SL',
        'Giá trị tồn': 'Ton_Kho_Value', 'Hết HSD (Giá)': 'Het_HSD_Value'
    }
    df_tonghop = df_tonghop.rename(columns=map_th)
    
    # Ép kiểu số
    for col in ['Xuat_Ban_SL', 'Ton_Kho_SL', 'Ton_Kho_Value', 'Het_HSD_Value']:
        if col in df_tonghop.columns:
            df_tonghop[col] = pd.to_numeric(df_tonghop[col], errors='coerce').fillna(0)

    # 2. Đọc sheet "Xuất bán" (Xử lý ô trộn dòng 2-3)
    df_xb_raw = pd.read_excel(url, sheet_name='Xuất bán', header=1)
    
    # Ép cột B là SKU (vị trí index 1)
    xb_cols = df_xb_raw.columns.tolist()
    xb_cols[1] = 'SKU'
    df_xb_raw.columns = xb_cols
    df_xb_raw.columns = df_xb_raw.columns.str.strip()
    
    # Tìm cột Khách hàng (cột F - index 5 theo screenshot)
    kh_col_name = [c for c in df_xb_raw.columns if 'Khách hàng' in str(c)][0]
    
    # Tính Khách hàng Active
    active_kh = df_xb_raw.groupby('SKU')[kh_col_name].nunique().reset_index()
    active_kh.rename(columns={kh_col_name: 'Khach_Hang_Active'}, inplace=True)
    
    # Merge 2 sheet
    df = pd.merge(df_tonghop, active_kh, on='SKU', how='left').fillna(0)
    return df

# --- 2. LOGIC VẬN HÀNH (S2S & LEAD TIME) ---
try:
    df = load_data()
    
    # Sidebar: Logo & Controls
    st.sidebar.image("https://raw.githubusercontent.com/vic-techSGM/sgm-supplychain/main/logo.png", width=180)
    st.sidebar.markdown("---")
    st.sidebar.header("⚙️ Supply Chain Parameters")
    
    doi_target = st.sidebar.slider("DOI - Tồn kho mục tiêu (Ngày)", 15, 120, 45)
    lead_time = st.sidebar.slider("Lead Time - Thời gian nhập (Ngày)", 10, 90, 30)

    # Tính toán Supply Chain Logic
    df['Daily_Sales'] = df['Xuat_Ban_SL'] / 150 # Trung bình 5 tháng
    df['ROP'] = (lead_time * df['Daily_Sales']) + (doi_target * df['Daily_Sales'])
    df['De_Xuat_Mua'] = (df['ROP'] - df['Ton_Kho_SL']).apply(lambda x: max(int(x), 0))

    def check_status(row):
        if row['Ton_Kho_SL'] < (lead_time * row['Daily_Sales']): return "🔴 ĐỨT HÀNG (Dưới Lead Time)"
        if row['Ton_Kho_SL'] < row['ROP']: return "🟡 CẦN NHẬP (Dưới DOI)"
        return "🟢 AN TOÀN"
    
    df['Trang_Thai'] = df.apply(check_status, axis=1)

    # --- 3. INTERFACE: TABS & BUTTONS ---
    tab1, tab2, tab3 = st.tabs(["🏥 QUẢN TRỊ TỔN KHO", "👥 TƯƠNG QUAN KHÁCH HÀNG", "⚠️ RỦI RO & HẠN DÙNG"])

    with tab1:
        # KPI Metrics
        m1, m2, m3 = st.columns(3)
        m1.metric("Tổng Vốn Tồn Kho", f"{df['Ton_Kho_Value'].sum():,.0f} đ")
        m2.metric("Số SKU Cần Đặt Hàng", len(df[df['De_Xuat_Mua'] > 0]))
        m3.metric("Số KH Active Toàn Hệ Thống", int(df['Khach_Hang_Active'].sum()))

        st.subheader("📋 Danh sách dự trù & Trạng thái tồn kho")
        # Phân lọc Hãng/Ngành hàng (Nếu cần)
        
        display_cols = ['SKU', 'Hang', 'Ton_Kho_SL', 'Khach_Hang_Active', 'Daily_Sales', 'ROP', 'De_Xuat_Mua', 'Trang_Thai']
        st.dataframe(df[display_cols].sort_values('De_Xuat_Mua', ascending=False), use_container_width=True)
        
        csv = df[display_cols].to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 TẢI DANH SÁCH ĐẶT HÀNG", data=csv, file_name='SGM_Order_Plan.csv')

    with tab2:
        st.subheader("📊 Phân tích S2S (Sales to Stock) & Customer Active")
        col_left, col_right = st.columns([2, 1])
        
        with col_left:
            fig = px.scatter(
                df, x="Khach_Hang_Active", y="Daily_Sales", size="Ton_Kho_SL", color="Trang_Thai",
                hover_name="SKU", title="Tương quan giữa Khách hàng và Sức bán"
            )
            st.plotly_chart(fig, use_container_width=True)
            
        with col_right:
            st.info("""
            **Cách đọc biểu đồ:**
            - **Trục X:** Càng về bên phải, SKU càng có nhiều khách hàng tin dùng.
            - **Trục Y:** Càng lên cao, SKU bán càng nhanh mỗi ngày.
            - **Màu sắc:** Cảnh báo đỏ/vàng giúp bạn ưu tiên nhập hàng cho SKU đông khách trước.
            """)

    with tab3:
        st.subheader("🚩 Cảnh báo thiệt hại hàng cận hạn/hết hạn")
        total_risk = df['Het_HSD_Value'].sum()
        st.error(f"Tổng giá trị hàng rủi ro: {total_risk:,.0f} VNĐ")
        
        fig_risk = px.bar(
            df[df['Het_HSD_Value'] > 0], x="SKU", y="Het_HSD_Value", color="Hang",
            title="Giá trị hàng rủi ro theo từng SKU"
        )
        st.plotly_chart(fig_risk, use_container_width=True)

except Exception as e:
    st.error(f"Lỗi hệ thống: {e}")
    st.info("Hệ thống đang tự động điều chỉnh cấu trúc Ô Trộn của file Excel...")
