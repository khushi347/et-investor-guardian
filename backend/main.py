# main.py

from fastapi import FastAPI
from ai_agent import generate_advice
from radar import generate_radar_alerts

app = FastAPI()


@app.get("/")
def home():
    return {"message": "ET Investor Guardian Backend Running 🚀"}


# 🔥 FINAL API
@app.get("/ask")
def ask_api(ticker: str, query: str):
    # 🤖 AI Decision
    ai_result = generate_advice(ticker, query)

    # 📡 Radar Alerts
    alerts = generate_radar_alerts(ticker)

    # 🔗 Combine everything
    return {
        "stock": ticker,
        "decision": ai_result["decision"],
        "reason": ai_result["reason"],
        "risk": ai_result["risk"],
        "alerts": alerts,
        "data": ai_result["data"]
    }