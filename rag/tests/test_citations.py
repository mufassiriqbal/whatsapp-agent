from app.models import User
from app.retriever import search_chunks


def test_hr_results_include_source_and_doc_id_metadata() -> None:
    results = search_chunks(
        User(id="hr-user", tenant_id="acme", groups=["hr"]),
        "leave policy",
    )

    assert results
    assert all(result.metadata.get("source") for result in results)
    assert all(result.metadata.get("doc_id") for result in results)


def test_hr_top_result_is_leave_policy() -> None:
    results = search_chunks(
        User(id="hr-user", tenant_id="acme", groups=["hr"]),
        "leave policy",
    )

    assert results[0].metadata["doc_id"] == "leave_policy"


def test_sales_pricing_results_include_pricing_citations() -> None:
    results = search_chunks(
        User(id="sales-user", tenant_id="acme", groups=["sales"]),
        "pricing",
    )

    assert results
    assert all(result.metadata["doc_id"] == "pricing" for result in results)
    assert all(result.metadata["source"].endswith("pricing.md") for result in results)
