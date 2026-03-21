# main.py

from fastapi import FastAPI
from ai_agent import generate_advice

app = FastAPI()


@app.get("/")
def home():
    return {"message": "AI Backend Running 🚀"}


# 🔥 IMPORTANT: function must be BELOW decorator
@app.get("/ask")
def ask_api(ticker: str):
    result = generate_advice(ticker)
    return result