import streamlit as st
import pandas as pd

# Cấu hình giao diện
st.set_page_config(page_title="Debug Data", layout="wide")

@st.cache_data(ttl=600)
def load_data_debug():
    sheet_id = st.secrets["spreadsheet_id"]
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=xlsx"
    
    # Đọc sheet Xuất bán để kiểm tra
    df_xuatban = pd.read_excel(url, sheet_name='Xuất bán') 
    return df_xuatban.columns.tolist()

# Hiển thị tên cột để debug
st.title("Kiểm tra cấu trúc file")
try:
    cols = load_data_debug()
    st.write("### Các cột đang có trong sheet 'Xuất bán' là:")
    st.write(cols)
    st.info("Hãy nhìn vào danh sách trên, tìm xem tên cột chứa mã hàng và tên cột chứa khách hàng viết chính xác là gì (bao gồm cả khoảng trắng).")
except Exception as e:
    st.error(f"Lỗi: {e}")
