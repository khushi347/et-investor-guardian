import sys
import os
import json
from dotenv import load_dotenv

# m2's fix for imports
sys.path.append(os.path.dirname(__file__))

load_dotenv()

# m2's debug line (remove later)


from groq import Groq
from data_fetcher import get_market_data
from utils import parse_portfolio_csv

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def build_prompt(ticker, market_data, user_query, portfolio):
    return f"""
You are an expert AI financial advisor for the Indian stock market.

Stock: {ticker}

Market Data:
Price Info: {market_data.get("price")}
Signals: {market_data.get("signals")}
News: {market_data.get("news")}

User Portfolio:
{portfolio}

User Question:
{user_query}

Instructions:
- Be smart and context-aware
- If user already holds the stock → mention it
- Avoid suggesting over-allocation
- Use signals (bulk deals, price change, news)
- Keep answers short (1–2 lines max)

Rules:
- Output STRICT JSON
- Only keys: insight, reason, risk
- No extra text

Example:
{{
  "insight": "Hold TCS",
  "reason": "Since you already hold TCS, adding more may increase concentration risk",
  "risk": "Moderate due to overexposure"
}}
"""


# 🔥 NEW: ₹ IMPACT FUNCTION
def calculate_impact(ticker, market_data, portfolio):
    if not portfolio:
        return "₹0"

    stock = ticker.replace(".NS", "")

    if stock not in portfolio:
        return "₹0"

    quantity = portfolio[stock]

    price_data = market_data.get("price", {})
    current_price = price_data.get("current_price", 0)
    change_percent = price_data.get("change_percent", 0)

    # price movement in ₹
    price_change = (change_percent / 100) * current_price

    impact = quantity * price_change

    # format result
    if impact > 0:
        return f"+₹{int(impact)}"
    elif impact < 0:
        return f"-₹{abs(int(impact))}"
    else:
        return "₹0"


def generate_advice(ticker, user_query="Analyze this stock", portfolio=None):
    print("STEP 1: Fetching market data...")

    # 🔹 M1: Market Data
    market_data = get_market_data(ticker)

    print("STEP 2: Building AI prompt...")

    prompt = build_prompt(ticker, market_data, user_query, portfolio)

    print("STEP 3: Calling AI...")

    try:
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
        )

        raw_output = chat_completion.choices[0].message.content.strip()

        print("STEP 4: AI raw output:", raw_output)

        # 🔥 Convert AI → JSON
        result = json.loads(raw_output)

        print("STEP 5: Parsed AI response")

        # 🔥 NEW: Calculate impact
        impact = calculate_impact(ticker, market_data, portfolio)

        # 🔥 FINAL CLEAN OUTPUT
        return {
            "insight": result.get("insight", ""),
            "reason": result.get("reason", ""),
            "risk": result.get("risk", ""),
            "impact": impact
        }

    except Exception as e:
        print("ERROR:", str(e))

        return {
            "insight": "Unable to analyze",
            "reason": "AI service error or invalid response",
            "risk": "Unknown",
            "impact": "₹0"
        }