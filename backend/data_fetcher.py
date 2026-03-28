# data_fetcher.py

import yfinance as yf
import pandas as pd
import random


def get_market_data(ticker):
    result = {
        "price": {},
        "signals": [],
        "news": []
    }

    try:
        stock = yf.Ticker(ticker)

        # =========================
        # 📊 1. PRICE DATA
        # =========================
        hist = stock.history(period="5d")  

        if hist is not None and not hist.empty:
            
            if len(hist) >= 2:
                latest = hist.iloc[-1]
                prev = hist.iloc[-2]

                change_percent = ((latest["Close"] - prev["Close"]) / prev["Close"]) * 100

                result["price"] = {
                    "current_price": float(round(latest["Close"], 2)),
                    "prev_close": float(round(prev["Close"], 2)),   
                    "change_percent": float(round(change_percent, 2))
                }

            else:
                # only 1 row available
                latest = hist.iloc[-1]

                result["price"] = {
                "current_price": float(round(latest["Close"], 2)),
                "prev_close": float(round(latest["Close"], 2)),  # ✅ fallback
                "change_percent": 0.0
                }

        else:
            result["price"] = {
            "current_price": 0.0,
            "prev_close": 0.0,   # ✅ ADD THIS
            "change_percent": 0.0
             }

        # =========================
        # 🏦 2. BULK/BLOCK DEALS (SIMULATED)
        # =========================
        fake_clients = ["HDFC Mutual Fund", "ICICI Prudential", "Foreign Investor", "SBI Funds"]

        result["signals"].append({
            "type": "bulk_deal",
            "client": random.choice(fake_clients),
            "action": random.choice(["BUY", "SELL"]),
            "quantity": random.randint(50000, 200000)
        })

        # =========================
        # 📰 3. NEWS
        # =========================
        try:
            news_items = stock.news

            if news_items:
                for item in news_items[:3]:
                    title = item.get("title")
                    link = item.get("link")

                    if title and link:
                        result["news"].append({
                            "title": title,
                            "publisher": item.get("publisher", "Unknown"),
                            "link": link
                        })

        except:
            pass

        # 👉 fallback if no news
        if not result["news"]:
            result["news"].append({
                "title": f"No recent news found for {ticker}",
                "publisher": "System",
                "link": "#"
            })

    except Exception as e:
        print("Error:", e)

    return result