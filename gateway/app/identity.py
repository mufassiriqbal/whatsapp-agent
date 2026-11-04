import json
from functools import lru_cache
from pathlib import Path

from pydantic import BaseModel, ConfigDict


class VerifiedUser(BaseModel):
    model_config = ConfigDict(frozen=True)

    user_id: str
    tenant_id: str
    groups: list[str]


IDENTITIES_FILE = Path(__file__).resolve().parents[1] / "data" / "identities.json"


def _normalize_phone(phone: str) -> str:
    normalized = phone.replace(" ", "").replace("-", "")
    return normalized if normalized.startswith("+") else f"+{normalized}"


@lru_cache
def _load_identities() -> dict[str, VerifiedUser]:
    identities = json.loads(IDENTITIES_FILE.read_text(encoding="utf-8"))
    return {
        _normalize_phone(phone): VerifiedUser.model_validate(user)
        for phone, user in identities.items()
    }


def lookup_user(phone: str) -> VerifiedUser | None:
    return _load_identities().get(_normalize_phone(phone))