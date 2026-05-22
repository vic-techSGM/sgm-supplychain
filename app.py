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
    
    # --- A. XỬ LÝ SHEET TỔNG HỢP (ĐỌC THEO INDEX TRÁNH LỖI MERGED) ---
    df_th_raw = pd.read_excel(url, sheet_name='Tổng hợp', header=1)
    
    # Index định vị: 1(Ngành), 2(Chủng loại), 3(Hãng), 4(Mã hàng), 10(Xuất bán), 14(Tồn kho), 15(Giá trị tồn)
    valid_cols = [i for i in [1, 2, 3, 4, 10, 14, 15] if i < df_th_raw.shape[1]]
    df_th = df_th_raw.iloc[:, valid_cols].copy()
    
    col_names = ['Nganh_Hang', 'Chung_Loai', 'Hang', 'SKU', 'Xuat_Ban_SL', 'Ton_Kho_SL', 'Ton_Kho_Value']
    df_th.columns = col_names[:len(valid_cols)]
    
    # Kiểm tra cột rủi ro HSD
    hsd_cols = [c for c in df_th_raw.columns if 'HSD' in str(c) or 'hạn' in str(c).lower()]
    df_th['Het_HSD_Value'] = pd.to_numeric(df_th_raw[hsd_cols[0]], errors='coerce').fillna(0) if hsd_cols else 0
    
    df_th = df_th.dropna(subset=['SKU'])
    df_th['SKU'] = df_th['SKU'].astype(str).str.strip()
    
    for col in ['Nganh_Hang', 'Chung_Loai', 'Hang']:
        if col in df_th.columns:
            df_th[col] = df_th[col].fillna('Khác').astype(str).str.strip()
            
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
    
    df = pd.merge(df_th, active_kh, on='SKU', how='left').fillna(0)
    return df

