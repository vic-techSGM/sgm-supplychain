import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ==========================================
# 1. CẤU HÌNH GIAO DIỆN MODERN TECH SGM
# ==========================================
st.set_page_config(page_title="SGM Supply Chain Intel", page_icon="🏥", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    /* Font Inter hiện đại */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }

    /* Nền tổng thể */
    .main { background-color: #f0f2f6; }

    /* SIDEBAR (MENU BỘ LỌC) */
    [data-testid="stSidebar"] {
        background-color: #f8f9fa !important;
        border-right: 1px solid #e9ecef !important;
        box-shadow: 2px 0 10px rgba(0,0,0,0.05);
    }
    
    /* Chữ bản quyền dưới Logo */
    .copyright-text {
        font-size: 11px;
        color: #9e9e9e;
        text-align: center;
        margin-top: -15px;
        margin-bottom: 20px;
        font-weight: 400;
    }

    /* CARD STYLE HERO SECTION (Shadow + Pastel Green) */
    div[data-testid="stMetric"] {
        background-color: #e8f5e9 !important; /* Green Pastel nhẹ */
        border-radius: 16px !important;
        padding: 24px !important;
        box-shadow: 0 8px 20px rgba(56,142,60,0.15) !important;
        border-left: 6px solid #388e3c !important; 
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    div[data-testid="stMetric"]:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 25px rgba(56,142,60,0.25) !important;
    }
    div[data-testid="stMetric"] label { font-weight: 800 !important; font-size: 15px !important; color: #2e7d32 !important; }
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] { color: #1b5e20 !important; font-weight: 800 !important; }

    /* TABS STYLE NỔI BẬT */
    button[data-baseweb="tab"] { 
        font-size: 17px !important; 
        font-weight: 700 !important; 
        color: #757575 !important;
        background: #ffffff;
        border-radius: 10px 10px 0 0;
        margin-right: 5px;
        padding: 10px 20px;
        box-shadow: 0px -2px 8px rgba(0,0,0,0.04);
    }
    button[aria-selected="true"] { 
        color: #2e7d32 !important; 
        background-color: #e8f5e9 !important;
        border-bottom: 3px solid #388e3c !important; 
        box-shadow: 0px -4px 12px rgba(56,142,60,0.2) !important;
    }
    
    /* BẢNG DỮ LIỆU & NÚT DOWNLOAD */
    .stDataFrame { border-radius: 12px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.08); }
    .stDownloadButton button { background-color: #388e3c !important; color: white !important; border-radius: 8px !important; font-weight: 700; border: none !important; width: 100%; box-shadow: 0 4px 6px rgba(56,142,60,0.3); }
    .stDownloadButton button:hover { background-color: #2e7d32 !important; transform: translateY(-2px); box-shadow: 0 6px 12px rgba(56,142,60,0.4); }
    
    /* CẤU TRÚC SMART CARD (THẺ ĐỀ XUẤT THÔNG MINH) */
    .smart-card-info { background-color: #e3f2fd; border-left: 5px solid #1976d2; padding: 16px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.05); margin-bottom: 12px; }
    .smart-card-warning { background-color: #fff3e0; border-left: 5px solid #f57c00; padding: 16px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.05); margin-bottom: 12px; }
    .smart-card-error { background-color: #ffebee; border-left: 5px solid #d32f2f; padding: 16px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.05); margin-bottom: 12px; }
    .smart-card-success { background-color: #e8f5e9; border-left: 5px solid #388e3c; padding: 16px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.05); margin-bottom: 12px; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. HỆ THỐNG XỬ LÝ DỮ LIỆU BỌC THÉP (TTL 10 PHÚT)
# ==========================================
@st.cache_data(ttl=600)
def load_data():
    sheet_id = st.secrets["spreadsheet_id"]
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=xlsx"
    
    # --- A. XỬ LÝ SHEET TỔNG HỢP ---
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
        if col in df_th.columns: 
            df_th[col] = df_th[col].fillna('Khác').astype(str).str.strip()
            
    for col in ['Xuat_Ban_SL', 'Ton_Kho_SL', 'Ton_Kho_Value', 'Het_HSD_Value']:
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
    df_xb_raw[kh_col_name] = df_xb_raw[kh_col_name].astype(str).str.strip()
    
    customer_mapping = df_xb_raw[['SKU', kh_col_name]].dropna().copy()
    customer_mapping.rename(columns={kh_col_name: 'Khach_Hang'}, inplace=True)
    customer_mapping = customer_mapping[customer_mapping['Khach_Hang'] != 'nan']
    
    active_kh = df_xb_raw.groupby('SKU')[kh_col_name].nunique().reset_index()
    active_kh.rename(columns={kh_col_name: 'Khach_Hang_Active'}, inplace=True)
    
    # --- C. HỢP NHẤT DỮ LIỆU KHO ---
    df = pd.merge(df_th, active_kh, on='SKU', how='left').fillna(0)
    return df, customer_mapping

# ==========================================
# 3. GIAO DIỆN CHÍNH & THUẬT TOÁN
# ==========================================
try:
    df_full, customer_mapping = load_data()
    
    # --- SIDEBAR MENU ---
    st.sidebar.image("https://raw.githubusercontent.com/vic-techSGM/sgm-supplychain/main/logo.png", use_container_width=True)
    st.sidebar.markdown("<div class='copyright-text'>Build & Developed by Vic Fan.<br>Copyrights reserved. Version 01.26.05</div>", unsafe_allow_html=True)
    
    st.sidebar.markdown("<h4 style='color:#388e3c; font-weight:800;'>⚙️ CẤU HÌNH HỆ THỐNG</h4>", unsafe_allow_html=True)
    doi_target = st.sidebar.slider("📅 DOI (Ngày an toàn)", 15, 120, 45)
    lead_time = st.sidebar.slider("⏱️ Lead Time (Ngày nhập)", 10, 90, 30)
    customer_growth = st.sidebar.slider("📈 Tăng trưởng KH Quý (%)", 0, 100, 15)
    
    st.sidebar.markdown("<h4 style='color:#388e3c; font-weight:800; margin-top:20px;'>📂 BỘ LỌC DỮ LIỆU</h4>", unsafe_allow_html=True)
    list_nganh = df_full['Nganh_Hang'].unique().tolist()
    selected_nganh = st.sidebar.multiselect("1. Ngành hàng", list_nganh, default=list_nganh)
    
    df_f1 = df_full[df_full['Nganh_Hang'].isin(selected_nganh)]
    list_chungloai = df_f1['Chung_Loai'].unique().tolist() if 'Chung_Loai' in df_f1.columns else []
    selected_chungloai = st.sidebar.multiselect("2. Chủng loại", list_chungloai, default=list_chungloai) if list_chungloai else []
    
    df_f2 = df_f1[df_f1['Chung_Loai'].isin(selected_chungloai)] if selected_chungloai else df_f1
    list_hang = df_f2['Hang'].unique().tolist()
    selected_hang = st.sidebar.multiselect("3. Hãng cung cấp", list_hang, default=list_hang)

    # Dữ liệu sau lọc
    df = df_f2[df_f2['Hang'].isin(selected_hang)].copy()
    
    # --- THUẬT TOÁN TÍNH TOÁN ---
    growth_factor = 1 + (customer_growth / 100)
    df['Daily_Sales'] = (df['Xuat_Ban_SL'] / 150) * growth_factor 
    df['S2S_Months'] = df['Ton_Kho_SL'] / ((df['Daily_Sales'] * 30) + 0.0001)
    
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

    total_daily_sales = df['Daily_Sales'].sum()
    avg_s2s_global = df['Ton_Kho_SL'].sum() / ((total_daily_sales * 30) + 0.0001) if total_daily_sales > 0 else 0

    # --- HERO SECTION ---
    st.markdown("<h2 style='font-weight: 800; color: #1b5e20;'>🏥 SGM SUPPLY CHAIN INTEL</h2>", unsafe_allow_html=True)
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("💰 TỔNG VỐN TỒN KHO", f"{df['Ton_Kho_Value'].sum():,.0f} ₫")
    m2.metric("📦 MÃ SKU ĐANG LỌC", f"{len(df):,}")
    m3.metric("🔥 S2S BÌNH QUÂN", f"{avg_s2s_global:.1f} Tháng")
    m4.metric("👥 KHÁCH HÀNG ACTIVE", f"{int(df['Khach_Hang_Active'].sum()):,}")

    # --- ĐIỀU HƯỚNG TABS ---
    st.markdown("<br>", unsafe_allow_html=True)
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📋 KẾ HOẠCH ĐẶT HÀNG", 
        "🔥 PHÂN LOẠI BÁN CHẠY", 
        "👥 KHÁCH HÀNG THEO SKU", 
        "🚩 RỦI RO HẠN DÙNG",
        "🔍 TRA CỨU ĐỀ XUẤT"
    ])

    with tab1:
        st.subheader("📊 Tỷ trọng Phân bổ Dòng vốn")
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            st.plotly_chart(px.pie(df, values='Ton_Kho_Value', names='Nganh_Hang', hole=0.4, title="Theo Ngành Hàng", color_discrete_sequence=px.colors.qualitative.Pastel), use_container_width=True)
        with col_p2:
            st.plotly_chart(px.pie(df, values='Ton_Kho_Value', names='Hang', hole=0.4, title="Theo Hãng Cung Cấp", color_discrete_sequence=px.colors.qualitative.Set2), use_container_width=True)

        st.subheader("🛒 Danh sách Kế hoạch Dự trù Đặt hàng")
        display_df = df[['SKU', 'Hang', 'Ton_Kho_SL', 'Khach_Hang_Active', 'Du_Tru_Thang', 'Du_Tru_Quy', 'De_Xuat_Mua', 'Trang_Thai', 'Canh_Bao_S2S']].copy()
        display_df.columns = [
            'Mã SKU', 'Hãng', 'Số Lượng Tồn Kho', 'Khách Hàng Active', 
            'Dự Trù Trong Tháng', 'Dự Trù 3 Tháng (Quý)', 'Số Lượng Cần Mua', 
            'Trạng Thái', 'Cảnh Báo S2S'
        ]
        st.dataframe(display_df.sort_values(by='Số Lượng Cần Mua', ascending=False), use_container_width=True, height=400)
        
        po_df = display_df[display_df['Số Lượng Cần Mua'] > 0]
        st.download_button(
            label="📥 XUẤT FILE ĐƠN ĐẶT HÀNG CHUẨN (PO)", 
            data=po_df.to_csv(index=False).encode('utf-8-sig'), 
            file_name='SGM_Purchase_Order.csv', mime='text/csv'
        )

    with tab2:
        st.markdown("<h3 style='font-weight: 700;'>🔥 Top 20 SKU Bán Chạy Nhất (Theo Sản Lượng)</h3>", unsafe_allow_html=True)
        
        # Lấy top 20, sắp xếp tăng dần để vẽ nằm ngang từ trên xuống
        top_sku = df.sort_values(by='Xuat_Ban_SL', ascending=True).tail(20)
        
        # Vẽ biểu đồ ngang, màu sắc Pantone Xanh Pastel (Blues)
        fig_bar = px.bar(
            top_sku, 
            x='Xuat_Ban_SL', 
            y='SKU', 
            orientation='h', 
            color='Xuat_Ban_SL', # Tự động đổ màu gradient theo giá trị
            color_continuous_scale="Blues", # Thang màu Pantone Pastel Blue
            text='Xuat_Ban_SL',
            labels={'Xuat_Ban_SL': 'Sản Lượng Phân Phối', 'SKU': 'Mã SKU'}
        )
        
        # Bo cong góc thanh Bar (Cập nhật Plotly mới nhất) và ẩn thanh thang màu
        fig_bar.update_traces(
            texttemplate='%{text:,.0f}', 
            textposition='outside', 
            marker_line_width=0,
            marker=dict(cornerradius=10) # Bo góc thanh bar
        )
        fig_bar.update_layout(
            coloraxis_showscale=False, # Ẩn cột màu bên cạnh cho giao diện clean
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis_title="Sản lượng xuất bán (Chiều ngang)",
            yaxis_title="Mã SKU",
            height=650 
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with tab3:
        st.markdown("<h3 style='font-weight: 700;'>🔍 Khách hàng theo SKU (Bản đồ Nhiệt S2S)</h3>", unsafe_allow_html=True)
        
        # Thẻ Hướng Dẫn UI
        st.markdown("""
        <div class="smart-card-info">
            <b style="color:#0d47a1; font-size: 16px;">💡 CÁCH ĐỌC BẢN ĐỒ NHIỆT (TREEMAP):</b><br>
            <span style="color:#1565c0; font-size: 14px;">
            - <b>Kích thước Khối hộp:</b> Đại diện cho lượng Tiền/Vốn tồn kho. Hộp càng to, tiền đọng càng lớn.<br>
            - <b>Màu sắc:</b> <span style="color:#2e7d32; font-weight:bold;">Xanh (Hợp lý)</span> | <span style="color:#e65100; font-weight:bold;">Cam (Nguy cơ đứt hàng)</span> | <span style="color:#c62828; font-weight:bold;">Đỏ (Tồn kho quá lâu - Trượt vòng quay vốn)</span>.
            </span>
        </div>
        """, unsafe_allow_html=True)

        list_kh = sorted(customer_mapping['Khach_Hang'].unique().tolist())
        selected_kh = st.multiselect("Gõ tên để tìm kiếm Khách Hàng (Hỗ trợ chọn nhiều):", list_kh)
        
        df_tab3 = df.copy()
        if selected_kh:
            skus_of_kh = customer_mapping[customer_mapping['Khach_Hang'].isin(selected_kh)]['SKU'].unique()
            df_tab3 = df[df['SKU'].isin(skus_of_kh)]
            
            # Giải thích thông minh tự động khi chọn Khách Hàng
            tong_von_kh = df_tab3['Ton_Kho_Value'].sum()
            so_ma_kh = len(df_tab3)
            st.markdown(f"""
            <div class="smart-card-success">
                <b style="color:#1b5e20;">📊 KẾT QUẢ ĐÁNH GIÁ TỆP KHÁCH HÀNG:</b><br>
                <span style="color:#2e7d32;">
                Tệp khách hàng bạn vừa chọn đang liên đới tới <b>{so_ma_kh} mã SKU</b>, với tổng dòng vốn lưu kho phục vụ trực tiếp là <b>{tong_von_kh:,.0f} VNĐ</b>. Hãy xem Bản đồ nhiệt bên dưới để rà soát xem có khối màu đỏ nào (hàng tồn kho lâu) đang bị kẹt tại nhóm khách này không.
                </span>
            </div>
            """, unsafe_allow_html=True)
        
        if not df_tab3.empty and df_tab3['Ton_Kho_Value'].sum() > 0:
            fig_treemap = px.treemap(
                df_tab3[df_tab3['Ton_Kho_Value'] > 0],
                path=[px.Constant("TỔNG TỒN KHO"), 'Canh_Bao_S2S', 'Hang', 'SKU'],
                values='Ton_Kho_Value', color='Canh_Bao_S2S',
                color_discrete_map={"⚠️ Chậm luân chuyển": "#ef5350", "🔥 Rủi ro thiếu hàng": "#ff9800", "✅ Hợp lý": "#66bb6a"}
            )
            fig_treemap.update_traces(root_color="#f8f9fa")
            fig_treemap.update_layout(margin=dict(t=30, l=10, r=10, b=10))
            st.plotly_chart(fig_treemap, use_container_width=True)
        else:
            st.warning("Không có dữ liệu vốn tồn kho để khởi tạo Bản đồ nhiệt.")

    with tab4:
        st.markdown("<h3 style='font-weight: 700;'>🚩 Cảnh báo Hàng Cận/Hết Hạn (FEFO)</h3>", unsafe_allow_html=True)
        risk_df = df[df['Het_HSD_Value'] > 0].copy()
        total_risk = risk_df['Het_HSD_Value'].sum()
        
        st.metric(label="🚨 TỔNG GIÁ TRỊ THIỆT HẠI DỰ KIẾN (Theo Lọc)", value=f"{total_risk:,.0f} ₫")
        
        if total_risk > 0:
            fig_risk = px.bar(
                risk_df, x='SKU', y='Het_HSD_Value', color='Hang', text='Het_HSD_Value',
                labels={'SKU': 'Mã SKU', 'Het_HSD_Value': 'Giá trị thiệt hại (₫)'},
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig_risk.update_traces(texttemplate='%{text:,.0f}', textposition='outside', marker_line_width=0, marker=dict(cornerradius=5))
            st.plotly_chart(fig_risk, use_container_width=True)
            
            st.markdown("#### 📋 Danh sách chi tiết SKU cận/hết hạn sử dụng")
            risk_display = risk_df[['SKU', 'Hang', 'Ton_Kho_SL', 'Het_HSD_Value']].copy()
            risk_display.columns = ['Mã SKU', 'Hãng Cung Cấp', 'Số Lượng Tồn', 'Giá Trị Mất Đi (VNĐ)']
            st.dataframe(risk_display.sort_values(by='Giá Trị Mất Đi (VNĐ)', ascending=False), use_container_width=True)
        else:
            st.markdown("<div class='smart-card-success'><b style='color:#1b5e20;'>✅ AN TOÀN:</b> Hệ thống ghi nhận không có rủi ro cận hạn hoặc hết hạn đối với nhóm danh mục đang chọn.</div>", unsafe_allow_html=True)

    with tab5:
        st.markdown("<h3 style='font-weight: 700;'>🔍 Tra cứu chi tiết & Đề xuất AI</h3>", unsafe_allow_html=True)
        selected_sku = st.selectbox("Gõ hoặc chọn Mã SKU cần phân tích:", df['SKU'].unique())
        
        if selected_sku:
            sku_data = df[df['SKU'] == selected_sku].iloc[0]
            
            c_desc1, c_desc2, c_desc3 = st.columns(3)
            c_desc1.info(f"**📂 Ngành hàng:**\n\n {sku_data['Nganh_Hang']}")
            c_desc2.info(f"**🔬 Chủng loại:**\n\n {sku_data['Chung_Loai']}")
            c_desc3.info(f"**🏭 Hãng cung cấp:**\n\n {sku_data['Hang']}")
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Tồn kho thực tế", f"{sku_data['Ton_Kho_SL']:,.0f}")
            c2.metric("Nhu cầu bán/ngày", f"{sku_data['Daily_Sales']:.2f}")
            c3.metric("Số KH Active", int(sku_data['Khach_Hang_Active']))
            c4.metric("Tháng tồn (S2S)", f"{sku_data['S2S_Months']:.1f} Tháng")
            
            st.markdown("<h4 style='font-weight: 700; margin-top: 20px;'>🧠 Đề xuất điều phối từ Hệ thống AI</h4>", unsafe_allow_html=True)
            
            if sku_data['Trang_Thai'] == "🔴 ĐỨT HÀNG":
                st.markdown(f"<div class='smart-card-error'><b style='color:#c62828;'>🚨 CẢNH BÁO KHẨN CẤP (ĐỨT HÀNG):</b><br><span style='color:#d32f2f;'>Số lượng tồn kho hiện tại thấp hơn mức an toàn Lead Time. Yêu cầu phòng mua hàng phát hành ngay đơn PO với số lượng <b>{sku_data['De_Xuat_Mua']:,.0f}</b> để bảo vệ chuỗi cung ứng.</span></div>", unsafe_allow_html=True)
            elif sku_data['Trang_Thai'] == "🟡 CẦN NHẬP":
                st.markdown(f"<div class='smart-card-warning'><b style='color:#e65100;'>⚠️ KẾ HOẠCH NHẬP BỔ SUNG:</b><br><span style='color:#f57c00;'>Mặt hàng đang nằm dưới điểm đặt hàng lại (ROP). Khuyến nghị bổ sung mua <b>{sku_data['De_Xuat_Mua']:,.0f}</b> sản phẩm trong đợt gom đơn tuần này.</span></div>", unsafe_allow_html=True)
            else:
                st.markdown("<div class='smart-card-success'><b style='color:#1b5e20;'>🟢 TỒN KHO AN TOÀN:</b><br><span style='color:#2e7d32;'>Mức trữ lượng hiện tại đáp ứng cực tốt chu kỳ vận hành đã thiết lập.</span></div>", unsafe_allow_html=True)
                
            if sku_data['S2S_Months'] > 6:
                st.markdown(f"<div class='smart-card-error'><b style='color:#c62828;'>📦 RỦI RO ĐỌNG VỐN (S2S):</b><br><span style='color:#d32f2f;'>Chỉ số Stock-to-Sales đạt {sku_data['S2S_Months']:.1f} tháng (vượt ngưỡng 6 tháng). Đề xuất Sale rà soát khách hàng, tổ chức xúc tiến bán hoặc ngưng nhập liệu mã này.</span></div>", unsafe_allow_html=True)
            elif sku_data['S2S_Months'] < 1 and sku_data['Daily_Sales'] > 0:
                st.markdown("<div class='smart-card-warning'><b style='color:#e65100;'>🔥 ÁP LỰC TIÊU THỤ LỚN:</b><br><span style='color:#f57c00;'>Vòng quay kho dưới 1 tháng. Sức mua đang tăng mạnh, cần cân nhắc nâng tồn kho mục tiêu (DOI) để tối ưu chi phí vận chuyển.</span></div>", unsafe_allow_html=True)
                
            if sku_data['Het_HSD_Value'] > 0:
                st.markdown(f"<div class='smart-card-error'><b style='color:#c62828;'>🚩 BÁO ĐỘNG HẠN SỬ DỤNG:</b><br><span style='color:#d32f2f;'>Mã SKU đang gánh khoản thiệt hại dự kiến <b>{sku_data['Het_HSD_Value']:,.0f} ₫</b>. Áp dụng ngay nguyên tắc xuất kho FEFO và đẩy mạnh xử lý hàng cận date.</span></div>", unsafe_allow_html=True)

except Exception as e:
    st.error(f"Lỗi hệ thống nội bộ: {e}")
