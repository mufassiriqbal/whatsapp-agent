from pathlib import Path
from uuid import NAMESPACE_URL, uuid5

from app.chunking import split_documents
from app.loaders import load_sources
from app.vectorstore import get_vectorstore


def ingest_sources(root: Path) -> int:
    chunks = split_documents(load_sources(root))
    document_chunk_indexes: dict[str, int] = {}
    ids: list[str] = []

    for chunk in chunks:
        doc_id = chunk.metadata["doc_id"]
        chunk_index = document_chunk_indexes.get(doc_id, 0)
        ids.append(str(uuid5(NAMESPACE_URL, f"{doc_id}:{chunk_index}")))
        document_chunk_indexes[doc_id] = chunk_index + 1

    get_vectorstore().add_documents(chunks, ids=ids)
    return len(chunks)


if __name__ == "__main__":
    print(ingest_sources(Path(__file__).resolve().parents[1] / "data" / "sources"))