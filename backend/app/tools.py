from contextvars import ContextVar
from typing import TypedDict

from langchain_core.tools import tool

from app.rag_client import search_knowledge_remote


class VerifiedUser(TypedDict):
    user_id: str
    tenant_id: str
    groups: list[str]


current_user: ContextVar[VerifiedUser | None] = ContextVar(
    "current_user",
    default=None,
)


def set_current_user(user: VerifiedUser) -> None:
    current_user.set(user)


def clear_current_user() -> None:
    current_user.set(None)


@tool
def search_knowledge(query: str) -> str:
    """Search the company's approved documents and return matching passages with their sources. Use this for any question about company policies, pricing, or internal information."""

    user = current_user.get()
    if user is None:
        raise RuntimeError("No verified user is set")

    results = search_knowledge_remote(
        user["user_id"],
        user["tenant_id"],
        user["groups"],
        query,
        k=4,
    )
    if not results:
        return "No matching company documents found."

    return "\n".join(
        f"[{result['doc_id']}] ({result['source']}) {result['text']}"
        for result in results
    )
