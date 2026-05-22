import streamlit as st
import pandas as pd

st.set_page_config(page_title="Check Columns", layout="wide")

sheet_id = st.secrets["spreadsheet_id"]
url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=xlsx"

# Thử đọc file
try:
    df_tonghop = pd.read_excel(url, sheet_name='Tổng hợp', header=1)
    st.success("Đã đọc được file! Dưới đây là danh sách tên cột chính xác trong file của bạn:")
    st.write(df_tonghop.columns.tolist()) # Dòng này sẽ in ra danh sách cột
except Exception as e:
    st.error(f"Lỗi: {e}")
