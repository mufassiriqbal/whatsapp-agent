import qdrant_client
from qdrant_client import models
from app.models import User


def build_acl_filter(user: User) -> qdrant_client.models.Filter:
    return models.Filter(
        must=[
            models.FieldCondition(
                key="metadata.tenant_id",
                match=models.MatchValue(value=user.tenant_id),
            ),
            models.FieldCondition(
                key="metadata.access_groups",
                match=models.MatchAny(any=user.groups),
            ),
        ],
    )