from app.models import User
from app.retriever import search_chunks


def test_hr_user_can_retrieve_leave_policy() -> None:
    results = search_chunks(
        User(id="hr-user", tenant_id="acme", groups=["hr"]),
        "leave policy",
    )

    assert any(result.metadata["doc_id"] == "leave_policy" for result in results)


def test_sales_user_cannot_retrieve_leave_policy() -> None:
    results = search_chunks(
        User(id="sales-user", tenant_id="acme", groups=["sales"]),
        "leave policy",
    )

    assert all(result.metadata["doc_id"] != "leave_policy" for result in results)


def test_user_without_groups_gets_no_results() -> None:
    assert search_chunks(
        User(id="ungrouped-user", tenant_id="acme", groups=[]),
        "leave policy",
    ) == []


def test_user_from_other_tenant_cannot_retrieve_leave_policy() -> None:
    results = search_chunks(
        User(id="other-tenant-user", tenant_id="other", groups=["hr"]),
        "leave policy",
    )

    assert all(result.metadata["doc_id"] != "leave_policy" for result in results)