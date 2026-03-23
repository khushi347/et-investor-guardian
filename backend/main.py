from fastapi import FastAPI
from ai_agent import generate_advice
from radar import generate_radar_alerts

app = FastAPI()


@app.get("/")
def home():
    return {"message": "Backend Running 🚀"}


@app.get("/ask")
def ask_api(ticker: str, query: str):
    ai_result = generate_advice(ticker, query)
    alerts = generate_radar_alerts(ticker)

    return {
        "stock": ticker,
        "decision": ai_result["decision"],
        "reason": ai_result["reason"],
        "risk": ai_result["risk"],
        "alerts": alerts,
        "data": ai_result["data"]
    }