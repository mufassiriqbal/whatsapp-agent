from langchain_core.documents import Document

from app.acl import build_acl_filter
from app.models import User
from app.vectorstore import get_vectorstore


def search_chunks(user: User, query: str, k: int = 4) -> list[Document]:
    if not user.groups:
        return []

    acl_filter = build_acl_filter(user)
    return get_vectorstore().similarity_search(query, k=k, filter=acl_filter)
