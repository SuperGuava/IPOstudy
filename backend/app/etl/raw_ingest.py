import json


def save_raw_payload(source: str, endpoint: str, payload: dict) -> dict:
    return {
        "source": source,
        "endpoint": endpoint,
        "payload": json.dumps(payload, ensure_ascii=False),
    }
