from ai_agent import generate_advice
import json

print("STARTED")

result = generate_advice(
    ticker="TCS.NS",
    portfolio={"TCS": 20, "INFY": 15},
    user_query="Should I buy TCS?"
)

print("\nFINAL OUTPUT:")
print(json.dumps(result, indent=2))
