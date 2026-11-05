from pathlib import Path

from fastapi import APIRouter, Header, HTTPException
from fastapi.responses import FileResponse
from langchain_core.messages import HumanMessage
from pydantic import BaseModel, Field

from app.graph import graph
from app.tools import clear_current_user, set_current_user
from app.web_auth import (
    load_web_users,
    make_session_token,
    read_session_token,
    verify_password,
)


class LoginRequest(BaseModel):
    username: str
    password: str


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)


router = APIRouter()


@router.get("/web")
def web() -> FileResponse:
    index_path = Path(__file__).resolve().parents[1] / "web" / "index.html"
    return FileResponse(index_path)


@router.post("/web/login")
def login(request: LoginRequest) -> dict[str, str]:
    user = load_web_users().get(request.username)
    if user is None or not verify_password(request.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    return {"token": make_session_token(user)}


@router.post("/web/chat")
def chat(
    request: ChatRequest,
    authorization: str | None = Header(default=None),
) -> dict[str, str]:
    if authorization is None or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid session token")

    user = read_session_token(authorization.removeprefix("Bearer "))
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid session token")

    set_current_user(user)
    try:
        result = graph.invoke({"messages": [HumanMessage(request.message)]})
        content = result["messages"][-1].content
        if isinstance(content, str):
            text = content
        else:
            text = "".join(
                part["text"] for part in content if isinstance(part, dict)
            )
        return {"reply": text}
    finally:
        clear_current_user()