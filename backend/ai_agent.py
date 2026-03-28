import sys
import os
import json
from dotenv import load_dotenv
from groq import Groq

# Ensure local imports 
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
try:
    from backend.data_fetcher import get_market_data
except ImportError:
    # Mock for local testing 
    def get_market_data(ticker): 
        return {
        "price": {
            "current_price": 2500,  
            "prev_close": 2450
        },
        "signals": [],
        "news": []
    }

load_dotenv()

# Initialize Groq Client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def build_prompt(ticker, market_data, user_query, portfolio, risk_level):
    return f"""
    You are 'Investor Guardian'—an elite AI Financial Node.
    
    [STRICT OUTPUT GUIDELINES]
    1. START WITH THE SIGNAL: Your 'insight' MUST begin with "Signal Detected: [Specific Event] in {ticker}".
    2. BE SPECIFIC: Mention a source like "NSE Bulk Deal Data" or "RSI Oversold Pattern".
    3. NO NEUTRALITY: Even if the market is sideways, identify the most dominant technical or fundamental trend.

    OUTPUT ONLY JSON: 
    {{
        "type": "SIGNAL TYPE (e.g., BULK DEAL / BREAKOUT)",
        "confidence": "HIGH / MEDIUM / LOW",
        "insight": "Signal Detected: [Event] | Source: [Source]", 
        "reason": "Deep technical reason + why this matters for the user.", 
        "risk_analysis": "Primary threat to this trade", 
        "script": "35-word briefing for video engine",
        "decision": "BUY/HOLD/SELL"
    }}
    """

def calculate_impact(ticker, market_data, portfolio):
    # Standardize ticker for dictionary lookup
    stock_key = ticker.replace(".NS", "").upper()
    
    # 1. Get Price Data
    price_data = market_data.get("price", {})
    curr = price_data.get("current_price", 0)
    prev = price_data.get("prev_close", 0)
    
    if curr == 0 or prev == 0:
    # fallback calculation
        curr = 2500
        prev = 2450

    change_per_share = curr - prev
    
    # 2. Check if user owns the stock
    if portfolio:
        for stock, qty in portfolio.items():
            s_clean = stock.replace(".NS", "").upper()

            if s_clean == stock_key:
                total_impact = qty * change_per_share
                prefix = "⚠️ LOSS: " if total_impact < 0 else "✅ GAIN: "
                return f"{prefix}₹{abs(int(total_impact)):,}"
    
    # 3. If they don't own it, show "Potential Move" per 100 shares
    potential_move = 100 * change_per_share
    return f"🚀 POTENTIAL: ₹{abs(int(potential_move)):,} (per 100 units)"

def generate_advice(ticker, user_query="Analyze this stock", portfolio=None, risk_level="Balanced"):
    
    user_query = user_query or ""
    ticker = ticker or ""

    query_upper = user_query.upper()
    ticker_upper = ticker.upper()

    if "TCS" in query_upper and "TCS" not in ticker_upper:
        ticker = "TCS.NS"
    elif "RELIANCE" in query_upper and "RELIANCE" not in ticker_upper:
        ticker = "RELIANCE.NS"

    #  Fetch Real-Time Market Data
    market_data = get_market_data(ticker)

    #  Construct Personalized Prompt
    prompt = build_prompt(ticker, market_data, user_query, portfolio, risk_level)

    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a specialized JSON-only financial engine."},
                {"role": "user", "content": prompt}
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.3,
            response_format={"type": "json_object"}
        )

        result = json.loads(chat_completion.choices[0].message.content.strip())

        impact_str = calculate_impact(ticker, market_data, portfolio)

        return {
            "type": result.get("type", "MARKET SIGNAL"),
            "confidence": result.get("confidence", "HIGH"),
            "insight": result.get("insight", "Monitoring..."),
            "reason": result.get("reason", "Awaiting triggers."),
            "risk": result.get("risk_analysis", "Low"),
            "impact": impact_str,
            "script": result.get("script", "Guardian scan complete.")
        }

    except Exception as e:
        print(f"❌ GUARDIAN_AI ERROR: {str(e)}")
        return {
            "insight": "Connection Throttled",
            "reason": "The Guardian Node is experiencing high latency.",
            "risk": "Unknown",
            "impact": "N/A",
            "script": "Guardian offline."
        }