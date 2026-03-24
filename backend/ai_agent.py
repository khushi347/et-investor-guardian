import sys
import os
import json
from dotenv import load_dotenv
from groq import Groq
from data_fetcher import get_market_data
from utils import parse_portfolio_csv

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

# 🔥 ₹ IMPACT FUNCTION: Calculates potential gains/losses based on portfolio holdings
def calculate_impact(ticker, market_data, portfolio):
    if not portfolio:
        return "₹0"

    # Clean ticker for matching (e.g., RELIANCE.NS -> RELIANCE)
    stock = ticker.replace(".NS", "")

    if stock not in portfolio:
        return "₹0"

    quantity = portfolio[stock]

    price_data = market_data.get("price", {})
    current_price = price_data.get("current_price", 0)
    change_percent = price_data.get("change_percent", 0)

    # Calculate price movement in ₹
    price_change = (change_percent / 100) * current_price
    impact = quantity * price_change

    # Format result for UI
    if impact > 0:
        return f"+₹{int(impact)}"
    elif impact < 0:
        return f"-₹{abs(int(impact))}"
    else:
        return "₹0"

def generate_advice(ticker, user_query="Analyze this stock", portfolio=None):
    """
    Main entry point: Fetches market data, gets AI insight, and calculates portfolio impact.
    """
    # 🔹 M1: Fetch real-time Market Data
    market_data = get_market_data(ticker)

    # 🔹 M2: Build optimized prompt
    prompt = build_prompt(ticker, market_data, user_query, portfolio)

    try:
        # Request completion from Groq (Llama 3.3 70B)
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
        )

        raw_output = chat_completion.choices[0].message.content.strip()

        # 🔥 Step 1: Convert AI text output to JSON
        # Some models might wrap JSON in backticks, so we strip them if necessary
        if "```json" in raw_output:
            raw_output = raw_output.split("```json")[1].split("```")[0].strip()
        
        result = json.loads(raw_output)

        # 🔥 Step 2: Calculate financial impact
        impact = calculate_impact(ticker, market_data, portfolio)

        # 🔥 Step 3: Return final cleaned object
        return {
            "insight": result.get("insight", "No insight provided"),
            "reason": result.get("reason", "N/A"),
            "risk": result.get("risk", "Unknown"),
            "impact": impact
        }

    except Exception as e:
        print(f"❌ AI_AGENT ERROR: {str(e)}")
        return {
            "insight": "Unable to analyze",
            "reason": "AI service error or invalid response formatting",
            "risk": "Unknown",
            "impact": "₹0"
        }

if __name__ == "__main__":
    # Quick Test Execution
    test_ticker = "RELIANCE.NS"
    test_portfolio = {"RELIANCE": 10}
    print(f"--- Testing AI Agent for {test_ticker} ---")
    print(generate_advice(test_ticker, portfolio=test_portfolio))