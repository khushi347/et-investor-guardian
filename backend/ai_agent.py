import os
from dotenv import load_dotenv

# 🔥 FORCE LOAD .env FROM ROOT
load_dotenv(dotenv_path=os.path.join(os.getcwd(), ".env"))

from groq import Groq
from .data_fetcher import get_market_data

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def generate_advice(ticker, user_query="Analyze this stock for me", portfolio=None):
    """
    Combines:
    - M1: Market data
    - M2: AI reasoning
    - M4: Signal + Portfolio + Risk logic
    """

    # 🔹 1. Fetch market data (M1)
    market_data = get_market_data(ticker)

    price = market_data.get("price", 0)
    change = market_data.get("change_percent", 0)
    signal = market_data.get("signal", "HOLD")

    reason = []
    decision = "HOLD"
    risk = "Moderate"

    # 🔹 2. Signal Logic (YOUR LOGIC)
    if signal == "BUY":
        decision = "BUY"
        reason.append("Institutional buying observed")
    elif signal == "SELL":
        decision = "SELL"
        reason.append("Institutional selling observed")

    # 🔹 3. Portfolio Awareness (YOUR LOGIC)
    if portfolio and ticker.replace(".NS", "") in portfolio:
        reason.append("You already hold this stock")

    # 🔹 4. Risk Logic (YOUR LOGIC)
    if abs(change) > 2:
        risk = "High"

    # 🔹 5. AI Prompt (M2 LOGIC)
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

    # 🔹 6. AI Response (M2)
    try:
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama3-8b-8192",
        )

        ai_response = chat_completion.choices[0].message.content.strip()
        reason.append(ai_response)

    except Exception as e:
        reason.append("AI analysis unavailable")

    # 🔹 7. Final Output
    return {
        "stock": ticker,
        "decision": decision,
        "reason": ", ".join(reason),
        "risk": risk,
        "data": market_data
    }