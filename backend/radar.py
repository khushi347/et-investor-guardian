# radar.py
from utils import clean_symbol, format_currency
from data_fetcher import get_stock_data, get_bulk_deals


def generate_radar_alerts():
    alerts = []

    stocks = ["TCS", "RELIANCE", "HDFCBANK"]

    # 📊 Price-based alerts
    for stock in stocks:
        data = get_stock_data(stock)

        if not data:
            continue

        if data["change"] > 10:
            alerts.append({
                "stock": stock,
                "event": "Price Surge",
                "explanation": f"{stock} jumped ₹{data['change']} today",
                "type": "price"
            })

    # 🏦 Bulk deal alerts
    deals = get_bulk_deals()

    for deal in deals:
        alerts.append({
            "stock": deal.get("symbol", "Unknown"),
            "event": "Bulk Deal Detected",
            "explanation": f"{deal.get('clientName', 'Investor')} made a large trade",
            "type": "bulk"
        })

    return alerts