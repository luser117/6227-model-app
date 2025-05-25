import twstock
import pandas as pd

def get_price_data(stock_id: str):
    stock = twstock.Stock(stock_id)
    data = stock.fetch_from(2024, 2)
    if not data:
        return pd.DataFrame(columns=['date', 'open', 'high', 'low', 'close', 'volume'])
    df = pd.DataFrame([{
        'date': d.date,
        'open': d.open,
        'high': d.high,
        'low': d.low,
        'close': d.close,
        'volume': d.capacity
    } for d in data])
    return df
