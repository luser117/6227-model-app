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

price_df['date'] = pd.to_datetime(price_df['date'], errors='coerce')

# 計算布林通道
price_df['MA20'] = price_df['close'].rolling(window=20).mean()
price_df['Upper'] = price_df['MA20'] + 2 * price_df['close'].rolling(window=20).std()
price_df['Lower'] = price_df['MA20'] - 2 * price_df['close'].rolling(window=20).std()

plot_df = price_df.dropna(subset=['date', 'close', 'MA20', 'Upper', 'Lower'])

st.subheader("股價與布林通道")
fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(plot_df['date'], plot_df['close'], label='收盤價')
ax.plot(plot_df['date'], plot_df['MA20'], label='MA20')
ax.fill_between(plot_df['date'], plot_df['Upper'], plot_df['Lower'],
                color='gray', alpha=0.3, label='布林通道')
ax.legend()
st.pyplot(fig)


# 產生買賣訊號（布林通道策略）
plot_df['Signal'] = 0
plot_df.loc[plot_df['close'] < plot_df['Lower'], 'Signal'] = 1  # 買進訊號
plot_df.loc[plot_df['close'] > plot_df['Upper'], 'Signal'] = -1  # 賣出訊號

# 回測策略績效
capital = 1000000
position = 0
cash = capital
buy_price = 0
trade_log = []

for i in range(1, len(plot_df)):
    today = plot_df.iloc[i]
    yesterday = plot_df.iloc[i - 1]

    if today['Signal'] == 1 and position == 0:
        # 買進
        position = cash // today['close']
        buy_price = today['close']
        cash -= position * buy_price
        trade_log.append(('Buy', today['date'], today['close']))

    elif today['Signal'] == -1 and position > 0:
        # 賣出
        cash += position * today['close']
        trade_log.append(('Sell', today['date'], today['close']))
        position = 0

final_value = cash + (position * plot_df.iloc[-1]['close'])
total_return = (final_value - capital) / capital
days = (plot_df.iloc[-1]['date'] - plot_df.iloc[0]['date']).days
annualized_return = (1 + total_return) ** (365 / days) - 1 if days > 0 else 0

# 勝率計算
wins = 0
trades = 0
for i in range(1, len(trade_log), 2):
    if i < len(trade_log):
        buy_price = trade_log[i - 1][2]
        sell_price = trade_log[i][2]
        if sell_price > buy_price:
            wins += 1
        trades += 1

win_rate = wins / trades if trades > 0 else 0

# 顯示績效
st.subheader("📊 回測績效指標")
col1, col2, col3, col4 = st.columns(4)
col1.metric("總報酬率", f"{total_return*100:.2f}%")
col2.metric("年化報酬率", f"{annualized_return*100:.2f}%")
col3.metric("勝率", f"{win_rate*100:.2f}%")
col4.metric("交易次數", f"{trades}")

# 畫出買賣訊號
for idx, row in plot_df.iterrows():
    if row['Signal'] == 1:
        ax.plot(row['date'], row['close'], '^', color='green', markersize=10)
    elif row['Signal'] == -1:
        ax.plot(row['date'], row['close'], 'v', color='red', markersize=10)

st.pyplot(fig)
