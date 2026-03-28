from utils import generate_id, get_confidence
from radar import generate_radar_alerts


def get_alerts():
    raw_alerts = generate_radar_alerts()

    formatted = []

    for i, alert in enumerate(raw_alerts):
        formatted.append({
            "id": generate_id(i),  
            "stock": alert["stock"],
            "event": alert["event"],
            "explanation": alert["explanation"],
            "confidence": get_confidence(alert["type"])  
        })

    return formatted