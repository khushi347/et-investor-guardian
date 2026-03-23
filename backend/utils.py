# utils.py
import pandas as pd
from datetime import datetime


# 📅 Get current timestamp
def get_timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# 💰 Format currency nicely
def format_currency(value):
    try:
        return f"₹{round(value, 2)}"
    except:
        return "₹0"


# 📊 Determine price trend
def get_trend(change):
    if change > 0:
        return "UP 📈"
    elif change < 0:
        return "DOWN 📉"
    else:
        return "STABLE"


# 🎯 Confidence logic (important for AI + UI)
def get_confidence(alert_type):
    if alert_type == "bulk":
        return "High"
    elif alert_type == "price":
        return "Medium"
    else:
        return "Low"


# 🧠 Clean stock symbol (just in case)
def clean_symbol(symbol):
    if symbol:
        return symbol.upper().strip()
    return "UNKNOWN"


# 🔥 Generate simple ID
def generate_id(index):
    return index + 1

def parse_portfolio_csv(file_path):
    try:
        df = pd.read_csv(file_path)

        portfolio = {}

        for _, row in df.iterrows():
            stock = str(row["Stock"]).strip().upper()
            quantity = int(row["Quantity"])

            portfolio[stock] = quantity

        return portfolio

    except Exception as e:
        print("CSV Parsing Error:", e)
        return {}