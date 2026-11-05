import hmac

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

from app.config import get_settings
from app.models import User
from app.retriever import search_chunks


class SearchRequest(BaseModel):
    user_id: str
    tenant_id: str
    groups: list[str]
    query: str
    k: int = Field(default=4, ge=1, le=10)


class SearchResult(BaseModel):
    text: str
    source: str
    doc_id: str


class SearchResponse(BaseModel):
    results: list[SearchResult]


app = FastAPI()

@app.on_event("startup")
def warm_up() -> None:
    from app.embeddings import get_embeddings
    from app.vectorstore import get_vectorstore

    get_embeddings().embed_query("warm up")
    get_vectorstore()


@app.post("/search", response_model=SearchResponse)
async def search(
    request: SearchRequest,
    x_internal_token: str | None = Header(default=None),
) -> SearchResponse:
    settings = get_settings()
    if x_internal_token is None or not hmac.compare_digest(
        x_internal_token, settings.internal_token
    ):
        raise HTTPException(status_code=401, detail="Invalid internal token")

    user = User(
        id=request.user_id,
        tenant_id=request.tenant_id,
        groups=request.groups,
    )
    chunks = search_chunks(user, request.query, request.k)
    return SearchResponse(
        results=[
            SearchResult(
                text=chunk.page_content,
                source=chunk.metadata["source"],
                doc_id=chunk.metadata["doc_id"],
            )
            for chunk in chunks
        ]
    )
