# backend/radar.py

from .utils import clean_symbol, format_currency
from .data_fetcher import get_market_data


def generate_radar_alerts():
    """
    Scans the core watchbox and generates alerts based on 
    price volatility and institutional signals.
    """

    alerts = []

    # Core watchlist
    stocks = ["TCS", "RELIANCE", "HDFCBANK"]

    for ticker in stocks:
        data = get_market_data(ticker)

        # 📊 PRICE-BASED ALERTS
        price_info = data.get("price", {})
        change_val = price_info.get("change_percent", 0)

        if change_val > 2:
            alerts.append({
                "stock": ticker,
                "event": "High Momentum Breakout 🚀",
                "explanation": "Stock is showing strong upward momentum with significant price movement.",
                "type": "price"
            })

        elif change_val < -2:
            alerts.append({
                "stock": ticker,
                "event": "Bearish Breakdown 📉",
                "explanation": "Stock is falling sharply, selling pressure high",
                "type": "price"
            })

        elif abs(change_val) > 1.5:
            direction = "Surge" if change_val > 0 else "Drop"
            alerts.append({
                "stock": ticker,
                "event": f"Price {direction}",
                "explanation": f"{ticker} moved {change_val}% in the last session.",
                "type": "price"
            })

        # 🏦 INSTITUTIONAL / BULK DEAL ALERTS
        signals = data.get("signals", [])

        for signal in signals:
            action = signal.get("action", "").upper()

            if signal.get("type") == "bulk_deal":
                client = signal.get("client", "Institutional Investor")
                qty = signal.get("quantity", 0)

                alerts.append({
                    "stock": ticker,
                    "event": "Bulk Deal Detected",
                    "explanation": f"{client} executed a {action} order of {qty:,} shares.",
                    "type": "bulk"
                })

            elif action == "BUY":
                alerts.append({
                    "stock": ticker,
                    "event": "Strong Institutional Buying 💰",
                    "explanation": "Large investors accumulating shares",
                    "type": "institutional"
                })

            elif action == "SELL":
                alerts.append({
                    "stock": ticker,
                    "event": "Institutional Selling Pressure ⚠️",
                    "explanation": "Big players reducing positions",
                    "type": "institutional"
                })

        # 🧠 DEFAULT ALERT (per stock)
        if not any(alert["stock"] == ticker for alert in alerts):
            alerts.append({
                "stock": ticker,
                "event": "Stable Movement",
                "explanation": "No major unusual activity detected",
                "type": "default"
            })

    return alerts