# radar.py
from utils import clean_symbol, format_currency
from data_fetcher import get_market_data


def generate_radar_alerts(ticker="TCS.NS"):
    data = get_market_data(ticker)

    alerts = []

    price_change = data["price"]["change_percent"]
    signal = data["signals"][0]["action"]

    # 📊 PRICE-BASED ALERTS
    if price_change > 2:
        alerts.append({
            "stock": ticker,
            "event": "High Momentum Breakout 🚀",
            "explanation": "Stock is rising तेजी से with strong upward momentum"
        })

    elif price_change < -2:
        alerts.append({
            "stock": ticker,
            "event": "Bearish Breakdown 📉",
            "explanation": "Stock is falling sharply, selling pressure high"
        })

    # 🏦 INSTITUTIONAL ALERTS
    if signal == "BUY":
        alerts.append({
            "stock": ticker,
            "event": "Strong Institutional Buying 💰",
            "explanation": "Large investors accumulating shares"
        })

    elif signal == "SELL":
        alerts.append({
            "stock": ticker,
            "event": "Institutional Selling Pressure ⚠️",
            "explanation": "Big players reducing positions"
        })

    # 🧠 DEFAULT ALERT
    if not alerts:
        alerts.append({
            "stock": ticker,
            "event": "Stable Movement",
            "explanation": "No major unusual activity detected"
        })

    return alerts