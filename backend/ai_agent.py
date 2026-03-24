import sys
import os
import json
from dotenv import load_dotenv

# m2's fix for imports
sys.path.append(os.path.dirname(__file__))

load_dotenv()

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

- ALSO generate a SHORT voice script (max 30 words)
- Script should sound natural and conversational

Rules:
- Output STRICT JSON
- Only keys: insight, reason, risk, script
- No extra text

Example:
{{
  "insight": "Hold TCS",
  "reason": "You already hold TCS and signals are mixed",
  "risk": "Moderate due to portfolio exposure",
  "script": "Since you already hold TCS, avoid adding more. Mixed signals suggest caution and your exposure is already high."
}}
"""


# 🔥 ₹ IMPACT FUNCTION
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

    price_change = (change_percent / 100) * current_price
    impact = quantity * price_change

    if impact > 0:
        return f"+₹{int(impact)}"
    elif impact < 0:
        return f"-₹{abs(int(impact))}"
    else:
        return "₹0"


def generate_advice(ticker, user_query="Analyze this stock", portfolio=None):
    print("STEP 1: Fetching market data...")

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

        result = json.loads(raw_output)

        print("STEP 5: Parsed AI response")

        # 🔥 impact calculation
        impact = calculate_impact(ticker, market_data, portfolio)

        return {
            "insight": result.get("insight", ""),
            "reason": result.get("reason", ""),
            "risk": result.get("risk", ""),
            "impact": impact,
            "script": result.get("script", "")   # 🔥 NEW FIELD
        }

    except Exception as e:
        print("ERROR:", str(e))

        return {
            "insight": "Unable to analyze",
            "reason": "AI service error or invalid response",
            "risk": "Unknown",
            "impact": "₹0",
            "script": "Unable to generate briefing at this moment."
        }