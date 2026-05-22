import streamlit as st
import pandas as pd
import plotly.express as px
import datetime

# ==========================================
# 1. CẤU HÌNH GIAO DIỆN LIGHT MODE & FONT MONTSERRAT
# ==========================================
st.set_page_config(page_title="SGM Supply Chain Intel", page_icon="🏥", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    /* Nhúng font Montserrat đồng bộ toàn diện hệ thống */
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700;800;900&display=swap');
    html, body, [class*="css"], [class*="st-"], .stApp { 
        font-family: 'Montserrat', sans-serif !important; 
    }

    /* -----------------------------------
       1. KHU VỰC MAIN & SIDEBAR
       ----------------------------------- */
    .stApp, .main { background-color: #ffffff !important; }
    .stApp p, .stApp span, div[data-testid="stMarkdownContainer"] { color: #1e293b !important; }
    h1, h2, h3, h4, h5, h6 { color: #0f172a !important; font-weight: 800 !important; }

    /* Sidebar nền xám nhẹ */
    [data-testid="stSidebar"] {
        background-color: #f1f5f9 !important; 
        border-right: 1px solid #e2e8f0 !important;
    }
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] label { 
        color: #334155 !important; 
        font-weight: 600 !important;
    }
    [data-testid="stSidebar"] h4 { 
        color: #0f172a !important; 
        font-size: 22px !important; 
        font-weight: 900 !important; 
        margin-top: 25px !important;
        margin-bottom: 15px !important;
        border-bottom: 2px solid #cbd5e1;
        padding-bottom: 10px;
    }
    .copyright-text { font-size: 11px !important; color: #64748b !important; text-align: center; margin-top: -15px; margin-bottom: 25px; font-weight: 500; }

    /* Loại bỏ phông nền trắng của logo SGM */
    [data-testid="stSidebar"] img {
        mix-blend-mode: multiply;
    }

    /* Slider & Multiselect với tone màu Green Pastel */
    .stSlider > div > div > div > div { background-color: #cbd5e1 !important; }
    .stSlider > div > div > div > div > div { background-color: #86efac !important; }
    .stSlider > div > div > div > div > div[role="slider"] { background-color: #22c55e !important; box-shadow: 0 0 10px rgba(34,197,94,0.4) !important; }
    
    .stMultiSelect div[data-baseweb="select"] {
        background-color: #f0fdf4 !important; 
        border: 1px solid #86efac !important;
        border-radius: 8px !important;
    }
    .stMultiSelect div[data-baseweb="select"]:focus-within {
        border-color: #22c55e !important;
    }
    .stMultiSelect span[data-baseweb="tag"] { 
        background-color: #bbf7d0 !important; 
        border: 1px solid #86efac !important; 
    }
    .stMultiSelect span[data-baseweb="tag"] span { 
        color: #14532d !important; 
        font-weight: 700 !important; 
    }
    .stMultiSelect span[data-baseweb="tag"] svg {
        fill: #14532d !important;
    }

    /* -----------------------------------
       2. HIỆU ỨNG THẺ CARD 3D FLOATING (MÀU NGÀ / CAM PASTEL)
       ----------------------------------- */
    div[data-testid="stMetric"] {
        background: linear-gradient(145deg, #fffdfa, #fdf4e7) !important; 
        border-radius: 20px !important;
        padding: 25px !important;
        box-shadow: 6px 12px 24px rgba(139,92,26,0.08), -2px -2px 10px rgba(255,255,255,0.8) !important;
        border-left: 6px solid #fb923c !important; 
        border-top: 1px solid rgba(251,146,60,0.1) !important;
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
    }
    div[data-testid="stMetric"]:hover { 
        transform: translateY(-8px) scale(1.02); 
        box-shadow: 10px 18px 30px rgba(139,92,26,0.12), -2px -2px 12px rgba(255,255,255,0.9) !important; 
    }
    div[data-testid="stMetric"] label { 
        color: #c2410c !important; 
        font-size: 15px !important; 
        text-transform: uppercase; 
        font-weight: 800 !important; 
        letter-spacing: 0.5px; 
    }
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] { 
        color: #1e293b !important; 
        font-size: 36px !important; 
        font-weight: 900 !important; 
        text-shadow: none !important;
    }

    /* STICKY HERO SECTION TỰ ĐỘNG TRÊN NỀN SÁNG */
    div[data-testid="stVerticalBlock"] > div:has(div[data-testid="stMetric"]) {
        position: sticky;
        top: 2.8rem;
        z-index: 999;
        background-color: #ffffff;
        padding: 10px 0 20px 0;
        border-bottom: 1px solid #e2e8f0;
    }

    /* -----------------------------------
       3. TÙY BIẾN ĐÓNG FRAME CHO CÁC TABS THEO YÊU CẦU
       ----------------------------------- */
    button[data-baseweb="tab"] { 
        font-family: 'Montserrat', sans-serif !important;
        font-size: 19px !important; /* Tăng nhẹ kích cỡ */
        font-weight: 800 !important; /* In đậm */
        color: #475569 !important; /* Màu xám đậm */
        background-color: #f8fafc !important; 
        border: 1px solid #cbd5e1 !important; /* Đóng frame */
        border-radius: 8px !important; 
        margin-right: 10px !important;
        padding: 12px 24px !important;
        transition: all 0.2s ease-in-out !important;
    }
    button[aria-selected="true"] { 
        color: #388e3c !important; /* Màu green của logo */
        background-color: #ffffff !important; 
        border: 2px solid #388e3c !important; /* Khung dày màu green */
        box-shadow: 0 4px 12px rgba(56,142,60,0.1) !important;
    }

    .stDataFrame { 
        background: #ffffff !important; 
        border-radius: 16px; 
        padding: 10px; 
        box-shadow: 0 10px 25px rgba(0,0,0,0.05) !important; 
        border: 1px solid #e2e8f0; 
    }
    
    .stDownloadButton button { background-color: #388e3c !important; color: white !important; border-radius: 10px !important; font-weight: 800 !important; border: none !important; width: 100%; box-shadow: 0 8px 15px rgba(56,142,60,0.2); transition: all 0.3s ease; }
    .stDownloadButton button:hover { background-color: #2e7d32 !important; transform: translateY(-3px); box-shadow: 0 12px 20px rgba(56,142,60,0.4); }
    
    /* -----------------------------------
       4. SMART CARDS PHONG CÁCH LIGHT MODE
       ----------------------------------- */
    .smart-card-info { background: #eff6ff !important; border-left: 5px solid #3b82f6 !important; padding: 22px; border-radius: 12px; color: #1e3a8a !important; margin-bottom: 18px; box-shadow: 0 4px 12px rgba(59,130,246,0.08); border-top: 1px solid rgba(59,130,246,0.1); }
    .smart-card-success { background: #f0fdf4 !important; border-left: 5px solid #10b981 !important; padding: 22px; border-radius: 12px; color: #14532d !important; margin-bottom: 18px; box-shadow: 0 4px 12px rgba(16,185,129,0.08); border-top: 1px solid rgba(16,185,129,0.1); }
    .smart-card-error { background: #fef2f2 !important; border-left: 5px solid #ef4444 !important; padding: 22px; border-radius: 12px; color: #7f1d1d !important; margin-bottom: 18px; box-shadow: 0 4px 12px rgba(239,68,68,0.08); border-top: 1px solid rgba(239,68,68,0.1); }
    .smart-card-warning { background: #fffbeb !important; border-left: 5px solid #f59e0b !important; padding: 22px; border-radius: 12px; color: #78350f !important; margin-bottom: 18px; box-shadow: 0 4px 12px rgba(245,158,11,0.08); border-top: 1px solid rgba(245,158,11,0.1); }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. HỆ THỐNG XỬ LÝ DỮ LIỆU
# ==========================================
@st.cache_data(ttl=600)
def load_data():
    sheet_id = st.secrets["spreadsheet_id"]
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=xlsx"
    
    df_th_raw = pd.read_excel(url, sheet_name='Tổng hợp', header=1)
    
    hsd_col_idx = None
    for idx, col in enumerate(df_th_raw.columns):
        if any(keyword in str(col).lower() for keyword in ['hsd', 'hạn', 'date', 'quá hạn']):
            hsd_col_idx = idx
            break
            
    if hsd_col_idx is None and df_th_raw.shape[1] > 17:
        hsd_col_idx = 17

    target_indices = [1, 2, 3, 4, 10, 14, 15] 
    if hsd_col_idx is not None and hsd_col_idx not in target_indices:
        target_indices.append(hsd_col_idx)
        
    df_th = df_th_raw.iloc[:, target_indices].copy()
    
    base_cols = ['Nganh_Hang', 'Chung_Loai', 'Hang', 'SKU', 'Xuat_Ban_SL', 'Ton_Kho_SL', 'Ton_Kho_Value']
    if hsd_col_idx is not None:
        df_th.columns = base_cols + ['Het_HSD_Value']
    else:
        df_th.columns = base_cols
        df_th['Het_HSD_Value'] = 0
        
    df_th = df_th.dropna(subset=['SKU'])
    df_th['SKU'] = df_th['SKU'].astype(str).str.strip()
    
    for col in ['Nganh_Hang', 'Chung_Loai', 'Hang']:
        if col in df_th.columns: df_th[col] = df_th[col].fillna('Khác').astype(str).str.strip()
    for col in ['Xuat_Ban_SL', 'Ton_Kho_SL', 'Ton_Kho_Value', 'Het_HSD_Value']:
        if col in df_th.columns: df_th[col] = pd.to_numeric(df_th[col], errors='coerce').fillna(0)

    df_xb_raw = pd.read_excel(url, sheet_name='Xuất bán', header=1)
    cols = df_xb_raw.columns.tolist()
    cols[1] = 'SKU'
    df_xb_raw.columns = cols
    
    kh_cols = [c for c in df_xb_raw.columns if 'Khách hàng' in str(c)]
    kh_col_name = kh_cols[0] if kh_cols else df_xb_raw.columns[5]
    
    df_xb_raw['SKU'] = df_xb_raw['SKU'].astype(str).str.strip()
    df_xb_raw[kh_col_name] = df_xb_raw[kh_col_name].astype(str).str.strip()
    
    customer_mapping = df_xb_raw[['SKU', kh_col_name]].dropna().copy()
    customer_mapping.rename(columns={kh_col_name: 'Khach_Hang'}, inplace=True)
    customer_mapping = customer_mapping[customer_mapping['Khach_Hang'] != 'nan']
    
    active_kh = df_xb_raw.groupby('SKU')[kh_col_name].nunique().reset_index()
    active_kh.rename(columns={kh_col_name: 'Khach_Hang_Active'}, inplace=True)
    
    df = pd.merge(df_th, active_kh, on='SKU', how='left').fillna(0)
    return df, customer_mapping

# ==========================================
# 3. GIAO DIỆN CHÍNH & THUẬT TOÁN ĐIỀU PHỐI
# ==========================================
try:
    df_full, customer_mapping = load_data()
    today = datetime.date.today()
    
    # --- SIDEBAR MENU ---
    st.sidebar.image("https://raw.githubusercontent.com/vic-techSGM/sgm-supplychain/main/logo.png", use_container_width=True)
    st.sidebar.markdown("<div class='copyright-text'>Build & Developed by Vic Fan.<br>Copyrights reserved. Version 01.26.05</div>", unsafe_allow_html=True)
    
    st.sidebar.markdown("<h4>⚙️ THAM SỐ DỰ TRÙ</h4>", unsafe_allow_html=True)
    doi_target = st.sidebar.slider("Ngày tồn kho an toàn (DOI)", 15, 120, 45)
    st.sidebar.caption("💡 Các mốc: 15 (Nguy cơ) - 45 (Chuẩn) - 90 (Đọng vốn)")
    lead_time = st.sidebar.slider("Lead Time (Thời gian nhập)", 10, 90, 30)
    customer_growth = st.sidebar.slider("Kỳ vọng tăng trưởng Khách hàng theo Quý (%)", 0, 100, 15)
    
    st.sidebar.markdown("<h4>📂 BỘ LỌC DỮ LIỆU</h4>", unsafe_allow_html=True)
    list_nganh = df_full['Nganh_Hang'].unique().tolist()
    selected_nganh = st.sidebar.multiselect("Phân nhóm Ngành hàng", list_nganh, default=list_nganh)
    
    df_f1 = df_full[df_full['Nganh_Hang'].isin(selected_nganh)]
    list_chungloai = df_f1['Chung_Loai'].unique().tolist() if 'Chung_Loai' in df_f1.columns else []
    selected_chungloai = st.sidebar.multiselect("Chi tiết Chủng loại", list_chungloai, default=list_chungloai) if list_chungloai else []
    
    df_f2 = df_f1[df_f1['Chung_Loai'].isin(selected_chungloai)] if selected_chungloai else df_f1
    list_hang = df_f2['Hang'].unique().tolist()
    selected_hang = st.sidebar.multiselect("Nhà cung cấp (Hãng)", list_hang, default=list_hang)

    df = df_f2[df_f2['Hang'].isin(selected_hang)].copy()
    
    # --- THUẬT TOÁN TÍNH TOÁN ROP VÀ S2S ---
    growth_factor = 1 + (customer_growth / 100)
    df['Daily_Sales'] = (df['Xuat_Ban_SL'] / 150) * growth_factor 
    df['S2S_Months'] = df['Ton_Kho_SL'] / ((df['Daily_Sales'] * 30) + 0.0001)
    
    df['Du_Tru_Thang'] = df['Daily_Sales'] * 30
    df['Du_Tru_Quy'] = df['Daily_Sales'] * 90
    
    df['ROP_Qty'] = (lead_time * df['Daily_Sales']) + (doi_target * df['Daily_Sales'])
    df['De_Xuat_Mua'] = (df['ROP_Qty'] - df['Ton_Kho_SL']).apply(lambda x: max(int(x), 0))

    def calculate_reorder_date(row):
        if row['Daily_Sales'] <= 0: return "Chưa phát sinh"
        days_to_rop = (row['Ton_Kho_SL'] - row['ROP_Qty']) / row['Daily_Sales']
        if days_to_rop <= 0: return today.strftime("%d/%m/%Y") 
        future_date = today + datetime.timedelta(days=int(days_to_rop))
        return future_date.strftime("%d/%m/%Y")
        
    df['Ngay_Dat_Hang_Du_Kien'] = df.apply(calculate_reorder_date, axis=1)

    def get_status(row):
        if row['Ton_Kho_SL'] < (lead_time * row['Daily_Sales']): return "🔴 ĐỨT HÀNG"
        if row['Ton_Kho_SL'] < row['ROP_Qty']: return "🟡 CẦN NHẬP"
        return "🟢 AN TOÀN"
    
    def get_s2s_alert(row):
        if row['S2S_Months'] > 6: return "⚠️ Chậm luân chuyển"
        if row['S2S_Months'] < 1: return "🔥 Rủi ro thiếu hàng"
        return "✅ Hợp lý"

    df['Trang_Thai'] = df.apply(get_status, axis=1)
    df['Canh_Bao_S2S'] = df.apply(get_s2s_alert, axis=1)

    total_daily_sales = df['Daily_Sales'].sum()
    avg_s2s_global = df['Ton_Kho_SL'].sum() / ((total_daily_sales * 30) + 0.0001) if total_daily_sales > 0 else 0

    # --- HERO SECTION TỔNG QUAN ---
    st.markdown("<h2 style='font-weight: 900; margin-bottom: 5px; color: #0f172a;'>🏥 SGM SUPPLY CHAIN INTEL</h2>", unsafe_allow_html=True)
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("TỔNG VỐN TỒN KHO", f"{df['Ton_Kho_Value'].sum():,.0f} ₫")
    m2.metric("MÃ SKU ĐANG LỌC", f"{len(df):,}")
    m3.metric("S2S BÌNH QUÂN", f"{avg_s2s_global:.1f} Tháng")
    m4.metric("KHÁCH HÀNG ACTIVE", f"{int(df['Khach_Hang_Active'].sum()):,}")

    st.markdown("<br>", unsafe_allow_html=True)
    
    # --- ĐIỀU HƯỚNG TABS (ĐÃ ĐỔI THỨ TỰ BÁN CHẠY XUỐNG VỊ TRÍ THỨ 4) ---
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 TỔNG QUAN & ĐẶT HÀNG", 
        "👥 KHÁCH HÀNG THEO SKU", 
        "🚩 RỦI RO HẠN DÙNG",
        "📈 PHÂN LOẠI BÁN CHẠY", 
        "💡 TRA CỨU ĐỀ XUẤT"
    ])

    # --- TAB 1: TỔNG QUAN & ĐẶT HÀNG ---
    with tab1:
        st.markdown("<h4 style='font-weight: 800; margin-top: 10px;'>📊 Dashboard Tổng Quan Cơ Cấu Vốn</h4>", unsafe_allow_html=True)
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            fig_pie_nganh = px.pie(
                df, values='Ton_Kho_Value', names='Nganh_Hang', hole=0.4, 
                title="Tỷ trọng Vốn theo Ngành Hàng", 
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            fig_pie_nganh.update_traces(textposition='inside', textinfo='percent')
            fig_pie_nganh.update_layout(
                showlegend=False, 
                paper_bgcolor='rgba(0,0,0,0)', 
                plot_bgcolor='rgba(0,0,0,0)',
                margin=dict(t=50, b=20, l=10, r=10),
                font=dict(family="Montserrat", color="#1e293b")
            )
            st.plotly_chart(fig_pie_nganh, use_container_width=True)
            
        with col_p2:
            fig_pie_hang = px.pie(
                df, values='Ton_Kho_Value', names='Hang', hole=0.4, 
                title="Tỷ trọng Vốn theo Hãng Cung Cấp", 
                color_discrete_sequence=px.colors.qualitative.Set2
            )
            fig_pie_hang.update_traces(textposition='inside', textinfo='percent')
            fig_pie_hang.update_layout(
                showlegend=False, 
                paper_bgcolor='rgba(0,0,0,0)', 
                plot_bgcolor='rgba(0,0,0,0)',
                margin=dict(t=50, b=20, l=10, r=10),
                font=dict(family="Montserrat", color="#1e293b")
            )
            st.plotly_chart(fig_pie_hang, use_container_width=True)
            
        st.markdown("<p style='text-align: center; font-size: 13px; color: #64748b;'><i>*Trỏ chuột vào biểu đồ để xem chi tiết tên hãng/ngành và giá trị vốn cụ thể</i></p>", unsafe_allow_html=True)

        st.markdown("<h4 style='font-weight: 800; margin-top: 30px;'>🛒 Danh sách Kế hoạch Dự trù Đặt hàng</h4>", unsafe_allow_html=True)
        
        display_df = df[['SKU', 'Hang', 'Ton_Kho_SL', 'Khach_Hang_Active', 'Du_Tru_Thang', 'Du_Tru_Quy', 'Ngay_Dat_Hang_Du_Kien', 'De_Xuat_Mua', 'Trang_Thai', 'Canh_Bao_S2S']].copy()
        display_df.columns = [
            'Mã SKU', 'Hãng', 'Số Lượng Tồn Kho', 'Khách Hàng Active', 
            'Dự Trù Trong Tháng', 'Dự Trù 3 Tháng (Quý)', 'Ngày Đặt Hàng (ROP)', 
            'Số Lượng Cần Mua', 'Trạng Thái', 'Cảnh Báo S2S'
        ]
        
        styled_df = display_df.style.format({
            'Số Lượng Tồn Kho': "{:,.0f}",
            'Dự Trù Trong Tháng': "{:,.0f}",
            'Dự Trù 3 Tháng (Quý)': "{:,.0f}",
            'Số Lượng Cần Mua': "{:,.0f}"
        })
        st.dataframe(styled_df, use_container_width=True, height=350)
        
        st.markdown("""
        <div class="smart-card-info">
            <b style="color:#1d4ed8;">ℹ️ CƠ CHẾ DỰ BÁO NGÀY ĐẶT HÀNG (ROP DATE):</b><br>
            Hệ thống tự động ước lượng <b>Thời điểm chính xác cần xuống đơn PO (Ngày/Tháng/Năm)</b>. ROP Date được hệ thống "dịch chuyển" liên tục dựa vào 3 tham số thiết lập tại menu bên trái: <b>Tốc độ tăng trưởng KH</b>, thời gian <b>Lead Time</b> chở hàng về, và số ngày tồn trữ phòng hờ <b>DOI</b>.
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<h4 style='font-weight: 800; margin-top: 30px;'>📥 Xuất File Đơn Đặt Hàng (PO)</h4>", unsafe_allow_html=True)
        po_df = display_df[display_df['Số Lượng Cần Mua'] > 0].copy()
        
        if not po_df.empty:
            export_cols = st.multiselect(
                "Chọn các cột dữ liệu muốn trích xuất:", 
                options=po_df.columns.tolist(), 
                default=po_df.columns.tolist()
            )
            st.download_button(
                label="📥 TẢI XUỐNG FILE PO (CSV)", 
                data=po_df[export_cols].to_csv(index=False).encode('utf-8-sig'), 
                file_name=f'SGM_PO_{today.strftime("%Y%m%d")}.csv', 
                mime='text/csv'
            )
        else:
            st.success("Không có mặt hàng nào cần đặt mua trong danh mục lọc hiện tại.")

    # --- TAB 2: KHÁCH HÀNG THEO SKU (CHUYỂN LÊN VỊ TRÍ THỨ 2) ---
    with tab2:
        st.markdown("<h3 style='font-weight: 800;'>🔍 Phân bổ Khách hàng theo SKU (Treemap)</h3>", unsafe_allow_html=True)
        
        st.markdown("""
        <div class="smart-card-info">
            <b style="color:#1d4ed8;">💡 CÁCH ĐỌC BẢN ĐỒ NHIỆT:</b><br>
            - <b>Diện tích khối:</b> Đại diện tỷ trọng Tiền (Vốn Tồn Kho).<br>
            - <b>Màu sắc:</b> <span style="color:#15803d; font-weight:800;">Xanh lá (Hợp lý)</span> | <span style="color:#b45309; font-weight:800;">Cam (Nguy cơ thiếu)</span> | <span style="color:#b91c1c; font-weight:800;">Đỏ tươi (Chậm luân chuyển)</span>.
        </div>
        """, unsafe_allow_html=True)

        list_kh = sorted(customer_mapping['Khach_Hang'].unique().tolist())
        selected_kh = st.multiselect("Gõ tên để tìm kiếm Khách Hàng:", list_kh)
        
        df_tab3 = df.copy()
        if selected_kh:
            skus_of_kh = customer_mapping[customer_mapping['Khach_Hang'].isin(selected_kh)]['SKU'].unique()
            df_tab3 = df[df['SKU'].isin(skus_of_kh)]
            
            st.markdown(f"""
            <div class="smart-card-success">
                <b style="color:#15803d;">📊 ĐÁNH GIÁ TỆP KHÁCH HÀNG:</b> Nhóm khách hàng này tiêu thụ <b>{len(df_tab3)} mã SKU</b>, tổng vốn lưu trữ là <b>{df_tab3['Ton_Kho_Value'].sum():,.0f} ₫</b>.
            </div>
            """, unsafe_allow_html=True)
        
        if not df_tab3.empty and df_tab3['Ton_Kho_Value'].sum() > 0:
            fig_treemap = px.treemap(
                df_tab3[df_tab3['Ton_Kho_Value'] > 0],
                path=[px.Constant("CỤC DIỆN TỔN KHO"), 'Canh_Bao_S2S', 'Hang', 'SKU'],
                values='Ton_Kho_Value', 
                color='Canh_Bao_S2S',
                color_discrete_map={"⚠️ Chậm luân chuyển": "#ef4444", "🔥 Rủi ro thiếu hàng": "#f59e0b", "✅ Hợp lý": "#10b981"}
            )
            fig_treemap.update_traces(root_color="#f1f5f9")
            fig_treemap.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', 
                plot_bgcolor='rgba(0,0,0,0)', 
                margin=dict(t=30, l=10, r=10, b=10),
                font=dict(family="Montserrat", color="#1e293b")
            )
            st.plotly_chart(fig_treemap, use_container_width=True)
        else:
            st.warning("Không có dữ liệu tồn kho hợp lệ để khởi tạo Bản đồ nhiệt.")

    # --- TAB 3: RỦI RO HẠN DÙNG (CHUYỂN LÊN VỊ TRÍ THỨ 3) ---
    with tab3:
        st.markdown("<h3 style='font-weight: 800;'>🚩 Cảnh báo Hàng Cận/Hết Hạn</h3>", unsafe_allow_html=True)
        risk_df = df[df['Het_HSD_Value'] > 0].copy()
        
        st.metric(label="🚨 TỔNG GIÁ TRỊ THIỆT HẠI DỰ KIẾN", value=f"{risk_df['Het_HSD_Value'].sum():,.0f} ₫")
        
        if not risk_df.empty:
            # Sửa đổi chú thích trục cột Y & X thành tiếng Việt
            fig_risk = px.bar(
                risk_df, 
                x='SKU', 
                y='Het_HSD_Value', 
                color='Hang', 
                text='Het_HSD_Value',
                color_discrete_sequence=px.colors.qualitative.Set3,
                labels={
                    'Het_HSD_Value': 'Giá trị hết hạn',
                    'SKU': 'Mã SKU',
                    'Hang': 'Hãng sản xuất'
                }
            )
            fig_risk.update_traces(texttemplate='%{text:,.0f}', textposition='outside', marker=dict(cornerradius=6))
            fig_risk.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', 
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(family="Montserrat", color="#1e293b")
            )
            st.plotly_chart(fig_risk, use_container_width=True)
            
            # Chuyển bảng thông tin chi tiết sang Tiếng Việt và đổi tên cột cuối thành Giá trị thất thoát
            display_risk_df = risk_df[['SKU', 'Hang', 'Ton_Kho_SL', 'Het_HSD_Value']].copy()
            display_risk_df.columns = ['Mã SKU', 'Hãng', 'Số Lượng Tồn Kho', 'Giá trị thất thoát']
            
            st.dataframe(
                display_risk_df.style.format({
                    'Số Lượng Tồn Kho': "{:,.0f}", 
                    'Giá trị thất thoát': "{:,.0f} ₫"
                }), 
                use_container_width=True
            )
        else: 
            st.markdown("<div class='smart-card-success'><b style='color:#15803d;'>✅ TRẠNG THÁI AN TOÀN:</b> Không ghi nhận rủi ro cận hạn.</div>", unsafe_allow_html=True)

    # --- TAB 4: PHÂN LOẠI BÁN CHẠY (CHUYỂN XUỐNG VỊ TRÍ THỨ 4) ---
    with tab4:
        st.markdown("<h3 style='font-weight: 800;'>🔥 Top 20 SKU Bán Chạy Nhất</h3>", unsafe_allow_html=True)
        
        top_sku = df.sort_values(by='Xuat_Ban_SL', ascending=False).head(20).sort_values(by='Xuat_Ban_SL', ascending=True)
        
        st.markdown("<h4 style='font-weight: 700; margin-top: 10px;'>1. Sản lượng Xuất bán theo Mã SKU</h4>", unsafe_allow_html=True)
        fig_bar = px.bar(
            top_sku, 
            x='Xuat_Ban_SL', 
            y='SKU', 
            orientation='h', 
            color='SKU', 
            color_discrete_sequence=px.colors.qualitative.Pastel, 
            text='Xuat_Ban_SL',
            labels={'Xuat_Ban_SL': 'Sản lượng', 'SKU': 'Mã SKU'}
        )
        fig_bar.update_traces(
            texttemplate='%{text:,.0f}', 
            textposition='outside', 
            marker_line_width=0, 
            marker=dict(cornerradius=8)
        )
        fig_bar.update_layout(
            showlegend=False, 
            paper_bgcolor='rgba(0,0,0,0)', 
            plot_bgcolor='rgba(0,0,0,0)', 
            height=500, 
            yaxis=dict(automargin=True),
            font=dict(family="Montserrat", color="#1e293b")
        )
        st.plotly_chart(fig_bar, use_container_width=True)
            
        st.markdown("<h4 style='font-weight: 700; margin-top: 30px;'>2. Phân bổ Tỷ trọng (%) Top 20 SKU</h4>", unsafe_allow_html=True)
        fig_pie_sales = px.pie(
            top_sku, 
            values='Xuat_Ban_SL', 
            names='SKU', 
            hole=0.4, 
            color='SKU', 
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig_pie_sales.update_traces(textposition='inside', textinfo='percent')
        fig_pie_sales.update_layout(
            height=600, 
            showlegend=False, 
            paper_bgcolor='rgba(0,0,0,0)', 
            plot_bgcolor='rgba(0,0,0,0)', 
            margin=dict(t=30, b=30, l=10, r=10),
            font=dict(family="Montserrat", color="#1e293b")
        )
        st.plotly_chart(fig_pie_sales, use_container_width=True)

    # --- TAB 5: TRA CỨU ĐỀ XUẤT ---
    with tab5:
        st.markdown("<h3 style='font-weight: 800;'>🔍 Tra cứu chi tiết & Đề xuất AI</h3>", unsafe_allow_html=True)
        selected_sku = st.selectbox("Chọn Mã SKU cần phân tích:", df['SKU'].unique())
        
        if selected_sku:
            sku_data = df[df['SKU'] == selected_sku].iloc[0]
            
            c_desc1, c_desc2, c_desc3 = st.columns(3)
            c_desc1.info(f"**📂 Ngành:** {sku_data['Nganh_Hang']}")
            c_desc2.info(f"**🔬 Chủng loại:** {sku_data['Chung_Loai']}")
            c_desc3.info(f"**🏭 Hãng:** {sku_data['Hang']}")
            
            st.markdown("<br>", unsafe_allow_html=True)
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Tồn thực tế", f"{sku_data['Ton_Kho_SL']:,.0f}")
            c2.metric("Bán/ngày", f"{sku_data['Daily_Sales']:.2f}")
            c3.metric("KH Active", int(sku_data['Khach_Hang_Active']))
            c4.metric("S2S", f"{sku_data['S2S_Months']:.1f} T")
            
            st.markdown("<h4 style='font-weight: 800; margin-top: 30px; margin-bottom: 20px;'>🧠 ENGINE ĐỀ XUẤT ĐIỀU PHỐI</h4>", unsafe_allow_html=True)
            
            if sku_data['Trang_Thai'] == "🔴 ĐỨT HÀNG": 
                st.markdown(f"<div class='smart-card-error'><b style='color:#b91c1c;'>🚨 BÁO ĐỘNG ĐỨT HÀNG:</b> Tồn hiện tại thấp hơn Lead Time. Mua ngay <b>{sku_data['De_Xuat_Mua']:,.0f}</b> đơn vị. Hạn cuối: <b>{sku_data['Ngay_Dat_Hang_Du_Kien']}</b>.</div>", unsafe_allow_html=True)
            elif sku_data['Trang_Thai'] == "🟡 CẦN NHẬP": 
                st.markdown(f"<div class='smart-card-warning'><b style='color:#b45309;'>⚠️ KẾ HOẠCH NHẬP:</b> Đã chạm ngưỡng ROP. Bổ sung <b>{sku_data['De_Xuat_Mua']:,.0f}</b> đơn vị trước ngày <b>{sku_data['Ngay_Dat_Hang_Du_Kien']}</b>.</div>", unsafe_allow_html=True)
            else: 
                st.markdown(f"<div class='smart-card-success'><b style='color:#15803d;'>🟢 AN TOÀN:</b> Chưa cần nhập thêm. Dự kiến đến <b>{sku_data['Ngay_Dat_Hang_Du_Kien']}</b> mới cần lên đơn.</div>", unsafe_allow_html=True)
                
            if sku_data['S2S_Months'] > 6: 
                st.markdown(f"<div class='smart-card-error'><b style='color:#b91c1c;'>📦 ĐỌNG VỐN:</b> S2S đạt <b>{sku_data['S2S_Months']:.1f} tháng</b>. Rà soát Sale hoặc ngưng nhập.</div>", unsafe_allow_html=True)
            elif sku_data['S2S_Months'] < 1 and sku_data['Daily_Sales'] > 0: 
                st.markdown("<div class='smart-card-warning'><b style='color:#b45309;'>🔥 ÁP LỰC TIÊU THỤ LỚN:</b> Vòng quay kho dưới 1 tháng. Cần nâng DOI.</div>", unsafe_allow_html=True)
                
            if sku_data['Het_HSD_Value'] > 0: 
                st.markdown(f"<div class='smart-card-error'><b style='color:#b91c1c;'>🚩 RỦI RO HSD:</b> Thiệt hại dự kiến <b>{sku_data['Het_HSD_Value']:,.0f} ₫</b>. Áp dụng FEFO ngay.</div>", unsafe_allow_html=True)

except Exception as e:
    st.error(f"Lỗi hệ thống nội bộ: {e}")
