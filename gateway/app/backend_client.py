import httpx

from app.config import get_settings
from app.identity import VerifiedUser


def send_to_backend(
    conversation_id: str,
    message: str,
    user: VerifiedUser,
) -> str:
    settings = get_settings()
    with httpx.Client(timeout=60.0) as client:
        response = client.post(
            f"{settings.backend_url}/chat",
            json={
                "conversation_id": conversation_id,
                "message": message,
                "user_id": user.user_id,
                "tenant_id": user.tenant_id,
                "groups": user.groups,
            },
            headers={"X-Internal-Token": settings.internal_token},
        )
    response.raise_for_status()
    return response.json()["reply"]
