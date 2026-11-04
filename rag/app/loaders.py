import json
from pathlib import Path

from langchain_core.documents import Document

from app.models import AccessPolicy


def load_sources(root: Path) -> list[Document]:
    documents: list[Document] = []
    for path in root.rglob("*.md"):
        sidecar = path.with_name(f"{path.stem}.meta.json")
        if not sidecar.exists():
            raise ValueError(f"Missing sidecar file: {sidecar}")

        policy = AccessPolicy.model_validate(
            json.loads(sidecar.read_text(encoding="utf-8"))
        )
        documents.append(
            Document(
                page_content=path.read_text(encoding="utf-8"),
                metadata={
                    "source": str(path.relative_to(root)),
                    "doc_id": path.stem,
                    "tenant_id": policy.tenant_id,
                    "access_groups": policy.access_groups,
                    "classification": policy.classification,
                },
            )
        )
    return documents