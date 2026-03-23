import sys
import os
sys.path.append(os.path.dirname(__file__))

import json
from dotenv import load_dotenv

load_dotenv()

from groq import Groq
from data_fetcher import get_market_data

# 🔥 ADD THIS LINE HERE
print("API KEY:", os.getenv("GROQ_API_KEY"))

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

        # 🔥 IMPORTANT: Convert AI → JSON
        result = json.loads(raw_output)

        print("STEP 5: Parsed AI response")

        return result

    except Exception as e:
        print("ERROR:", str(e))

        # 🔥 fallback (never break UI)
        return {
            "insight": "Unable to analyze",
            "reason": "AI service error or invalid response",
            "risk": "Unknown"
        }