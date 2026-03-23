
from groq import Groq
from backend.data_fetcher import get_market_data
from backend.utils import parse_portfolio_csv   # ✅ FIXED IMPORT

# Load env
from dotenv import load_dotenv
import os

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def generate_advice(ticker, user_query, portfolio_path="portfolio.csv"):
    """
    Combines:
    - M1: Market data
    - M2: AI reasoning
    - M4: Portfolio + Risk logic
    """

    # 🔹 Load portfolio
    portfolio = parse_portfolio_csv(portfolio_path)

    # 🔹 Fetch market data
    market_data = get_market_data(ticker)

    price = market_data["price"]["current_price"]
    change = market_data["price"]["change_percent"]

    signal = market_data["signals"][0]["action"] if market_data["signals"] else "HOLD"

    reason = []
    decision = "HOLD"
    risk = "Moderate"

    # 🔹 Signal Logic
    if signal == "BUY":
        decision = "BUY"
        reason.append("Institutional buying observed")
    elif signal == "SELL":
        decision = "SELL"
        reason.append("Institutional selling observed")

    # 🔹 Portfolio Logic
    stock_name = ticker.replace(".NS", "")
    if stock_name in portfolio:
        reason.append("You already hold this stock")

    # 🔹 Risk Logic
    if abs(change) > 2:
        risk = "High"

    # 🔹 AI Prompt
    prompt = f"""
You are a smart financial assistant.

Stock: {ticker}
Price: {price}
Change: {change}%

User Portfolio: {portfolio}

User Question:
{user_query}

Give a short, clear explanation whether to BUY, SELL, or HOLD.
"""

    # 🔹 AI Response
    try:
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama3-8b-8192",
        )

        ai_response = chat_completion.choices[0].message.content.strip()
        reason.append(ai_response)

    except Exception as e:
        reason.append("AI analysis unavailable")

    # 🔹 Final Output
    return {
        "stock": ticker,
        "decision": decision,
        "reason": ", ".join(reason),
        "risk": risk,
        "data": market_data
    }