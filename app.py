import streamlit as st
import pandas as pd
import plotly.express as px

# Cấu hình giao diện WebApp trải rộng
st.set_page_config(page_title="SGM Supply Chain Pro", layout="wide", initial_sidebar_state="expanded")
st.title("HỆ THỐNG QUẢN TRỊ KHO & CUNG ỨNG - SAIGONMED")

@st.cache_data(ttl=600) # Tự động xóa bộ nhớ đệm sau mỗi 10 phút để tải số liệu mới từ Google Sheets
def load_data():
    # KỸ THUẬT KẾT NỐI ONLINE BẢO MẬT: Lấy ID từ hệ thống quản lý mã khóa của Streamlit Cloud
    try:
        sheet_id = st.secrets["spreadsheet_id"]
    except:
        # Dự phòng chạy dưới máy cá nhân (Local) nếu chưa cấu hình mã khóa Cloud
        sheet_id = "1fmf68LVDT2KzR2IYs0nl2VlEVSvHqZ2h2ER8sNcgO2E"
        
    url = f"https://docs.google.com/spreadsheets/d/1fmf68LVDT2KzR2IYs0nl2VlEVSvHqZ2h2ER8sNcgO2E/export?format=xlsx"
    df = pd.read_excel(url, sheet_name='Tổng hợp', header=1)
    
    # Định vị cấu trúc tiêu đề kép nâng cao
    new_cols = list(df.columns)
    new_cols[1] = 'Nganh_Hang'
    new_cols[2] = 'Chung_Loai'
    new_cols[3] = 'Hang'
    new_cols[4] = 'SKU'
    new_cols[10] = 'Xuat_Ban_SL'     
    new_cols[11] = 'Xuat_Ban_Value'  
    new_cols[14] = 'Ton_Kho_SL'      
    new_cols[15] = 'Ton_Kho_Value'   
    new_cols[16] = 'Het_HSD_SL'      
    new_cols[17] = 'Het_HSD_Value'   
    
    df.columns = new_cols
    df = df.loc[:, ~df.columns.duplicated()] 
    df = df.iloc[1:]
    df = df.dropna(subset=['SKU', 'Nganh_Hang'])
    
    for col in ['Ton_Kho_SL', 'Ton_Kho_Value', 'Xuat_Ban_SL', 'Xuat_Ban_Value', 'Het_HSD_SL', 'Het_HSD_Value']:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
    return df

df = load_data()

# ================= SIDEBAR & BỘ THAM SỐ TÙY CHỈNH =================
st.sidebar.header("Bộ Tham Số Dự Trù")
ty_le_tang_truong_quy = st.sidebar.slider("Kỳ vọng tăng trưởng Khách hàng theo Quý (%)", 0, 100, 15, 1)

st.sidebar.header("Bộ Lọc Dữ Liệu")
selected_nganh = st.sidebar.multiselect("Ngành Hàng", df['Nganh_Hang'].unique(), default=df['Nganh_Hang'].unique())
selected_loai = st.sidebar.multiselect("Chủng Loại", df['Chung_Loai'].unique(), default=df['Chung_Loai'].unique())
selected_hang = st.sidebar.multiselect("Hãng", df['Hang'].unique())

filtered_df = df[
    (df['Nganh_Hang'].isin(selected_nganh)) & 
    (df['Chung_Loai'].isin(selected_loai))
]
if selected_hang:
    filtered_df = filtered_df[filtered_df['Hang'].isin(selected_hang)]

# ================= CHIA GIAO DIỆN THÀNH 4 TABS =================
tab1, tab2, tab3, tab4 = st.tabs([
    "🛒 1. Dự Trù & Đặt Hàng", 
    "🏆 2. Phân Tích Lợi Nhuận Theo SKU", 
    "⚠️ 3. Quản Trị Hàng Cận/Hết Date", 
    "🔍 4. Chi Tiết Theo SKU"
])

