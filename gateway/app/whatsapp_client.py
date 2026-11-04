import httpx

from app.config import get_settings


def send_text(to: str, body: str) -> None:
    settings = get_settings()
    with httpx.Client(timeout=15.0) as client:
        response = client.post(
            f"https://graph.facebook.com/v21.0/{settings.whatsapp_phone_number_id}/messages",
            headers={
                "Authorization": f"Bearer {settings.whatsapp_access_token}",
            },
            json={
                "messaging_product": "whatsapp",
                "to": to,
                "type": "text",
                "text": {"body": body[:4096]},
            },
        )
        response.raise_for_status()
