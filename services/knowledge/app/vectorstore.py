from functools import lru_cache

import qdrant_client
from langchain_qdrant import QdrantVectorStore
from qdrant_client import models

from app.config import get_settings
from app.embeddings import get_embeddings


@lru_cache
def get_vectorstore() -> QdrantVectorStore:
    settings = get_settings()
    client = qdrant_client.QdrantClient(url=settings.qdrant_url)

    if not client.collection_exists(settings.qdrant_collection):
        client.create_collection(
            collection_name=settings.qdrant_collection,
            vectors_config=models.VectorParams(
                size=settings.embedding_dim,
                distance=models.Distance.COSINE,
            ),
        )
        client.create_payload_index(
            collection_name=settings.qdrant_collection,
            field_name="metadata.tenant_id",
            field_schema=models.PayloadSchemaType.KEYWORD,
        )
        client.create_payload_index(
            collection_name=settings.qdrant_collection,
            field_name="metadata.access_groups",
            field_schema=models.PayloadSchemaType.KEYWORD,
        )

    return QdrantVectorStore(
        client=client,
        collection_name=settings.qdrant_collection,
        embedding=get_embeddings(),
    )