# ================= TAB 1: DỰ TRÙ & XUẤT BÁO CÁO =================
with tab1:
    st.subheader("Tổng Quan Giá Trị Phân Bổ Tồn Kho")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Tổng SKU Đang Quản Lý", len(filtered_df))
    col2.metric("Tổng Giá Trị Tồn Kho (VND)", f"{filtered_df['Ton_Kho_Value'].sum():,.0f}")
    
    stock_to_sell = filtered_df['Ton_Kho_SL'].sum() / (filtered_df['Xuat_Ban_SL'].sum() + 0.0001)
    
    if stock_to_sell < 1.0:
        sts_status = "🔴 Đứt hàng (Nguy hiểm)"
    elif 1.0 <= stock_to_sell <= 2.5:
        sts_status = "🟢 Hợp lý (An toàn)"
    else:
        sts_status = "🟡 Ứ đọng vốn (Nguy hiểm)"
        
    col3.metric(
        "Tỉ Lệ Stock-to-Sell (Bình quân)", 
        f"{stock_to_sell:.1f} tháng",
        delta=sts_status,
        delta_color="off"
    )
    
    c1, c2 = st.columns(2)
    with c1:
        fig_nganh = px.pie(filtered_df, values='Ton_Kho_SL', names='Nganh_Hang', title="Cơ Cấu Tồn Kho Theo Ngành Hàng")
        st.plotly_chart(fig_nganh, use_container_width=True)
    with c2:
        hang_df = filtered_df.groupby('Hang')['Ton_Kho_Value'].sum().reset_index()
        fig_hang = px.bar(hang_df, x='Hang', y='Ton_Kho_Value', title="Giá Trị Tồn Kho Phân Bổ Theo Hãng", text_auto='.2s')
        st.plotly_chart(fig_hang, use_container_width=True)

    st.divider()

    st.subheader("Dự Trù Mua Hàng")
    
    SO_THANG_LICH_SU = 5  
    MOM_GROWTH_RATE = 1.15 
    
    forecast_df = filtered_df[['SKU', 'Hang', 'Ton_Kho_SL', 'Xuat_Ban_SL']].copy()
    forecast_df['Trung_Binh_Thang'] = forecast_df['Xuat_Ban_SL'] / SO_THANG_LICH_SU
    forecast_df['Nhu_Cau_Thang_Toi'] = forecast_df['Trung_Binh_Thang'] * MOM_GROWTH_RATE
    forecast_df['Nhu_Cau_Quy'] = forecast_df['Trung_Binh_Thang'] * 3 * (1 + ty_le_tang_truong_quy / 100)
    
    forecast_df['De_Xuat_Mua_Them_Quy'] = forecast_df['Nhu_Cau_Quy'] - forecast_df['Ton_Kho_SL']
    forecast_df['De_Xuat_Mua_Them_Quy'] = forecast_df['De_Xuat_Mua_Them_Quy'].apply(lambda x: max(int(x), 0))
    forecast_df['Trang_Thai'] = forecast_df.apply(
        lambda x: "🔴 ĐẶT HÀNG GẤP" if x['Ton_Kho_SL'] < x['Nhu_Cau_Quy'] else "🟢 TỒN KHO AN TOÀN", axis=1
    )
    
    display_cols = ['SKU', 'Hang', 'Ton_Kho_SL', 'Trung_Binh_Thang', 'Nhu_Cau_Thang_Toi', 'Nhu_Cau_Quy', 'De_Xuat_Mua_Them_Quy', 'Trang_Thai']
    display_df = forecast_df[display_cols].sort_values(by='De_Xuat_Mua_Them_Quy', ascending=False).reset_index(drop=True)
    display_df.columns = ['Mã Hàng (SKU)', 'Hãng', 'Tồn Kho Hiện Tại', 'Trung Bình Xuất/Tháng', 'Nhu Cầu Tháng Tới', 'Nhu Cầu Quý', 'Đề Xuất Mua Thêm', 'Trạng Thái']
    
    csv = display_df.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="📥 Xuất File Đề Xuất Số Lượng Mua Hàng",
        data=csv,
        file_name='Danh_Sach_Dat_Hang_SGM.csv',
        mime='text/csv',
    )
    st.dataframe(display_df, use_container_width=True)

