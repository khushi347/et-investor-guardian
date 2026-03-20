# utils.py

import yfinance as yf

def get_stock_price(symbol):
    stock = yf.Ticker(symbol)
    data = stock.history(period="1d")
    return round(data["Close"].iloc[-1], 2)