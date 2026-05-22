import streamlit as st
import pandas as pd
import plotly.express as px

# ==========================================
# 1. CẤU HÌNH GIAO DIỆN SGM MEDICAL TECH
# ==========================================
st.set_page_config(page_title="SGM Supply Chain Intel", page_icon="🏥", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    .main { background-color: #f4f7f9; }
    div[data-testid="stMetric"] {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        border-left: 6px solid #F58220; 
        transition: transform 0.2s ease-in-out;
    }
    div[data-testid="stMetric"]:hover { transform: translateY(-5px); }
    button[data-baseweb="tab"] { font-size: 16px; font-weight: 600; color: #555; }
    button[aria-selected="true"] { color: #F58220 !important; border-bottom-color: #F58220 !important; }
    .stDownloadButton button { background-color: #388e3c !important; color: white !important; border-radius: 8px !important; font-weight: bold; border: none !important; width: 100%; }
    .stDownloadButton button:hover { background-color: #2e7d32 !important; }
    [data-testid="stSidebar"] { background-color: #ffffff; border-right: 1px solid #e0e0e0; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. HỆ THỐNG XỬ LÝ DỮ LIỆU BỌC THÉP
# ==========================================
@st.cache_data(ttl=600)
def load_data():
    sheet_id = st.secrets["spreadsheet_id"]
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=xlsx"
    
    # --- A. XỬ LÝ SHEET TỔNG HỢP ---
    df_th_raw = pd.read_excel(url, sheet_name='Tổng hợp', header=1)
    
    # Index: 1(Ngành), 2(Chủng loại), 3(Hãng), 4(SKU), 10(Xuất bán), 14(Tồn kho), 15(Giá trị tồn)
    valid_cols = [i for i in [1, 2, 3, 4, 10, 14, 15] if i < df_th_raw.shape[1]]
    df_th = df_th_raw.iloc[:, valid_cols].copy()
    
    col_names = ['Nganh_Hang', 'Chung_Loai', 'Hang', 'SKU', 'Xuat_Ban_SL', 'Ton_Kho_SL', 'Ton_Kho_Value']
    df_th.columns = col_names[:len(valid_cols)]
    
    # Tìm cột Hết HSD (Nếu có)
    hsd_cols = [c for c in df_th_raw.columns if 'HSD' in str(c) or 'hạn' in str(c).lower()]
    df_th['Het_HSD_Value'] = pd.to_numeric(df_th_raw[hsd_cols[0]], errors='coerce').fillna(0) if hsd_cols else 0
    
    # Làm sạch
    df_th = df_th.dropna(subset=['SKU'])
    df_th['SKU'] = df_th['SKU'].astype(str).str.strip()
    
    for col in ['Nganh_Hang', 'Chung_Loai', 'Hang']:
        if col in df_th.columns:
            df_th[col] = df_th[col].fillna('Khác').astype(str)
            
    for col in ['Xuat_Ban_SL', 'Ton_Kho_SL', 'Ton_Kho_Value']:
        if col in df_th.columns:
            df_th[col] = pd.to_numeric(df_th[col], errors='coerce').fillna(0)

    # --- B. XỬ LÝ SHEET XUẤT BÁN ---
    df_xb_raw = pd.read_excel(url, sheet_name='Xuất bán', header=1)
    cols = df_xb_raw.columns.tolist()
    cols[1] = 'SKU'
    df_xb_raw.columns = cols
    
    kh_cols = [c for c in df_xb_raw.columns if 'Khách hàng' in str(c)]
    kh_col_name = kh_cols[0] if kh_cols else df_xb_raw.columns[5]
    
    df_xb_raw['SKU'] = df_xb_raw['SKU'].astype(str).str.strip()
    active_kh = df_xb_raw.groupby('SKU')[kh_col_name].nunique().reset_index()
    active_kh.rename(columns={kh_col_name: 'Khach_Hang_Active'}, inplace=True)
    
    # --- C. MERGE ---
    df = pd.merge(df_th, active_kh, on='SKU', how='left').fillna(0)
    return df

# ==========================================
# 3. GIAO DIỆN & TÍNH TOÁN LOGIC
# ==========================================
try:
    df_full = load_data()
    
    # --- SIDEBAR: BỘ LỌC ĐA TẦNG ---
    st.sidebar.image("https://raw.githubusercontent.com/vic-techSGM/sgm-supplychain/main/logo.png", use_container_width=True)
    st.sidebar.markdown("---")
    
    st.sidebar.header("🎯 Tham số Cung ứng")
    doi_target = st.sidebar.slider("DOI (Tồn kho mục tiêu - Ngày)", 15, 120, 45)
    lead_time = st.sidebar.slider("Lead Time (Ngày nhập hàng)", 10, 90, 30)
    
    st.sidebar.header("📂 Bộ lọc Dữ liệu")
    list_nganh = df_full['Nganh_Hang'].unique().tolist()
    selected_nganh = st.sidebar.multiselect("1. Ngành hàng", list_nganh, default=list_nganh)
    
    df_f1 = df_full[df_full['Nganh_Hang'].isin(selected_nganh)]
    list_chungloai = df_f1['Chung_Loai'].unique().tolist() if 'Chung_Loai' in df_f1.columns else []
    selected_chungloai = st.sidebar.multiselect("2. Chủng loại", list_chungloai, default=list_chungloai) if list_chungloai else []
    
    df_f2 = df_f1[df_f1['Chung_Loai'].isin(selected_chungloai)] if selected_chungloai else df_f1
    list_hang = df_f2['Hang'].unique().tolist()
    selected_hang = st.sidebar.multiselect("3. Hãng cung cấp", list_hang, default=list_hang)

    # DataFrame đã lọc hoàn chỉnh
    df = df_f2[df_f2['Hang'].isin(selected_hang)].copy()
    
    # --- THUẬT TOÁN ROP & S2S ---
    df['Daily_Sales'] = df['Xuat_Ban_SL'] / 150 # Trung bình 5 tháng
    df['S2S_Months'] = df['Ton_Kho_SL'] / ((df['Daily_Sales'] * 30) + 0.0001) # Tháng tồn kho
    df['ROP'] = (lead_time * df['Daily_Sales']) + (doi_target * df['Daily_Sales'])
    df['De_Xuat_Mua'] = (df['ROP'] - df['Ton_Kho_SL']).apply(lambda x: max(int(x), 0))

    def get_status(row):
        if row['Ton_Kho_SL'] < (lead_time * row['Daily_Sales']): return "🔴 ĐỨT HÀNG"
        if row['Ton_Kho_SL'] < row['ROP']: return "🟡 CẦN NHẬP"
        return "🟢 AN TOÀN"
    
    def get_s2s_alert(row):
        if row['S2S_Months'] > 6: return "⚠️ Chậm luân chuyển"
        if row['S2S_Months'] < 1: return "🔥 Rủi ro thiếu hàng"
        return "✅ Hợp lý"

    df['Trang_Thai'] = df.apply(get_status, axis=1)
    df['Canh_Bao_S2S'] = df.apply(get_s2s_alert, axis=1)

    # --- TỔNG QUAN DASHBOARD ---
    st.title("🏥 Hệ thống Quản trị Cung ứng SGM")
    
    # Metrics linh động theo bộ lọc
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Tổng Vốn Tồn Kho", f"{df['Ton_Kho_Value'].sum():,.0f} ₫")
    m2.metric("Tổng Mã SKU", len(df))
    m3.metric("Số SKU Cần Đặt Hàng", len(df[df['De_Xuat_Mua'] > 0]))
    m4.metric("Tổng KH Active", int(df['Khach_Hang_Active'].sum()))

    # --- 5 TABS CHUYÊN SÂU ---
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 TỔNG QUAN & DỰ TRÙ", 
        "🔥 SKU BÁN CHẠY", 
        "👥 TƯƠNG QUAN (S2S)", 
        "🚩 RỦI RO HẠN DÙNG",
        "🔍 TRA CỨU CHI TIẾT"
    ])

    with tab1:
        st.subheader("Cơ cấu Vốn Tồn Kho")
        col_pie1, col_pie2 = st.columns(2)
        with col_pie1:
            fig_pie1 = px.pie(df, values='Ton_Kho_Value', names='Nganh_Hang', hole=0.4, title="Theo Ngành Hàng")
            st.plotly_chart(fig_pie1, use_container_width=True)
        with col_pie2:
            fig_pie2 = px.pie(df, values='Ton_Kho_Value', names='Hang', hole=0.4, title="Theo Hãng Cung Cấp")
            st.plotly_chart(fig_pie2, use_container_width=True)

        st.subheader("🛒 Bảng Kế hoạch Đặt hàng tự động")
        display_cols = ['SKU', 'Chung_Loai', 'Ton_Kho_SL', 'S2S_Months', 'Khach_Hang_Active', 'ROP', 'De_Xuat_Mua', 'Trang_Thai', 'Canh_Bao_S2S']
        st.dataframe(df[display_cols].sort_values(by='De_Xuat_Mua', ascending=False), use_container_width=True)

    with tab2:
        st.subheader("Top 20 SKU có sản lượng bán cao nhất")
        top_sku = df.sort_values(by='Xuat_Ban_SL', ascending=False).head(20)
        fig_bar = px.bar(top_sku, x='Xuat_Ban_SL', y='SKU', orientation='h', color='Hang', title="Sản lượng xuất bán (Lịch sử)")
        st.plotly_chart(fig_bar, use_container_width=True)

    with tab3:
        st.subheader("Phân tích S2S & Mức độ Active của Khách hàng")
        fig_scatter = px.scatter(
            df, x="Khach_Hang_Active", y="S2S_Months", size="Ton_Kho_Value", color="Canh_Bao_S2S",
            hover_name="SKU", 
            labels={"Khach_Hang_Active": "Số Lượng Khách Hàng", "S2S_Months": "Tháng Tồn Kho (S2S)"},
            color_discrete_map={"⚠️ Chậm luân chuyển": "#d32f2f", "🔥 Rủi ro thiếu hàng": "#f57c00", "✅ Hợp lý": "#388e3c"}
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

    with tab4:
        st.subheader("Cảnh báo Hàng Cận/Hết Date")
        if df['Het_HSD_Value'].sum() > 0:
            st.error(f"Tổng thiệt hại dự kiến: {df['Het_HSD_Value'].sum():,.0f} ₫")
            risk_df =df[df['Het_HSD_Value'] > 0]
            fig_risk = px.bar(risk_df, x='SKU', y='Het_HSD_Value', color='Hang', title="Giá trị thiệt hại theo SKU")
            st.plotly_chart(fig_risk, use_container_width=True)
            st.dataframe(risk_df[['SKU', 'Hang', 'Ton_Kho_SL', 'Het_HSD_Value']], use_container_width=True)
        else:
            st.success("Tất cả SKU trong bộ lọc hiện tại đều an toàn về Hạn sử dụng.")

    with tab5:
        st.subheader("Tra cứu Thông số chi tiết từng SKU")
        selected_sku = st.selectbox("Gõ hoặc chọn Mã SKU cần kiểm tra:", df['SKU'].unique())
        
        if selected_sku:
            sku_data = df[df['SKU'] == selected_sku].iloc[0]
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Tồn kho hiện tại", f"{sku_data['Ton_Kho_SL']:,.0f}")
            c2.metric("Sức bán/ngày", f"{sku_data['Daily_Sales']:.2f}")
            c3.metric("KH Active", int(sku_data['Khach_Hang_Active']))
            c4.metric("Tháng tồn (S2S)", f"{sku_data['S2S_Months']:.1f} tháng")
            
            st.markdown("---")
            st.write(f"**Trạng thái nhập hàng:** {sku_data['Trang_Thai']}")
            st.write(f"**Cảnh báo luân chuyển:** {sku_data['Canh_Bao_S2S']}")
            st.write(f"**Điểm đặt hàng (ROP):** {sku_data['ROP']:,.0f}")
            st.write(f"**Đề xuất mua ngay:** {sku_data['De_Xuat_Mua']:,.0f}")

except Exception as e:
    st.error(f"Lỗi khởi tạo hệ thống: {e}")
