import sys
import os
import json
from dotenv import load_dotenv
from groq import Groq
from backend.data_fetcher import get_market_data
from backend.utils import parse_portfolio_csv

# Ensure local imports work correctly
sys.path.append(os.path.dirname(__file__))

load_dotenv()

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
    # 🔹 M1: Fetch Market Data
    market_data = get_market_data(ticker)

    # 🔹 M2: Build Prompt
    prompt = build_prompt(ticker, market_data, user_query, portfolio)

    try:
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
        )

        raw_output = chat_completion.choices[0].message.content.strip()

        # 🔥 Handle JSON formatting issues
        if "```json" in raw_output:
            raw_output = raw_output.split("```json")[1].split("```")[0].strip()

        result = json.loads(raw_output)

        # 🔥 Calculate ₹ impact
        impact = calculate_impact(ticker, market_data, portfolio)

        return {
            "insight": result.get("insight", ""),
            "reason": result.get("reason", ""),
            "risk": result.get("risk", ""),
            "impact": impact,
            "script": result.get("script", "")
        }

    except Exception as e:
        print(f"❌ AI_AGENT ERROR: {str(e)}")

        return {
            "insight": "Unable to analyze",
            "reason": "AI service error or invalid response",
            "risk": "Unknown",
            "impact": "₹0",
            "script": "Unable to generate briefing at this moment."
        }