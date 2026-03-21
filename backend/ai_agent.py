# ai_agent.py

from data_fetcher import get_market_data


def generate_advice(ticker, portfolio=None):
    data = get_market_data(ticker)

    price = data["price"]["change_percent"]
    signal = data["signals"][0]["action"]

    decision = "HOLD"
    reason = []
    risk = "Moderate"

    # 📊 Price logic
    if price > 1:
        decision = "BUY"
        reason.append("Positive price momentum")
    elif price < -1:
        decision = "SELL"
        reason.append("Negative trend detected")

    # 🏦 Signal logic
    if signal == "BUY":
        decision = "BUY"
        reason.append("Institutional buying observed")
    elif signal == "SELL":
        decision = "SELL"
        reason.append("Institutional selling observed")

    # 🧠 Portfolio awareness
    if portfolio and ticker.replace(".NS", "") in portfolio:
        reason.append("You already hold this stock")

    # ⚠️ Risk logic
    if abs(price) > 2:
        risk = "High"

    return {
        "stock": ticker,
        "decision": decision,
        "reason": ", ".join(reason),
        "risk": risk,
        "data": data
    }