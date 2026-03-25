import sys
import os
import json
from dotenv import load_dotenv
from groq import Groq

# Ensure local imports for data fetcher work
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
try:
    from backend.data_fetcher import get_market_data
except ImportError:
    # Fallback/Mock for local testing if M1 is not linked
    def get_market_data(ticker): return {"price": {}, "signals": [], "news": []}

load_dotenv()

# Initialize Groq Client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def build_prompt(ticker, market_data, user_query, portfolio, risk_level):
    """The Master Instruction: Combines market data with user context."""
    
    portfolio_context = f"User holds: {portfolio}" if portfolio else "User has no current holdings in this asset."
    
    # Inside build_prompt...
    return f"""
    You are the 'Investor Guardian'—an elite AI Financial Advisor for the Indian Stock Market.
    
    [CONTEXT]
    TARGET: {ticker} | PROFILE: {risk_level} | {portfolio_context}
    
    [MARKET DATA]
    Price/Signals/News: {market_data}

    [SCRIPTING INSTRUCTIONS]
    Write a "Guardian Briefing" script (max 35 words). 
    - DO NOT start with "The stock price is..." or "According to data...".
    - DO NOT use technical jargon like "50 SMA" unless it's the main reason for the move.
    - DO use active, human-like phrases: "I'm seeing a shift in...", "Your portfolio is currently...", "It's worth noting that...".
    - DO make it sound like a personal update from a high-level analyst.
    - Example: "I've detected a significant bullish crossover for Reliance. Given your balanced profile, this looks like a stable entry point, though I'd watch the current resistance levels closely."

    OUTPUT ONLY JSON: {{"insight": "...", "reason": "...", "risk_analysis": "...", "script": "..."}}
    """

def calculate_impact(ticker, market_data, portfolio):
    """Calculates the potential ₹ gain/loss based on current portfolio holdings."""
    if not portfolio:
        return "₹0"

    # Clean ticker for matching (e.g., RELIANCE.NS -> RELIANCE)
    stock_key = ticker.replace(".NS", "").upper()
    
    # Check if stock exists in user's dictionary
    if stock_key not in portfolio:
        return "₹0 (No Exposure)"

    quantity = portfolio[stock_key]
    price_data = market_data.get("price", {})
    
    current_price = price_data.get("current_price", 0)
    change_percent = price_data.get("change_percent", 0)

    # Math: (Qty * Price) * (Change % / 100)
    price_change = (change_percent / 100) * current_price
    impact_val = quantity * price_change

    if impact_val > 0:
        return f"+₹{int(impact_val):,}"
    elif impact_val < 0:
        return f"-₹{abs(int(impact_val)):,}"
    else:
        return "₹0"

def generate_advice(ticker, user_query="Analyze this stock", portfolio=None, risk_level="Balanced"):
    """Main entry point for M3 Dashboard to get AI reasoning."""
    
    # 🔹 M1: Fetch Real-Time Market Data
    market_data = get_market_data(ticker)

    # 🔹 M2: Construct Personalized Prompt
    prompt = build_prompt(ticker, market_data, user_query, portfolio, risk_level)

    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a specialized JSON-only financial engine."},
                {"role": "user", "content": prompt}
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.3, # Low temperature for financial accuracy
            response_format={"type": "json_object"}
        )

        raw_output = chat_completion.choices[0].message.content.strip()
        result = json.loads(raw_output)

        # Calculate Financial Impact for the UI
        impact_str = calculate_impact(ticker, market_data, portfolio)

        return {
            "insight": result.get("insight", "Monitoring..."),
            "reason": result.get("reason", "Awaiting further market triggers."),
            "risk": result.get("risk_analysis", "Moderate"),
            "impact": impact_str,
            "script": result.get("script", "Guardian scan complete.")
        }

    except Exception as e:
        print(f"❌ GUARDIAN_AI ERROR: {str(e)}")
        return {
            "insight": "Connection Throttled",
            "reason": "The Guardian Node is experiencing high latency. Standard analysis protocols apply.",
            "risk": "Unknown",
            "impact": "N/A",
            "script": "Guardian offline. Reconnecting to NSE feed."
        }