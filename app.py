import streamlit as st
import pandas as pd
import plotly.express as px

# ==========================================
# 1. CẤU HÌNH GIAO DIỆN SGM MEDICAL TECH (PASTEL GREEN & FLOATING UI)
# ==========================================
st.set_page_config(page_title="SGM Supply Chain Intel", page_icon="🏥", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif !important;
    }
    
    .main { background-color: #f4f7f9; }
    
    /* -----------------------------------
       HIỆU ỨNG THẺ METRIC (HERO SECTION) 
       ----------------------------------- */
    div[data-testid="stMetric"] {
        background-color: #f1f8e9 !important; /* Màu xanh pastel nhẹ nhàng */
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 8px 16px rgba(56, 142, 60, 0.2) !important; /* Shadow xanh lá */
        border-left: 6px solid #388e3c !important; 
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    div[data-testid="stMetric"]:hover { 
        transform: translateY(-8px); 
        box-shadow: 0 12px 24px rgba(56, 142, 60, 0.4) !important; /* Shadow đậm hơn khi hover */
    }
    /* In đậm tiêu đề thẻ Metric */
    div[data-testid="stMetric"] label {
        font-weight: 800 !important;
        font-size: 16px !important;
        color: #2e7d32 !important;
    }
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        color: #1b5e20 !important;
        font-weight: 800 !important;
    }
    
    /* -----------------------------------
       HIỆU ỨNG TABS (FLOATING TABS)
       ----------------------------------- */
    button[data-baseweb="tab"] { 
        font-size: 18px !important; 
        font-weight: 700 !important; 
        color: #757575 !important; 
        background-color: #ffffff;
        border-radius: 12px 12px 0 0;
        margin-right: 6px;
        padding: 12px 24px;
        box-shadow: 0px -2px 8px rgba(56, 142, 60, 0.1);
        transition: all 0.3s ease;
    }
    button[data-baseweb="tab"]:hover {
        color: #388e3c !important;
        background-color: #f8fbf8;
    }
    button[aria-selected="true"] { 
        color: #2e7d32 !important; 
        background-color: #e8f5e9 !important; /* Tab đang chọn sáng màu pastel */
        border-bottom-color: #2e7d32 !important; 
        box-shadow: 0px -6px 15px rgba(56, 142, 60, 0.35) !important; /* Shadow xanh nổi bật */
        transform: translateY(-2px);
    }
    
    /* -----------------------------------
       MENU SIDEBAR & BỘ LỌC (IN ĐẬM + PASTEL)
       ----------------------------------- */
    [data-testid="stSidebar"] { 
        background-color: #ffffff; 
        border-right: 1px solid #e0e0e0; 
    }
    /* In đậm các nhãn bộ lọc và thanh trượt */
    [data-testid="stSidebar"] label {
        font-weight: 700 !important;
        font-size: 15px !important;
        color: #1b5e20 !important;
    }
    /* Đổi màu slider sang xanh pastel */
    .stSlider > div > div > div > div { background-color: #a5d6a7 !important; }
    .stSlider > div > div > div > div > div[role="slider"] { 
        background-color: #388e3c !important; 
        box-shadow: 0 0 8px rgba(56, 142, 60, 0.5) !important; 
    }
    /* Đổi màu MultiSelect Tags */
    .stMultiSelect span[data-baseweb="tag"] {
        background-color: #e8f5e9 !important;
        color: #2e7d32 !important;
        font-weight: 700;
        border: 1px solid #a5d6a7;
    }
    
    /* Nút Download */
    .stDownloadButton button { background-color: #388e3c !important; color: white !important; border-radius: 8px !important; font-weight: 700; border: none !important; width: 100%; box-shadow: 0 4px 6px rgba(56,142,60,0.3); }
    .stDownloadButton button:hover { background-color: #2e7d32 !important; transform: translateY(-2px); box-shadow: 0 6px 12px rgba(56,142,60,0.4); }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. HỆ THỐNG XỬ LÝ DỮ LIỆU TỰ ĐỘNG CẬP NHẬT
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
# 3. GIAO DIỆN CHÍNH & THUẬT TOÁN ĐỀ XUẤT
# ==========================================
try:
    df_full, customer_mapping = load_data()
    
    # --- SIDEBAR CONTROLS ---
    st.sidebar.image("https://raw.githubusercontent.com/vic-techSGM/sgm-supplychain/main/logo.png", use_container_width=True)
    st.sidebar.markdown("---")
    
    st.sidebar.header("⚙️ Tham số Chuỗi cung ứng")
    doi_target = st.sidebar.slider("DOI - Tồn kho mục tiêu (Ngày)", 15, 120, 45)
    lead_time = st.sidebar.slider("Lead Time - Thời gian nhập hàng (Ngày)", 10, 90, 30)
    customer_growth = st.sidebar.slider("Kỳ vọng tăng trưởng KH theo Quý (%)", 0, 100, 15)
    
    st.sidebar.header("📂 Bộ lọc Dữ liệu")
    list_nganh = df_full['Nganh_Hang'].unique().tolist()
    selected_nganh = st.sidebar.multiselect("1. Ngành hàng", list_nganh, default=list_nganh)
    
    df_f1 = df_full[df_full['Nganh_Hang'].isin(selected_nganh)]
    list_chungloai = df_f1['Chung_Loai'].unique().tolist() if 'Chung_Loai' in df_f1.columns else []
    selected_chungloai = st.sidebar.multiselect("2. Chủng loại", list_chungloai, default=list_chungloai) if list_chungloai else []
    
    df_f2 = df_f1[df_f1['Chung_Loai'].isin(selected_chungloai)] if selected_chungloai else df_f1
    list_hang = df_f2['Hang'].unique().tolist()
    selected_hang = st.sidebar.multiselect("3. Hãng cung cấp", list_hang, default=list_hang)

    df = df_f2[df_f2['Hang'].isin(selected_hang)].copy()
    
    # --- THUẬT TOÁN PHÂN TÍCH TỒN KHO AN TOÀN ---
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
    st.title("🏥 Hệ thống Quản trị Cung ứng SGM")
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("TỔNG VỐN TỒN KHO", f"{df['Ton_Kho_Value'].sum():,.0f} ₫")
    m2.metric("TỔNG MÃ SKU (ĐANG LỌC)", f"{len(df):,}")
    m3.metric("S2S BÌNH QUÂN", f"{avg_s2s_global:.1f} Tháng")
    m4.metric("TỔNG KH ACTIVE", f"{int(df['Khach_Hang_Active'].sum()):,}")

    # --- ĐIỀU HƯỚNG TABS ---
    st.markdown("<br>", unsafe_allow_html=True)
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📋 KẾ HOẠCH ĐẶT HÀNG", 
        "🔥 PHÂN LOẠI BÁN CHẠY", 
        "👥 BẢN ĐỒ S2S", 
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
        st.subheader("🔥 Top 20 SKU Bán Chạy Nhất (Theo Sản Lượng)")
        # Lấy top 20, sắp xếp tăng dần để Plotly vẽ từ trên xuống dưới cho biểu đồ ngang
        top_sku = df.sort_values(by='Xuat_Ban_SL', ascending=True).tail(20)
        
        # Biểu đồ cột ngang (Horizontal Bar Chart)
        fig_bar = px.bar(
            top_sku, 
            x='Xuat_Ban_SL', 
            y='SKU', 
            orientation='h', 
            color='Hang', 
            text='Xuat_Ban_SL',
            labels={'Xuat_Ban_SL': 'Tổng lượng xuất bán', 'SKU': 'Mã SKU'},
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig_bar.update_traces(texttemplate='%{text:,.0f}', textposition='outside', marker_line_width=0)
        fig_bar.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis_title="Sản lượng xuất bán",
            yaxis_title="Mã SKU",
            height=600 # Tăng chiều cao để các thanh hiển thị thoáng hơn
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with tab3:
        st.subheader("🔍 Bản đồ Tồn kho S2S & Tra cứu theo Khách hàng")
        list_kh = sorted(customer_mapping['Khach_Hang'].unique().tolist())
        selected_kh = st.multiselect("Tìm kiếm SKU theo Khách hàng (Có thể chọn nhiều):", list_kh)
        
        df_tab3 = df.copy()
        if selected_kh:
            skus_of_kh = customer_mapping[customer_mapping['Khach_Hang'].isin(selected_kh)]['SKU'].unique()
            df_tab3 = df[df['SKU'].isin(skus_of_kh)]
            st.success(f"Đã lọc ra {len(df_tab3)} Mã SKU liên quan đến khách hàng đã chọn.")
        
        if not df_tab3.empty and df_tab3['Ton_Kho_Value'].sum() > 0:
            fig_treemap = px.treemap(
                df_tab3[df_tab3['Ton_Kho_Value'] > 0],
                path=[px.Constant("TỔNG TỒN KHO S2S"), 'Canh_Bao_S2S', 'Hang', 'SKU'],
                values='Ton_Kho_Value', color='Canh_Bao_S2S',
                color_discrete_map={"⚠️ Chậm luân chuyển": "#d32f2f", "🔥 Rủi ro thiếu hàng": "#f57c00", "✅ Hợp lý": "#388e3c"}
            )
            fig_treemap.update_traces(root_color="lightgrey")
            fig_treemap.update_layout(margin=dict(t=30, l=10, r=10, b=10))
            st.plotly_chart(fig_treemap, use_container_width=True)
        else:
            st.warning("Không có dữ liệu tồn kho để vẽ bản đồ cho khách hàng này.")

    with tab4:
        st.subheader("🚩 Cảnh báo Hàng Cận/Hết Hạn và Đánh giá Thiệt hại")
        risk_df = df[df['Het_HSD_Value'] > 0].copy()
        total_risk = risk_df['Het_HSD_Value'].sum()
        
        st.metric(label="🚨 TỔNG GIÁ TRỊ THIỆT HẠI DỰ KIẾN (Đang lọc)", value=f"{total_risk:,.0f} ₫")
        
        if total_risk > 0:
            fig_risk = px.bar(
                risk_df, x='SKU', y='Het_HSD_Value', color='Hang', text='Het_HSD_Value',
                labels={'SKU': 'Mã SKU', 'Het_HSD_Value': 'Giá trị thiệt hại (₫)'},
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig_risk.update_traces(texttemplate='%{text:,.0f}', textposition='outside', marker_line_width=0)
            st.plotly_chart(fig_risk, use_container_width=True)
            
            st.markdown("#### 📋 Danh sách chi tiết SKU cận/hết hạn sử dụng")
            risk_display = risk_df[['SKU', 'Hang', 'Ton_Kho_SL', 'Het_HSD_Value']].copy()
            risk_display.columns = ['Mã SKU', 'Hãng Cung Cấp', 'Số Lượng Tồn', 'Giá Trị Mất Đi (VNĐ)']
            st.dataframe(risk_display.sort_values(by='Giá Trị Mất Đi (VNĐ)', ascending=False), use_container_width=True)
        else:
            st.success("Hệ thống ghi nhận không có rủi ro cận hạn hoặc hết hạn đối với nhóm danh mục đang chọn.")

    with tab5:
        st.subheader("🔍 Tra cứu chi tiết thông số & Đề xuất thông minh")
        selected_sku = st.selectbox("Gõ hoặc chọn Mã SKU cần kiểm tra:", df['SKU'].unique())
        
        if selected_sku:
            sku_data = df[df['SKU'] == selected_sku].iloc[0]
            
            st.markdown("### 📋 Thông tin danh mục sản phẩm")
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
            
            st.markdown("### 🧠 Đề xuất điều phối thông minh từ hệ thống")
            
            recommendations = []
            
            if sku_data['Trang_Thai'] == "🔴 ĐỨT HÀNG":
                recommendations.append(f"🚨 **CẢNH BÁO KHẨN CẤP:** Số lượng tồn kho hiện tại thấp hơn mức thời gian nhập hàng an toàn (Lead Time: {lead_time} ngày). Yêu cầu phòng mua hàng phát hành ngay đơn PO với số lượng **{sku_data['De_Xuat_Mua']:,.0f}** để tránh làm đứt gãy dịch vụ.")
            elif sku_data['Trang_Thai'] == "🟡 CẦN NHẬP":
                recommendations.append(f"⚠️ **KẾ HOẠCH NHẬP BỔ SUNG:** Mặt hàng đang nằm dưới điểm đặt hàng lại (ROP). Khuyến nghị bổ sung mua **{sku_data['De_Xuat_Mua']:,.0f}** sản phẩm trong đợt gom đơn tuần này để đảm bảo chỉ số DOI mục tiêu.")
            else:
                recommendations.append("🟢 **TỒN KHO AN TOÀN:** Mức trữ lượng hiện tại đủ cung ứng tốt trong chu kỳ vận hành đã thiết lập.")
                
            if sku_data['S2S_Months'] > 6:
                recommendations.append(f"📦 **RỦI RO ĐỌNG VỐN CAO:** Chỉ số Stock-to-Sales đạt {sku_data['S2S_Months']:.1f} tháng (vượt ngưỡng an toàn 6 tháng). Đề xuất rà soát lại tệp khách hàng, triển khai các chương trình giải phóng hàng tồn hoặc hạn chế nhập mới mã hàng này.")
            elif sku_data['S2S_Months'] < 1 and sku_data['Daily_Sales'] > 0:
                recommendations.append("🔥 **ÁP LỰC TIÊU THỤ LỚN:** Vòng quay kho quá nhanh dưới 1 tháng. Sức mua đang tăng mạnh, cần cân nhắc tăng DOI mục tiêu của mã này lên để tối ưu chi phí vận chuyển.")
                
            if sku_data['Het_HSD_Value'] > 0:
                recommendations.append(f"🚩 **RỦI RO HẠN SỬ DỤNG:** Mã SKU này đang gánh khoản thiệt hại cận/hết hạn dự kiến lên đến **{sku_data['Het_HSD_Value']:,.0f} ₫**. Đề xuất kho vận áp dụng nghiêm ngặt nguyên tắc FEFO (Hết hạn trước - Xuất trước).")

            for rec in recommendations:
                st.write(rec)

except Exception as e:
    st.error(f"Lỗi đồng bộ cấu trúc hiển thị: {e}")
