import streamlit as st
from auth import check_password
from data_fetch import get_price_data
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="6227 茂綸預測模型", layout="wide")

if not check_password():
    st.stop()

st.title("📈 6227 茂綸 - 技術指標與簡易預測模型")

try:
    price_df = get_price_data("6227")
    st.write("📄 資料預覽", price_df.head())
    if 'close' not in price_df.columns:
        st.error("❌ 資料缺少 'close' 欄位，請檢查 data_fetch.py 的欄位命名。")
        st.stop()
except Exception as e:
    st.error(f"讀取股價資料失敗：{e}")
    st.stop()

# 確保日期格式正確
price_df['date'] = pd.to_datetime(price_df['date'], errors='coerce')

# 計算布林通道
price_df['MA20'] = price_df['close'].rolling(window=20).mean()
price_df['Upper'] = price_df['MA20'] + 2 * price_df['close'].rolling(window=20).std()
price_df['Lower'] = price_df['MA20'] - 2 * price_df['close'].rolling(window=20).std()

# 過濾掉任何包含 NaN 或日期無效的列
plot_df = price_df.dropna(subset=['date', 'close', 'MA20', 'Upper', 'Lower'])

st.subheader("股價與布林通道")
fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(plot_df['date'], plot_df['close'], label='收盤價')
ax.plot(plot_df['date'], plot_df['MA20'], label='MA20')
ax.fill_between(plot_df['date'], plot_df['Upper'], plot_df['Lower'],
                color='gray', alpha=0.3, label='布林通道')
ax.legend()
st.pyplot(fig)
