import httpx

from app.config import get_settings


def search_knowledge_remote(
    user_id: str,
    tenant_id: str,
    groups: list[str],
    query: str,
    k: int = 4,
) -> list[dict]:
    settings = get_settings()
    payload = {
        "user_id": user_id,
        "tenant_id": tenant_id,
        "groups": groups,
        "query": query,
        "k": max(1, min(10, k)),
    }
    with httpx.Client(timeout=10) as client:
        response = client.post(
            f"{settings.rag_url}/search",
            json=payload,
            headers={"X-Internal-Token": settings.internal_token},
        )
        response.raise_for_status()
        return response.json()["results"]