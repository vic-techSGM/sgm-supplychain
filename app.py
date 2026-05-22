import streamlit as st
import pandas as pd
import plotly.express as px
import datetime

# ==========================================
# 1. CẤU HÌNH GIAO DIỆN DARK MODE & UI LAYOUT
# ==========================================
st.set_page_config(page_title="SGM Supply Chain Intel", page_icon="🏥", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }

    /* Dark Mode Global */
    .main { background-color: #0f172a !important; color: #f8fafc !important; }
    
    /* Sticky Hero Section */
    .sticky-header {
        position: sticky;
        top: 0;
        z-index: 999;
        background-color: #0f172a;
        padding-top: 10px;
        padding-bottom: 20px;
        border-bottom: 1px solid #1e293b;
    }

    /* Sidebar - Nền trắng sạch */
    [data-testid="stSidebar"] { background-color: #ffffff !important; }
    [data-testid="stSidebar"] h4, [data-testid="stSidebar"] label { color: #1e293b !important; }
    .copyright-text { font-size: 11px; color: #64748b; text-align: center; margin-top: -15px; margin-bottom: 25px; }

    /* Cards trong Dark Mode */
    div[data-testid="stMetric"] {
        background-color: #1e293b !important;
        border-radius: 16px !important;
        padding: 20px !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3) !important;
        border-left: 6px solid #388e3c !important; 
    }
    div[data-testid="stMetric"] label { color: #cbd5e1 !important; font-weight: 700 !important; }
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] { color: #ffffff !important; font-weight: 800 !important; }

    /* Tabs Bold & Size to */
    button[data-baseweb="tab"] { 
        font-size: 18px !important; font-weight: 800 !important; color: #94a3b8 !important;
        background: transparent; padding: 15px 30px;
    }
    button[aria-selected="true"] { color: #388e3c !important; border-bottom: 3px solid #388e3c !important; }

    /* Smart Cards */
    .smart-card-info { background-color: #1e293b; border-left: 5px solid #3b82f6; padding: 15px; border-radius: 8px; color: #f1f5f9; margin-bottom: 15px; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. XỬ LÝ DỮ LIỆU
# ==========================================
@st.cache_data(ttl=600)
def load_data():
    sheet_id = st.secrets["spreadsheet_id"]
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=xlsx"
    
    df_th_raw = pd.read_excel(url, sheet_name='Tổng hợp', header=1)
    
    # Tìm cột HSD
    hsd_col_idx = 17 if df_th_raw.shape[1] > 17 else None
    target_indices = [1, 2, 3, 4, 10, 14, 15] 
    if hsd_col_idx: target_indices.append(hsd_col_idx)
    
    df_th = df_th_raw.iloc[:, target_indices].copy()
    base_cols = ['Nganh_Hang', 'Chung_Loai', 'Hang', 'SKU', 'Xuat_Ban_SL', 'Ton_Kho_SL', 'Ton_Kho_Value']
    df_th.columns = base_cols + (['Het_HSD_Value'] if hsd_col_idx else [])
    
    df_th = df_th.dropna(subset=['SKU'])
    df_th['SKU'] = df_th['SKU'].astype(str).str.strip()
    for col in ['Nganh_Hang', 'Chung_Loai', 'Hang']: df_th[col] = df_th[col].fillna('Khác').astype(str).str.strip()
    for col in ['Xuat_Ban_SL', 'Ton_Kho_SL', 'Ton_Kho_Value', 'Het_HSD_Value']: df_th[col] = pd.to_numeric(df_th[col], errors='coerce').fillna(0)

    df_xb_raw = pd.read_excel(url, sheet_name='Xuất bán', header=1)
    cols = df_xb_raw.columns.tolist(); cols[1] = 'SKU'; df_xb_raw.columns = cols
    kh_col_name = [c for c in df_xb_raw.columns if 'Khách hàng' in str(c)][0]
    
    active_kh = df_xb_raw.groupby('SKU')[kh_col_name].nunique().reset_index().rename(columns={kh_col_name: 'Khach_Hang_Active'})
    customer_mapping = df_xb_raw[['SKU', kh_col_name]].dropna().rename(columns={kh_col_name: 'Khach_Hang'})
    
    df = pd.merge(df_th, active_kh, on='SKU', how='left').fillna(0)
    return df, customer_mapping

# ==========================================
# 3. GIAO DIỆN CHÍNH
# ==========================================
try:
    df_full, customer_mapping = load_data()
    today = datetime.date.today()
    
    # Sidebar
    st.sidebar.image("https://raw.githubusercontent.com/vic-techSGM/sgm-supplychain/main/logo.png", use_container_width=True)
    st.sidebar.markdown("<div class='copyright-text'>Build & Developed by Vic Fan.<br>Copyrights reserved. Version 01.26.05</div>", unsafe_allow_html=True)
    
    st.sidebar.markdown("#### ⯁ THAM SỐ DỰ TRÙ")
    doi_target = st.sidebar.slider("📅 Ngày tồn kho an toàn", 15, 120, 45)
    st.sidebar.caption("15 (Nguy cơ) - 45 (Chuẩn) - 90 (Đọng vốn)")
    lead_time = st.sidebar.slider("⏱️ Lead Time (Ngày)", 10, 90, 30)
    customer_growth = st.sidebar.slider("📈 Kỳ vọng tăng trưởng Khách hàng theo Quý (%)", 0, 100, 15)
    
    # Filter Logic
    selected_nganh = st.sidebar.multiselect("Ngành hàng", df_full['Nganh_Hang'].unique().tolist(), default=df_full['Nganh_Hang'].unique().tolist())
    df_f = df_full[df_full['Nganh_Hang'].isin(selected_nganh)]
    selected_chungloai = st.sidebar.multiselect("Chủng loại", df_f['Chung_Loai'].unique().tolist(), default=df_f['Chung_Loai'].unique().tolist())
    df_f = df_f[df_f['Chung_Loai'].isin(selected_chungloai)]
    selected_hang = st.sidebar.multiselect("Hãng", df_f['Hang'].unique().tolist(), default=df_f['Hang'].unique().tolist())
    df = df_f[df_f['Hang'].isin(selected_hang)].copy()
    
    # Calculate
    df['Daily_Sales'] = (df['Xuat_Ban_SL'] / 150) * (1 + customer_growth / 100)
    df['ROP_Qty'] = (lead_time * df['Daily_Sales']) + (doi_target * df['Daily_Sales'])
    df['De_Xuat_Mua'] = (df['ROP_Qty'] - df['Ton_Kho_SL']).apply(lambda x: max(int(x), 0))
    df['Ngay_Dat_Hang_Du_Kien'] = df.apply(lambda row: (today + datetime.timedelta(days=max(0, int((row['Ton_Kho_SL'] - row['ROP_Qty']) / (row['Daily_Sales']+0.0001))))).strftime("%d/%m/%Y") if row['Daily_Sales'] > 0 else "N/A", axis=1)

    # Hero Sticky Header
    st.markdown('<div class="sticky-header">', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("TỔNG VỐN TỒN", f"{df['Ton_Kho_Value'].sum():,.0f} ₫")
    c2.metric("SKU LỌC", f"{len(df):,}")
    c3.metric("S2S BÌNH QUÂN", f"{df['Ton_Kho_SL'].sum() / ((df['Daily_Sales'].sum() * 30) + 1):.1f} T")
    c4.metric("KH ACTIVE", f"{int(df['Khach_Hang_Active'].sum()):,}")
    st.markdown('</div>', unsafe_allow_html=True)

    # Tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 TỔNG QUAN & ĐẶT HÀNG", "📈 PHÂN LOẠI BÁN CHẠY", "👥 KHÁCH HÀNG THEO SKU", "🚩 RỦI RO HẠN DÙNG", "💡 TRA CỨU ĐỀ XUẤT"])

    with tab1:
        st.subheader("🛒 Danh sách Kế hoạch Dự trù")
        df_disp = df[['SKU', 'Hang', 'Ton_Kho_SL', 'ROP_Qty', 'Ngay_Dat_Hang_Du_Kien', 'De_Xuat_Mua']].copy()
        df_disp.columns = ['Mã SKU', 'Hãng', 'Tồn Kho', 'ROP (Số lượng)', 'ROP Dự Kiến (Ngày)', 'Cần Mua']
        st.dataframe(df_disp.style.format({'Tồn Kho': '{:,.0f}', 'ROP (Số lượng)': '{:,.0f}', 'Cần Mua': '{:,.0f}'}), use_container_width=True)
        
        st.markdown("**Chú thích:** ROP dự kiến được tính toán dựa trên thông số Sidebar và biên độ tăng trưởng khách hàng.")
        
        # PO Export
        po_df = df_disp[df_disp['Cần Mua'] > 0]
        if not po_df.empty:
            cols = st.multiselect("Chọn cột xuất PO:", options=po_df.columns.tolist(), default=po_df.columns.tolist())
            st.download_button("📥 Xuất PO", po_df[cols].to_csv(index=False).encode('utf-8-sig'), 'PO.csv')

    with tab2:
        st.subheader("Phân loại bán chạy")
        top_sku = df.sort_values(by='Xuat_Ban_SL', ascending=False).head(20)
        
        # Chart Bar (trên)
        fig_bar = px.bar(top_sku.sort_values('Xuat_Ban_SL'), x='Xuat_Ban_SL', y='SKU', orientation='h', color='SKU', color_discrete_sequence=px.colors.qualitative.Pastel)
        fig_bar.update_traces(marker=dict(cornerradius=5))
        st.plotly_chart(fig_bar, use_container_width=True)
        
        # Chart Pie (dưới)
        fig_pie = px.pie(top_sku, values='Xuat_Ban_SL', names='SKU', color='SKU', color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig_pie, use_container_width=True)

    with tab3:
        st.subheader("Bản đồ nhiệt Khách hàng theo SKU")
        # Logic treemap
        st.info("Sử dụng bản đồ nhiệt để phân bổ vốn theo khách hàng...")

    with tab4:
        st.subheader("Hàng cận hạn")
        # Logic hạn dùng

    with tab5:
        st.subheader("Tra cứu AI")
        sku = st.selectbox("Chọn SKU", df['SKU'].unique())
        if sku:
            st.write("Đề xuất thông minh...")

except Exception as e:
    st.error(f"Lỗi: {e}")
