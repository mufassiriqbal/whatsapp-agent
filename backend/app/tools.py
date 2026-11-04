from contextvars import ContextVar
import logging
from typing import TypedDict

import httpx
from langchain_core.tools import tool

from app.rag_client import search_knowledge_remote


logger = logging.getLogger(__name__)


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

    try:
        results = search_knowledge_remote(
            user["user_id"],
            user["tenant_id"],
            user["groups"],
            query,
            k=4,
        )
    except httpx.HTTPStatusError:
        logger.exception("Knowledge base request failed with an HTTP status error")
        return "The company knowledge base is temporarily unavailable. Tell the user you can't check that right now and offer to connect them with a human."
    except httpx.HTTPError:
        logger.exception("Knowledge base request failed")
        return "The company knowledge base is temporarily unavailable. Tell the user you can't check that right now and offer to connect them with a human."
    if not results:
        return "No matching company documents found."

    return "\n".join(
        f"[{result['doc_id']}] ({result['source']}) {result['text']}"
        for result in results
    )
