# alerts.py


from utils import generate_id, get_confidence

"id": generate_id(i),
"confidence": get_confidence(alert["type"])
from radar import generate_radar_alerts


def get_alerts():
    raw_alerts = generate_radar_alerts()

    formatted = []

    for i, alert in enumerate(raw_alerts):
        formatted.append({
            "id": i + 1,
            "stock": alert["stock"],
            "event": alert["event"],
            "explanation": alert["explanation"],
            "confidence": "High" if alert["type"] == "bulk" else "Medium"
        })

    return formatted