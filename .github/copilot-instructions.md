# Project rules
- Stack: Python 3.12, FastAPI, LangGraph, Pydantic v2, pytest, ruff, uv.
- Async everywhere. Type hints on all functions.
- Provider calls go through adapters in `shared/adapters/`. Never call vendor SDKs from business logic.
- Secrets come from env vars only.
- Answers must be short. No restating the question. Code first, one line of explanation max.
- When editing, show only changed functions or a diff, not whole files.