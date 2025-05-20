import streamlit as st
import pandas as pd
from auth import check_login
from data_fetch import get_price_data, get_revenue_data
import matplotlib.pyplot as plt

if not check_login():
    st.stop()

st.title("6227 茂綸 - 智能買賣分析系統")

with st.spinner("取得資料中..."):
    price_df = get_price_data("6227")
    revenue_df = get_revenue_data("6227")

df = pd.merge(price_df, revenue_df, on="Date", how="inner")
df.set_index("Date", inplace=True)

df["MA5"] = df["Close"].rolling(5).mean()
df["MA20"] = df["Close"].rolling(20).mean()
df["MA60"] = df["Close"].rolling(60).mean()
df["STD20"] = df["Close"].rolling(20).std()
df["Upper"] = df["MA20"] + 2 * df["STD20"]
df["Lower"] = df["MA20"] - 2 * df["STD20"]

df["Buy"] = (
    (df["YoY"] > 30) &
    (df["MA5"] > df["MA20"]) &
    (df["MA5"].shift(1) <= df["MA20"].shift(1)) &
    (df["Close"] > df["MA60"]) &
    (df["Close"] > df["Upper"])
)

df["Sell"] = (
    ((df["MA5"] < df["MA20"]) & (df["MA5"].shift(1) >= df["MA20"].shift(1))) |
    (df["YoY"].rolling(2).mean() < 20) |
    (df["Close"] < df["MA60"]) |
    (df["Close"] < df["Lower"])
)

st.subheader("股價與技術指標")
fig, ax = plt.subplots(figsize=(14, 6))
ax.plot(df.index, df["Close"], label="收盤價")
ax.plot(df.index, df["MA5"], label="MA5")
ax.plot(df.index, df["MA20"], label="MA20")
ax.plot(df.index, df["MA60"], label="MA60")
ax.plot(df.index, df["Upper"], linestyle="--", alpha=0.5, label="布林上軌")
ax.plot(df.index, df["Lower"], linestyle="--", alpha=0.5, label="布林下軌")
ax.scatter(df[df["Buy"]].index, df[df["Buy"]]["Close"], marker="^", color="green", label="買進", s=100)
ax.scatter(df[df["Sell"]].index, df[df["Sell"]]["Close"], marker="v", color="red", label="賣出", s=100)
ax.legend()
st.pyplot(fig)

st.subheader("營收年增率 (YoY)")
st.line_chart(df["YoY"])

st.subheader("策略績效回測")
initial_cash = 1_000_000
cash = initial_cash
position = 0
portfolio = []

for i in range(len(df)):
    row = df.iloc[i]
    if row["Buy"] and cash > row["Close"]:
        position = cash // row["Close"]
        cash -= position * row["Close"]
    elif row["Sell"] and position > 0:
        cash += position * row["Close"]
        position = 0
    total = cash + position * row["Close"]
    portfolio.append(total)

df["Portfolio"] = portfolio
st.line_chart(df["Portfolio"])
total_return = (df["Portfolio"].iloc[-1] / initial_cash - 1) * 100
st.metric("總報酬率", f"{total_return:.2f}%")
