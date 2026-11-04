import hashlib
import hmac

from app.security import verify_meta_signature, verify_webhook_challenge

BODY = b'{"entry":[{"changes":[{"value":{"messages":[{"from":"923001112222","type":"text","text":{"body":"hi"}}]}}]}]}'


def _sign(body: bytes, secret: str) -> str:
    return "sha256=" + hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()


def test_valid_signature_passes(monkeypatch):
    monkeypatch.setattr("app.security.get_settings", lambda: type("S", (), {"meta_app_secret": "placeholder-app-secret", "meta_verify_token": "tok"})())
    assert verify_meta_signature(BODY, _sign(BODY, "placeholder-app-secret"))


def test_tampered_body_fails(monkeypatch):
    monkeypatch.setattr("app.security.get_settings", lambda: type("S", (), {"meta_app_secret": "placeholder-app-secret", "meta_verify_token": "tok"})())
    assert not verify_meta_signature(BODY + b" ", _sign(BODY, "placeholder-app-secret"))


def test_missing_or_malformed_header_fails(monkeypatch):
    monkeypatch.setattr("app.security.get_settings", lambda: type("S", (), {"meta_app_secret": "placeholder-app-secret", "meta_verify_token": "tok"})())
    assert not verify_meta_signature(BODY, None)
    assert not verify_meta_signature(BODY, "abc123")


def test_challenge_requires_matching_token(monkeypatch):
    monkeypatch.setattr("app.security.get_settings", lambda: type("S", (), {"meta_app_secret": "x", "meta_verify_token": "tok"})())
    assert verify_webhook_challenge("subscribe", "tok", "123") == "123"
    assert verify_webhook_challenge("subscribe", "wrong", "123") is None
    assert verify_webhook_challenge("unsubscribe", "tok", "123") is None