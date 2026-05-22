import streamlit as st
import pandas as pd
import plotly.express as px

# ==========================================
# 1. CẤU HÌNH GIAO DIỆN MODERN TECH & SHADOW UI
# ==========================================
st.set_page_config(page_title="SGM Supply Chain Intel", page_icon="⚡", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    /* Font Inter hiện đại từ Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }

    /* -----------------------------------
       TƯƠNG PHẢN NỀN TỔNG THỂ
       ----------------------------------- */
    /* Vùng Main (Trung tâm) màu xám xanh cực nhạt để làm nổi bật các thẻ trắng */
    .main { background-color: #f0f4f8 !important; }
    
    /* Vùng Sidebar (Menu) màu trắng tinh, tạo sự tách biệt hoàn toàn */
    [data-testid="stSidebar"] {
        background-color: #ffffff !important;
        border-right: 1px solid #e2e8f0 !important;
        box-shadow: 4px 0 24px rgba(0,0,0,0.04);
    }

    /* Chữ bản quyền */
    .copyright-text { font-size: 11px; color: #94a3b8; text-align: center; margin-top: -15px; margin-bottom: 25px; font-weight: 500; }

    /* -----------------------------------
       HIỆU ỨNG THẺ (CARD) SHADOW NỔI 3D
       ----------------------------------- */
    div[data-testid="stMetric"] {
        background-color: #ffffff !important;
        border-radius: 16px !important;
        padding: 24px !important;
        /* Shadow đậm, phân lớp rõ ràng */
        box-shadow: 0 10px 30px rgba(0,0,0,0.05), 0 4px 6px rgba(0,0,0,0.02) !important;
        border-left: 6px solid #388e3c !important; 
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    div[data-testid="stMetric"]:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 35px rgba(56,142,60,0.15), 0 5px 15px rgba(0,0,0,0.05) !important;
    }
    div[data-testid="stMetric"] label { font-weight: 800 !important; font-size: 14px !important; color: #475569 !important; text-transform: uppercase; letter-spacing: 0.5px;}
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] { color: #15803d !important; font-weight: 800 !important; font-size: 32px !important;}

    /* -----------------------------------
       GREEN PASTEL CHO SLIDER & BỘ LỌC
       ----------------------------------- */
    /* Màu thanh trượt */
    .stSlider div[data-baseweb="slider"] div[role="slider"] {
        background-color: #388e3c !important; border: 2px solid #ffffff; box-shadow: 0 2px 6px rgba(56,142,60,0.4);
    }
    .stSlider div[data-baseweb="slider"] > div > div > div:first-child { background-color: #81c784 !important; }
    
    /* Màu MultiSelect */
    .stMultiSelect span[data-baseweb="tag"] { background-color: #e8f5e9 !important; color: #2e7d32 !important; border: 1px solid #a5d6a7; font-weight: 600; }

    /* -----------------------------------
       TABS NỔI BẬT & NÚT BẤM (BUTTON)
       ----------------------------------- */
    button[data-baseweb="tab"] { 
        font-size: 16px !important; font-weight: 700 !important; color: #64748b !important;
        background: transparent; padding: 12px 24px; border-radius: 8px 8px 0 0;
    }
    button[aria-selected="true"] { 
        color: #2e7d32 !important; background-color: #ffffff !important;
        border-bottom: 3px solid #388e3c !important; 
        box-shadow: 0 -4px 15px rgba(0,0,0,0.03) !important;
    }
    
    .stDataFrame { border-radius: 12px; overflow: hidden; box-shadow: 0 8px 24px rgba(0,0,0,0.06); background: #ffffff; padding: 10px; }
    
    .stDownloadButton button { background-color: #388e3c !important; color: white !important; border-radius: 8px !important; font-weight: 700; border: none !important; box-shadow: 0 4px 10px rgba(56,142,60,0.25); }
    .stDownloadButton button:hover { background-color: #2e7d32 !important; transform: translateY(-2px); box-shadow: 0 6px 15px rgba(56,142,60,0.35); }
    
    /* Smart Cards */
    .smart-card-info { background-color: #ffffff; border-left: 5px solid #3b82f6; padding: 20px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); margin-bottom: 16px; }
    .smart-card-warning { background-color: #ffffff; border-left: 5px solid #f59e0b; padding: 20px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); margin-bottom: 16px; }
    .smart-card-error { background-color: #ffffff; border-left: 5px solid #ef4444; padding: 20px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); margin-bottom: 16px; }
    .smart-card-success { background-color: #ffffff; border-left: 5px solid #10b981; padding: 20px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); margin-bottom: 16px; }
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
    
    # --- C. HỢP NHẤT DỮ LIỆU ---
    df = pd.merge(df_th, active_kh, on='SKU', how='left').fillna(0)
    return df, customer_mapping

# ==========================================
# 3. GIAO DIỆN CHÍNH & THUẬT TOÁN ĐIỀU PHỐI
# ==========================================
try:
    df_full, customer_mapping = load_data()
    
    # --- SIDEBAR MENU VỚI ICON HIỆN ĐẠI ---
    st.sidebar.image("https://raw.githubusercontent.com/vic-techSGM/sgm-supplychain/main/logo.png", use_container_width=True)
    st.sidebar.markdown("<div class='copyright-text'>Build & Developed by Vic Fan.<br>Copyrights reserved. Version 01.26.05</div>", unsafe_allow_html=True)
    
    st.sidebar.markdown("<h4 style='color:#1e293b; font-weight:800; letter-spacing: 0.5px;'>⯁ CẤU HÌNH HỆ THỐNG</h4>", unsafe_allow_html=True)
    doi_target = st.sidebar.slider("Ngưỡng DOI (Ngày an toàn)", 15, 120, 45)
    lead_time = st.sidebar.slider("Lead Time (Thời gian nhập)", 10, 90, 30)
    customer_growth = st.sidebar.slider("Biên độ Tăng trưởng KH (%)", 0, 100, 15)
    
    st.sidebar.markdown("<h4 style='color:#1e293b; font-weight:800; margin-top:30px; letter-spacing: 0.5px;'>⯁ BỘ LỌC DỮ LIỆU</h4>", unsafe_allow_html=True)
    list_nganh = df_full['Nganh_Hang'].unique().tolist()
    selected_nganh = st.sidebar.multiselect("Ngành hàng phân phối", list_nganh, default=list_nganh)
    
    df_f1 = df_full[df_full['Nganh_Hang'].isin(selected_nganh)]
    list_chungloai = df_f1['Chung_Loai'].unique().tolist() if 'Chung_Loai' in df_f1.columns else []
    selected_chungloai = st.sidebar.multiselect("Chủng loại chi tiết", list_chungloai, default=list_chungloai) if list_chungloai else []
    
    df_f2 = df_f1[df_f1['Chung_Loai'].isin(selected_chungloai)] if selected_chungloai else df_f1
    list_hang = df_f2['Hang'].unique().tolist()
    selected_hang = st.sidebar.multiselect("Hãng sản xuất (NPP)", list_hang, default=list_hang)

    # Áp dụng bộ lọc cuối cùng
    df = df_f2[df_f2['Hang'].isin(selected_hang)].copy()
    
    # --- THUẬT TOÁN TÍNH TOÁN ROP VÀ S2S ---
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
    st.markdown("<h2 style='font-weight: 800; color: #0f172a; margin-bottom: 20px;'>🏥 SGM SUPPLY CHAIN INTEL</h2>", unsafe_allow_html=True)
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("TỔNG VỐN TỒN KHO", f"{df['Ton_Kho_Value'].sum():,.0f} ₫")
    m2.metric("MÃ SKU ĐANG LỌC", f"{len(df):,}")
    m3.metric("S2S BÌNH QUÂN", f"{avg_s2s_global:.1f} Tháng")
    m4.metric("KHÁCH HÀNG ACTIVE", f"{int(df['Khach_Hang_Active'].sum()):,}")

    # --- ĐIỀU HƯỚNG TABS ---
    st.markdown("<br>", unsafe_allow_html=True)
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "⚡ KẾ HOẠCH ĐẶT HÀNG", 
        "📊 PHÂN LOẠI BÁN CHẠY", 
        "👥 KHÁCH HÀNG THEO SKU", 
        "🚩 RỦI RO HẠN DÙNG",
        "💡 TRA CỨU ĐỀ XUẤT"
    ])

    with tab1:
        st.markdown("<h3 style='font-weight: 700; color: #1e293b;'>🛒 Danh sách Kế hoạch Dự trù Đặt hàng</h3>", unsafe_allow_html=True)
        
        display_df = df[['SKU', 'Hang', 'Ton_Kho_SL', 'Khach_Hang_Active', 'Du_Tru_Thang', 'Du_Tru_Quy', 'ROP', 'De_Xuat_Mua', 'Trang_Thai', 'Canh_Bao_S2S']].copy()
        display_df.columns = [
            'Mã SKU', 'Hãng', 'Số Lượng Tồn Kho', 'Khách Hàng Active', 
            'Dự Trù Trong Tháng', 'Dự Trù 3 Tháng (Quý)', 'ROP Dự Kiến', 'Số Lượng Cần Mua', 
            'Trạng Thái', 'Cảnh Báo S2S'
        ]
        st.dataframe(display_df.sort_values(by='Số Lượng Cần Mua', ascending=False), use_container_width=True, height=350)
        
        # Chú thích Logic ROP Thông minh
        st.markdown("""
        <div style="background: #f8fafc; padding: 12px 16px; border-radius: 8px; border-left: 4px solid #3b82f6; font-size: 14px; color: #475569; margin-bottom: 20px;">
            <b>ℹ️ TÍNH TOÁN ĐIỂM ĐẶT HÀNG (ROP):</b> Hệ thống tính toán ROP tự động dựa trên mức tiêu thụ trung bình, nhân với tỷ lệ <b>Tăng trưởng Khách hàng</b>. Hàng hoá sẽ chạm ROP và báo <b>"CẦN NHẬP"</b> khi Lượng tồn kho giảm xuống bằng tổng của Lượng hàng bán trong chu kỳ <b>Lead Time</b> cộng với Lượng hàng bảo lưu trong ngưỡng <b>DOI</b>.
        </div>
        """, unsafe_allow_html=True)
        
        # Chức năng xuất File tuỳ biến cột
        st.markdown("<h4 style='font-weight: 600; color: #1e293b; margin-top: 30px;'>📥 Xuất File Đơn Đặt Hàng (PO)</h4>", unsafe_allow_html=True)
        po_df = display_df[display_df['Số Lượng Cần Mua'] > 0].copy()
        
        if not po_df.empty:
            export_cols = st.multiselect("Chọn các trường dữ liệu cần thiết để xuất file PO:", options=po_df.columns.tolist(), default=po_df.columns.tolist())
            st.download_button(
                label="📥 TẢI XUỐNG FILE EXCEL/CSV (PO)", 
                data=po_df[export_cols].to_csv(index=False).encode('utf-8-sig'), 
                file_name='SGM_Purchase_Order_Custom.csv', mime='text/csv'
            )
        else:
            st.success("Không có mặt hàng nào cần đặt mua trong danh mục lọc hiện tại.")

    with tab2:
        st.markdown("<h3 style='font-weight: 700; color: #1e293b;'>🔥 Top 20 SKU Bán Chạy Nhất (Trục Đứng)</h3>", unsafe_allow_html=True)
        
        # Lấy top 20, sắp xếp giảm dần để bar cao nhất nằm bên trái
        top_sku = df.sort_values(by='Xuat_Ban_SL', ascending=False).head(20)
        
        # Biểu đồ CỘT DỌC, Trục X=SKU, Trục Y=Sản Lượng
        fig_bar = px.bar(
            top_sku, 
            x='SKU', 
            y='Xuat_Ban_SL', 
            color='Xuat_Ban_SL', 
            color_continuous_scale="Blues", # Màu xanh dương pastel đổ gradient
            text='Xuat_Ban_SL',
            labels={'Xuat_Ban_SL': 'Sản lượng xuất bán', 'SKU': 'Mã SKU'}
        )
        fig_bar.update_traces(
            texttemplate='%{text:,.0f}', 
            textposition='outside', 
            marker_line_width=0,
            marker=dict(cornerradius=8) # Bo cong thanh Bar
        )
        fig_bar.update_layout(
            coloraxis_showscale=False, 
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis_title="Mã SKU Hàng Hóa",
            yaxis_title="Tổng Sản Lượng Xuất Bán",
            height=550 
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with tab3:
        st.markdown("<h3 style='font-weight: 700; color: #1e293b;'>🔍 Phân bổ Khách hàng theo SKU (Bản đồ Nhiệt)</h3>", unsafe_allow_html=True)
        
        st.markdown("""
        <div class="smart-card-info">
            <b style="color:#1d4ed8; font-size: 15px;">💡 CÁCH ĐỌC BẢN ĐỒ NHIỆT (TREEMAP):</b><br>
            <span style="color:#334155; font-size: 14px; line-height: 1.6;">
            - <b>Kích thước Diện tích:</b> Biểu thị tỷ trọng Dòng tiền (Vốn Tồn Kho). Diện tích càng rộng, vốn đọng càng nhiều.<br>
            - <b>Quy ước Màu sắc:</b> <span style="color:#15803d; font-weight:700;">Xanh lá (Tồn kho hợp lý)</span> | <span style="color:#b45309; font-weight:700;">Cam (Nguy cơ thiếu hụt/Đứt gãy)</span> | <span style="color:#b91c1c; font-weight:700;">Đỏ tươi (Chậm luân chuyển, kẹt vốn dài hạn)</span>.
            </span>
        </div>
        """, unsafe_allow_html=True)

        list_kh = sorted(customer_mapping['Khach_Hang'].unique().tolist())
        selected_kh = st.multiselect("Gõ tên để tìm kiếm Khách Hàng (Hỗ trợ chọn nhiều):", list_kh)
        
        df_tab3 = df.copy()
        if selected_kh:
            skus_of_kh = customer_mapping[customer_mapping['Khach_Hang'].isin(selected_kh)]['SKU'].unique()
            df_tab3 = df[df['SKU'].isin(skus_of_kh)]
            
            tong_von_kh = df_tab3['Ton_Kho_Value'].sum()
            st.markdown(f"""
            <div class="smart-card-success">
                <b style="color:#047857; font-size: 15px;">📊 KẾT QUẢ ĐÁNH GIÁ TỆP KHÁCH HÀNG:</b><br>
                <span style="color:#334155; font-size: 14px;">
                Tệp khách hàng đang chọn tiêu thụ trực tiếp <b>{len(df_tab3)} mã SKU</b>, với tổng dòng vốn lưu trữ đang phân bổ là <b>{tong_von_kh:,.0f} ₫</b>. Hãy quan sát nhanh Bản đồ nhiệt bên dưới, nếu xuất hiện diện tích Đỏ lớn, chứng tỏ lượng hàng lưu kho phục vụ nhóm khách này đang trượt vòng quay vốn.
                </span>
            </div>
            """, unsafe_allow_html=True)
        
        if not df_tab3.empty and df_tab3['Ton_Kho_Value'].sum() > 0:
            fig_treemap = px.treemap(
                df_tab3[df_tab3['Ton_Kho_Value'] > 0],
                path=[px.Constant("CỤC DIỆN TỔN KHO"), 'Canh_Bao_S2S', 'Hang', 'SKU'],
                values='Ton_Kho_Value', color='Canh_Bao_S2S',
                color_discrete_map={"⚠️ Chậm luân chuyển": "#ef4444", "🔥 Rủi ro thiếu hàng": "#f59e0b", "✅ Hợp lý": "#10b981"}
            )
            fig_treemap.update_traces(root_color="#f8fafc")
            fig_treemap.update_layout(margin=dict(t=30, l=10, r=10, b=10))
            st.plotly_chart(fig_treemap, use_container_width=True)
        else:
            st.warning("Không có dữ liệu tồn kho hợp lệ để khởi tạo Bản đồ nhiệt cho tuỳ chọn này.")

    with tab4:
        st.markdown("<h3 style='font-weight: 700; color: #1e293b;'>🚩 Cảnh báo Hàng Cận/Hết Hạn (FEFO)</h3>", unsafe_allow_html=True)
        risk_df = df[df['Het_HSD_Value'] > 0].copy()
        total_risk = risk_df['Het_HSD_Value'].sum()
        
        st.metric(label="🚨 TỔNG GIÁ TRỊ THIỆT HẠI DỰ KIẾN", value=f"{total_risk:,.0f} ₫")
        
        if total_risk > 0:
            fig_risk = px.bar(
                risk_df, x='SKU', y='Het_HSD_Value', color='Hang', text='Het_HSD_Value',
                labels={'SKU': 'Mã SKU', 'Het_HSD_Value': 'Giá trị thiệt hại (₫)'},
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig_risk.update_traces(texttemplate='%{text:,.0f}', textposition='outside', marker_line_width=0, marker=dict(cornerradius=6))
            fig_risk.update_layout(plot_bgcolor='rgba(0,0,0,0)', xaxis_title="Mã SKU", yaxis_title="Tổng Giá trị mất đi (VNĐ)")
            st.plotly_chart(fig_risk, use_container_width=True)
            
            st.markdown("<h4 style='font-weight: 600; color: #334155; margin-top: 20px;'>📋 Bảng Kê Chi Tiết Thiệt Hại</h4>", unsafe_allow_html=True)
            risk_display = risk_df[['SKU', 'Hang', 'Ton_Kho_SL', 'Het_HSD_Value']].copy()
            risk_display.columns = ['Mã SKU', 'Hãng Cung Cấp', 'Số Lượng Tồn', 'Giá Trị Mất Đi (VNĐ)']
            st.dataframe(risk_display.sort_values(by='Giá Trị Mất Đi (VNĐ)', ascending=False), use_container_width=True)
        else:
            st.markdown("<div class='smart-card-success'><b style='color:#047857;'>✅ TRẠNG THÁI AN TOÀN:</b> Hệ thống ghi nhận không có rủi ro cận hạn hoặc hết hạn đối với nhóm danh mục đang chọn.</div>", unsafe_allow_html=True)

    with tab5:
        st.markdown("<h3 style='font-weight: 700; color: #1e293b;'>🔍 Tra cứu chi tiết & Đề xuất AI</h3>", unsafe_allow_html=True)
        selected_sku = st.selectbox("Gõ Mã SKU hoặc mở danh sách lựa chọn:", df['SKU'].unique())
        
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
            
            st.markdown("<h4 style='font-weight: 700; color: #1e293b; margin-top: 30px; margin-bottom: 20px;'>🧠 ENGINE ĐỀ XUẤT ĐIỀU PHỐI</h4>", unsafe_allow_html=True)
            
            if sku_data['Trang_Thai'] == "🔴 ĐỨT HÀNG":
                st.markdown(f"<div class='smart-card-error'><b style='color:#b91c1c; font-size: 15px;'>🚨 CẢNH BÁO KHẨN CẤP (ĐỨT HÀNG):</b><br><span style='color:#334155;'>Số lượng tồn kho hiện tại thấp hơn mức an toàn (Lead Time: {lead_time} ngày). Yêu cầu phòng mua hàng phát hành ngay đơn PO với số lượng <b>{sku_data['De_Xuat_Mua']:,.0f}</b> sản phẩm để bảo vệ chuỗi cung ứng.</span></div>", unsafe_allow_html=True)
            elif sku_data['Trang_Thai'] == "🟡 CẦN NHẬP":
                st.markdown(f"<div class='smart-card-warning'><b style='color:#b45309; font-size: 15px;'>⚠️ KẾ HOẠCH NHẬP BỔ SUNG:</b><br><span style='color:#334155;'>Mặt hàng đang nằm dưới điểm đặt hàng lại (ROP). Khuyến nghị bổ sung mua <b>{sku_data['De_Xuat_Mua']:,.0f}</b> sản phẩm trong đợt gom đơn tuần này.</span></div>", unsafe_allow_html=True)
            else:
                st.markdown("<div class='smart-card-success'><b style='color:#047857; font-size: 15px;'>🟢 TỒN KHO AN TOÀN:</b><br><span style='color:#334155;'>Mức trữ lượng hiện tại đáp ứng cực tốt chu kỳ vận hành đã thiết lập. Chưa cần can thiệp nhập thêm.</span></div>", unsafe_allow_html=True)
                
            if sku_data['S2S_Months'] > 6:
                st.markdown(f"<div class='smart-card-error'><b style='color:#b91c1c; font-size: 15px;'>📦 RỦI RO ĐỌNG VỐN LÂU DÀI:</b><br><span style='color:#334155;'>Chỉ số Stock-to-Sales đạt <b>{sku_data['S2S_Months']:.1f} tháng</b> (vượt ngưỡng 6 tháng). Đề xuất Sale rà soát tệp khách hàng, tổ chức xúc tiến bán hoặc ngưng kế hoạch nhập liệu mã này.</span></div>", unsafe_allow_html=True)
            elif sku_data['S2S_Months'] < 1 and sku_data['Daily_Sales'] > 0:
                st.markdown("<div class='smart-card-warning'><b style='color:#b45309; font-size: 15px;'>🔥 ÁP LỰC TIÊU THỤ LỚN:</b><br><span style='color:#334155;'>Vòng quay kho dưới 1 tháng. Sức mua đang tăng mạnh, cần cân nhắc nâng tồn kho mục tiêu (DOI) để tối ưu chi phí vận tải quốc tế.</span></div>", unsafe_allow_html=True)
                
            if sku_data['Het_HSD_Value'] > 0:
                st.markdown(f"<div class='smart-card-error'><b style='color:#b91c1c; font-size: 15px;'>🚩 BÁO ĐỘNG HẠN SỬ DỤNG:</b><br><span style='color:#334155;'>Mã SKU đang gánh khoản thiệt hại dự kiến <b>{sku_data['Het_HSD_Value']:,.0f} ₫</b>. Cần áp dụng ngay nguyên tắc xuất kho FEFO và đẩy mạnh xử lý hàng cận date.</span></div>", unsafe_allow_html=True)

except Exception as e:
    st.error(f"Lỗi hệ thống nội bộ: {e}")
