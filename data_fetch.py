import pandas as pd
import requests
from datetime import datetime
import io

def get_price_data(stock_id: str):
    url = f"https://www.twse.com.tw/exchangeReport/STOCK_DAY?response=csv&date=20240201&stockNo={stock_id}"
    response = requests.get(url)
    data = response.text
    lines = [line for line in data.split("\n") if len(line.split(",")) >= 7]
    csv_data = "\n".join(lines)
    df = pd.read_csv(io.StringIO(csv_data))
    df["Date"] = pd.to_datetime(df["日期"].str.replace("/", "-"))
    df["Close"] = pd.to_numeric(df["收盤價"].astype(str).str.replace(",", ""), errors="coerce")
    return df[["Date", "Close"]].dropna()

def get_revenue_data(stock_id: str):
    url = f"https://goodinfo.tw/tw/ShowSaleMonChart.asp?STOCK_ID={stock_id}"
    headers = {"User-Agent": "Mozilla/5.0"}
    df = pd.read_html(requests.get(url, headers=headers).text)[0]
    df.columns = df.columns.get_level_values(0)
    df = df.rename(columns={"月份": "Date", "年增率(%)": "YoY"})
    df = df[["Date", "YoY"]]
    df = df.dropna()
    df["Date"] = pd.to_datetime(df["Date"], format="%Y/%m")
    df["YoY"] = pd.to_numeric(df["YoY"].astype(str).str.replace("%", ""), errors="coerce")
    return df.dropna()
