import base64
import hashlib
import hmac
import json
import secrets
import time
from functools import lru_cache
from pathlib import Path

from app.config import get_settings


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode(),
        salt,
        200_000,
    )
    return f"{salt.hex()}${password_hash.hex()}"


def verify_password(password: str, stored: str) -> bool:
    try:
        salt_hex, hash_hex = stored.split("$", 1)
        expected_hash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode(),
            bytes.fromhex(salt_hex),
            200_000,
        ).hex()
    except ValueError:
        return False
    return hmac.compare_digest(expected_hash, hash_hex)


@lru_cache
def load_web_users() -> dict:
    users_path = Path(__file__).resolve().parents[1] / "data" / "web_users.json"
    with users_path.open(encoding="utf-8") as users_file:
        return json.load(users_file)


def make_session_token(user: dict) -> str:
    payload = {
        "user_id": user["user_id"],
        "tenant_id": user["tenant_id"],
        "groups": user["groups"],
        "exp": int(time.time()) + 8 * 60 * 60,
    }
    payload_bytes = json.dumps(payload, separators=(",", ":")).encode()
    encoded_payload = base64.urlsafe_b64encode(payload_bytes).rstrip(b"=").decode()
    signature = hmac.new(
        get_settings().web_session_secret.encode(),
        encoded_payload.encode(),
        hashlib.sha256,
    ).hexdigest()
    return f"{encoded_payload}.{signature}"


def read_session_token(token: str) -> dict | None:
    try:
        encoded_payload, signature = token.split(".", 1)
        expected_signature = hmac.new(
            get_settings().web_session_secret.encode(),
            encoded_payload.encode(),
            hashlib.sha256,
        ).hexdigest()
        if not hmac.compare_digest(expected_signature, signature):
            return None

        padding = "=" * (-len(encoded_payload) % 4)
        payload = json.loads(
            base64.urlsafe_b64decode(f"{encoded_payload}{padding}").decode()
        )
        if payload["exp"] < time.time():
            return None
        return {
            "user_id": payload["user_id"],
            "tenant_id": payload["tenant_id"],
            "groups": payload["groups"],
        }
    except (ValueError, KeyError, TypeError, UnicodeDecodeError, json.JSONDecodeError):
        return None
