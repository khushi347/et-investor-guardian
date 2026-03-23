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


#  Clean stock symbol 
def clean_symbol(symbol):
    if symbol:
        return symbol.upper().strip()
    return "UNKNOWN"


# Generate simple ID
def generate_id(index):
    return index + 1

def parse_portfolio_csv(file):
    import pandas as pd

    try:
        if file.name.endswith('.csv'):
            df = pd.read_csv(file)
        else:
            df = pd.read_excel(file)

        print("RAW:", df.head())

        # 🔥 Strong cleaning
        df.columns = (
            df.columns
            .str.strip()
            .str.lower()
            .str.replace(r'[^a-z0-9 ]', '', regex=True)
        )

        print("CLEANED COLUMNS:", df.columns.tolist())

        ticker_col = None
        qty_col = None

        for col in df.columns:
            if 'tick' in col or 'symbol' in col or 'stock' in col:
                ticker_col = col
            if 'qty' in col or 'hold' in col or 'quantity' in col:
                qty_col = col

        print("DETECTED:", ticker_col, qty_col)

        if ticker_col is None or qty_col is None:
            return {}

        portfolio = {}

        for _, row in df.iterrows():
            symbol = str(row[ticker_col]).strip().upper()

            if symbol and symbol.lower() not in ['nan', 'none', '']:
                try:
                    qty = int(float(row[qty_col]))
                except:
                    qty = 0

                portfolio[symbol] = qty

        print("FINAL PORTFOLIO:", portfolio)

        return portfolio

    except Exception as e:
        print("Parser Error:", e)
        return {}