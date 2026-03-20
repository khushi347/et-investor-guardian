# alerts.py

from datetime import datetime

# Step 1: Hardcoded alerts
alerts_data = [
    {
        "stock": "HDFC Bank",
        "event": "₹45 Cr block deal yesterday",
        "explanation": "Large investors traded shares in bulk, showing strong market activity."
    },
    {
        "stock": "Reliance",
        "event": "Promoter stake increased by 0.8%",
        "explanation": "Promoters increasing stake indicates confidence in future growth."
    },
    {
        "stock": "TCS",
        "event": "High institutional buying observed",
        "explanation": "Institutional buying suggests positive sentiment and long-term potential."
    }
]

# Step 2: Optional tag function
def get_tag(stock):
    if stock == "HDFC Bank":
        return "🏦"
    elif stock == "Reliance":
        return "⚡"
    elif stock == "TCS":
        return "💻"
    return "📊"

# Step 3: Main function (IMPORTANT)
def get_alerts():
    formatted_alerts = []

    for i, alert in enumerate(alerts_data):
        formatted_alerts.append({
            "id": i + 1,
            "stock": alert["stock"],
            "tag": get_tag(alert["stock"]),
            "event": alert["event"],
            "explanation": alert["explanation"],
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

    return formatted_alerts