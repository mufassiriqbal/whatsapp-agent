import hmac

from fastapi import FastAPI, Header, HTTPException
from langchain_core.messages import HumanMessage
from pydantic import BaseModel, Field

from app.config import get_settings
from app.graph import graph
from app.tools import clear_current_user, set_current_user


class ChatRequest(BaseModel):
    conversation_id: str
    message: str = Field(min_length=1, max_length=2000)
    user_id: str
    tenant_id: str
    groups: list[str]


class ChatResponse(BaseModel):
    reply: str


app = FastAPI()


@app.post("/chat", response_model=ChatResponse)
def chat(
    request: ChatRequest,
    x_internal_token: str | None = Header(default=None),
) -> ChatResponse:
    settings = get_settings()
    if x_internal_token is None or not hmac.compare_digest(
        x_internal_token, settings.internal_token
    ):
        raise HTTPException(status_code=401, detail="Invalid internal token")

    set_current_user(
        {
            "user_id": request.user_id,
            "tenant_id": request.tenant_id,
            "groups": request.groups,
        }
    )
    try:
        result = graph.invoke({"messages": [HumanMessage(request.message)]})
        content = result["messages"][-1].content
        if isinstance(content, str):
            text = content
        else:
            text = "".join(
                part["text"] for part in content if isinstance(part, dict)
            )
        return ChatResponse(reply=text)
    finally:
        clear_current_user()
