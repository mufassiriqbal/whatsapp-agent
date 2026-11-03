from typing import Literal

from pydantic import BaseModel, ConfigDict


class User(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: str
    tenant_id: str
    groups: list[str]


class AccessPolicy(BaseModel):
    model_config = ConfigDict(frozen=True)

    tenant_id: str
    access_groups: list[str]
    classification: Literal["public", "internal", "confidential"]