# ==========================================
# 3. GIAO DIỆN CHÍNH & THUẬT TOÁN LOGIC
# ==========================================
try:
    df_full = load_data()
    
    # --- SIDEBAR: BỘ ĐIỀU KHIỂN CHIẾN LƯỢC ---
    st.sidebar.image("https://raw.githubusercontent.com/vic-techSGM/sgm-supplychain/main/logo.png", use_container_width=True)
    st.sidebar.markdown("---")
    
    st.sidebar.header("⚙️ Tham số Chuỗi cung ứng")
    doi_target = st.sidebar.slider("DOI - Tồn kho mục tiêu (Ngày)", 15, 120, 45)
    lead_time = st.sidebar.slider("Lead Time - Thời gian nhập hàng (Ngày)", 10, 90, 30)
    customer_growth = st.sidebar.slider("Kỳ vọng tăng trưởng KH theo Quý (%)", 0, 100, 15, help="Tỷ lệ phình to nhu cầu thị trường")
    
    st.sidebar.header("📂 Bộ lọc Dữ liệu")
    list_nganh = df_full['Nganh_Hang'].unique().tolist()
    selected_nganh = st.sidebar.multiselect("1. Ngành hàng", list_nganh, default=list_nganh)
    
    df_f1 = df_full[df_full['Nganh_Hang'].isin(selected_nganh)]
    list_chungloai = df_f1['Chung_Loai'].unique().tolist() if 'Chung_Loai' in df_f1.columns else []
    selected_chungloai = st.sidebar.multiselect("2. Chủng loại", list_chungloai, default=list_chungloai) if list_chungloai else []
    
    df_f2 = df_f1[df_f1['Chung_Loai'].isin(selected_chungloai)] if selected_chungloai else df_f1
    list_hang = df_f2['Hang'].unique().tolist()
    selected_hang = st.sidebar.multiselect("3. Hãng cung cấp", list_hang, default=list_hang)

    # Áp dụng bộ lọc cuối cùng
    df = df_f2[df_f2['Hang'].isin(selected_hang)].copy()
    
    # --- THUẬT TOÁN TÍNH TOÁN DỰ TRÚ ---
    growth_factor = 1 + (customer_growth / 100)
    df['Daily_Sales'] = (df['Xuat_Ban_SL'] / 150) * growth_factor # Tốc độ bán đã tính tăng trưởng
    
    # Chỉ số S2S cục bộ dựa trên dữ liệu lọc
    df['S2S_Months'] = df['Ton_Kho_SL'] / ((df['Daily_Sales'] * 30) + 0.0001)
    
    # Chỉ số dự trù theo chu kỳ yêu cầu
    df['Du_Tru_Thang'] = df['Daily_Sales'] * 30
    df['Du_Tru_Quy'] = df['Daily_Sales'] * 90
    
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

    # Tính toán S2S Bình Quân của toàn bộ danh mục sau lọc
    total_daily_sales = df['Daily_Sales'].sum()
    avg_s2s_global = df['Ton_Kho_SL'].sum() / ((total_daily_sales * 30) + 0.0001) if total_daily_sales > 0 else 0

    # --- HERO SECTION: TẦNG Ô THỐNG KÊ BIẾN ĐỘNG ---
    st.title("🏥 Hệ thống Quản trị Cung ứng SGM")
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Tổng Vốn Tồn Kho", f"{df['Ton_Kho_Value'].sum():,.0f} ₫")
    m2.metric("Tổng Mã SKU (Đang lọc)", f"{len(df):,}")
    m3.metric("S2S Bình Quân (Tháng)", f"{avg_s2s_global:.1f} Tháng")
    m4.metric("Tổng KH Active", f"{int(df['Khach_Hang_Active'].sum()):,}")

    # --- CẤU TRÚC PHÂN PHỐI TABS ---
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📋 KẾ HOẠCH ĐẶT HÀNG", 
        "🔥 PHÂN LOẠI BÁN CHẠY", 
        "👥 TƯƠNG QUAN BIẾN ĐỘNG", 
        "🚩 RỦI RO HẠN DÙNG",
        "🔍 TÌM KIẾM CHI TIẾT"
    ])

    with tab1:
        st.subheader("📊 Tỷ trọng Phân bổ Dòng vốn")
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            st.plotly_chart(px.pie(df, values='Ton_Kho_Value', names='Nganh_Hang', hole=0.4, title="Theo Ngành Hàng"), use_container_width=True)
        with col_p2:
            st.plotly_chart(px.pie(df, values='Ton_Kho_Value', names='Hang', hole=0.4, title="Theo Hãng Cung Cấp"), use_container_width=True)

        st.subheader("🛒 Danh sách Kế hoạch Dự trù Đặt hàng")
        
        # Tách biệt, gán tên Tiếng Việt chuẩn hoá không dùng gạch dưới
        display_df = df[['SKU', 'Hang', 'Ton_Kho_SL', 'Khach_Hang_Active', 'Du_Tru_Thang', 'Du_Tru_Quy', 'De_Xuat_Mua', 'Trang_Thai', 'Canh_Bao_S2S']].copy()
        display_df.columns = [
            'Mã SKU', 'Hãng', 'Số Lượng Tồn Kho', 'Khách Hàng Active', 
            'Dự Trù Trong Tháng', 'Dự Trù 3 Tháng (Quý)', 'Số Lượng Cần Mua', 
            'Trạng Thái', 'Cảnh Báo S2S'
        ]
        
        st.dataframe(display_df.sort_values(by='Số Lượng Cần Mua', ascending=False), use_container_width=True, height=400)
        
        # Thêm nút xuất PO trực tiếp cho các mặt hàng cần mua
        po_df = display_df[display_df['Số Lượng Cần Mua'] > 0]
        st.download_button(
            label="📥 XUẤT FILE ĐƠN ĐẶT HÀNG CHUẨN (PO)", 
            data=po_df.to_csv(index=False).encode('utf-8-sig'), 
            file_name='SGM_Purchase_Order.csv',
            mime='text/csv'
        )

    with tab2:
        st.subheader("Phân loại SKU Bán chạy nhất")
        top_sku = df.sort_values(by='Xuat_Ban_SL', ascending=False).head(20)
        fig_bar = px.bar(
            top_sku, x='Xuat_Ban_SL', y='SKU', orientation='h', color='Hang',
            labels={'Xuat_Ban_SL': 'Tổng lượng xuất bán', 'SKU': 'Mã SKU'},
            title="Top 20 sản phẩm có sản lượng phân phối cao nhất"
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with tab3:
        st.subheader("Phân tích S2S & Mức độ Active của Khách hàng")
        fig_scatter = px.scatter(
            df, x="Khach_Hang_Active", y="S2S_Months", size="Ton_Kho_Value", color="Canh_Bao_S2S",
            hover_name="SKU", 
            labels={"Khach_Hang_Active": "Số Lượng Khách Hàng Active", "S2S_Months": "Tháng Tồn Kho thực tế (S2S)"},
            color_discrete_map={"⚠️ Chậm luân chuyển": "#d32f2f", "🔥 Rủi ro thiếu hàng": "#f57c00", "✅ Hợp lý": "#388e3c"}
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

    with tab4:
        st.subheader("Hàng Cận/Hết Date theo bộ lọc")
        risk_value = df['Het_HSD_Value'].sum()
        if risk_value > 0:
            st.error(f"Tổng giá trị hàng rủi ro trong nhóm đang lọc: {risk_value:,.0f} ₫")
            fig_risk = px.bar(df[df['Het_HSD_Value'] > 0], x='SKU', y='Het_HSD_Value', color='Hang', title="Chi tiết giá trị hao hụt")
            st.plotly_chart(fig_risk, use_container_width=True)
        else:
            st.success("Tất cả SKU trong phân nhóm lọc hiện tại đều an toàn.")

    with tab5:
        st.subheader("Tìm kiếm chi tiết theo SKU")
        selected_sku = st.selectbox("Gõ hoặc chọn Mã SKU cần kiểm tra:", df['SKU'].unique())
        if selected_sku:
            sku_data = df[df['SKU'] == selected_sku].iloc[0]
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Tồn kho thực tế", f"{sku_data['Ton_Kho_SL']:,.0f}")
            c2.metric("Nhu cầu bán/ngày (Đã tính tăng trưởng)", f"{sku_data['Daily_Sales']:.2f}")
            c3.metric("KH Active", int(sku_data['Khach_Hang_Active']))
            c4.metric("Tháng tồn hiện tại", f"{sku_data['S2S_Months']:.1f} Tháng")

except Exception as e:
    st.error(f"Lỗi đồng bộ cấu trúc hiển thị: {e}")
