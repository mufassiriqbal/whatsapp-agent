import json
from pathlib import Path

from langchain_core.documents import Document


def load_sources(root: Path) -> list[Document]:
    documents: list[Document] = []
    for path in root.rglob("*.md"):
        sidecar = path.with_name(f"{path.name}.meta.json")
        if not sidecar.exists():
            raise ValueError(f"Missing sidecar file: {sidecar}")

        metadata = json.loads(sidecar.read_text(encoding="utf-8"))
        documents.append(
            Document(
                page_content=path.read_text(encoding="utf-8"),
                metadata={
                    "source": str(path.relative_to(root)),
                    "doc_id": path.stem,
                    "tenant_id": metadata["tenant_id"],
                    "access_groups": metadata["access_groups"],
                    "classification": metadata["classification"],
                },
            )
        )
    return documents