import hashlib
import hmac

from app.config import get_settings


def verify_meta_signature(
    raw_body: bytes,
    signature_header: str | None,
) -> bool:
    if signature_header is None or not signature_header.startswith("sha256="):
        return False

    signature = signature_header.removeprefix("sha256=")
    if not signature:
        return False

    expected = hmac.new(
        get_settings().meta_app_secret.encode(),
        raw_body,
        hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(expected, signature)


def verify_webhook_challenge(
    mode: str,
    token: str,
    challenge: str,
) -> str | None:
    settings = get_settings()
    if mode == "subscribe" and hmac.compare_digest(
        token,
        settings.meta_verify_token,
    ):
        return challenge
    return None