# ================= TAB 2: PHÂN TÍCH LỢI NHUẬN / TOP PERFORMERS =================
with tab2:
    st.subheader("Nhóm Hàng Chủ Lực")
    
    # Bẻ nhỏ dòng text để chống lỗi SyntaxError trên TextEdit
    st.write(
        "Nhận diện các mặt hàng mang lại dòng tiền lớn nhất, "
        "tập trung nguồn vốn đảm bảo lộ trình thanh toán."
    )
    
    pareto_df = filtered_df.groupby(['SKU', 'Hang'])['Xuat_Ban_Value'].sum().reset_index()
    pareto_df = pareto_df.sort_values(by='Xuat_Ban_Value', ascending=False).head(20) 
    
    fig_pareto = px.bar(
        pareto_df, x='SKU', y='Xuat_Ban_Value', color='Hang',
        title="Top 20 SKU Có Giá Trị Xuất Bán (Doanh Thu) Cao Nhất",
        text_auto='.2s', labels={'Xuat_Ban_Value': 'Giá trị xuất bán (VND)'}
    )
    st.plotly_chart(fig_pareto, use_container_width=True)
    
    st.info(
        "💡 Lời khuyên: Đảm bảo tồn kho an toàn tuyệt đối cho các SKU nằm trong biểu đồ này. "
        "Hết hàng nhóm này sẽ gây đứt gãy dòng tiền nghiêm trọng."
    )

# ================= TAB 3: QUẢN TRỊ HÀNG CẬN/HẾT DATE =================
with tab3:
    st.subheader("Cảnh Báo Hàng Hóa Hết HSD")
    
    risk_df = filtered_df[filtered_df['Het_HSD_SL'] > 0].copy()
    total_loss = risk_df['Het_HSD_Value'].sum()
    
    st.metric("Tổng Giá Trị Khấu Hao Do Hết Date", f"{total_loss:,.0f} VND", delta="- Thiệt hại", delta_color="inverse")
    
    if not risk_df.empty:
        st.error(
            "Danh sách các mặt hàng đã ghi nhận quá HSD. Cần cân nhắc lại Safety Stock "
            "và thuật toán nhập hàng của các SKU này để tránh tồn đọng lãng phí."
        )
        risk_display = risk_df[['SKU', 'Hang', 'Het_HSD_SL', 'Het_HSD_Value']].sort_values(by='Het_HSD_Value', ascending=False).reset_index(drop=True)
        risk_display.columns = ['Mã Hàng', 'Hãng', 'Số Lượng Hết Date', 'Giá Trị Mất Đi (VND)']
        
        styled_risk = risk_display.style.format({
            "Giá Trị Mất Đi (VND)": "{:,.0f}"
        })
        
        st.dataframe(styled_risk, use_container_width=True)
    else:
        st.success("Tuyệt vời! Hiện tại hệ thống không ghi nhận mặt hàng nào bị hết Date trong kho.")

# ================= TAB 4: Chi Tiết Theo SKU =================
with tab4:
    st.subheader("Tìm kiếm thông tin Xuất/Nhập/Tồn theo SKU")
    
    selected_sku = st.selectbox("Gõ hoặc chọn Mã Hàng (SKU) cần kiểm tra:", filtered_df['SKU'].unique())
    
    if selected_sku:
        sku_data = filtered_df[filtered_df['SKU'] == selected_sku].iloc[0]
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Tồn Kho Thực Tế", f"{sku_data['Ton_Kho_SL']:,.2f}")
        c2.metric("Tổng Xuất Bán (Lũy kế)", f"{sku_data['Xuat_Ban_SL']:,.2f}")
        c3.metric("Lượng Đã Hết Date", f"{sku_data['Het_HSD_SL']:,.2f}")
        c4.metric("Giá Trị Đang Nằm Kho", f"{sku_data['Ton_Kho_Value']:,.0f} VND")
        
        st.write("---")
        st.write(
            f"**Ngành hàng:** {sku_data['Nganh_Hang']} | "
            f"**Chủng loại:** {sku_data['Chung_Loai']} | "
            f"**Hãng cung cấp:** {sku_data['Hang']}"
        )
        
        st.warning(
            "💡 Khuyến nghị kiểm kê thực tế cuối mỗi ngày."
        )