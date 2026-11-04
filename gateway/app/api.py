import logging

from fastapi import FastAPI, Query, Request
from fastapi.responses import PlainTextResponse, Response

from app.backend_client import send_to_backend
from app.dedupe import mark_seen
from app.identity import lookup_user
from app.security import verify_meta_signature, verify_webhook_challenge
from app.whatsapp_client import send_text


logger = logging.getLogger(__name__)
app = FastAPI()


@app.get("/webhook", response_model=None)
def verify_webhook(
    hub_mode: str = Query(alias="hub.mode"),
    hub_verify_token: str = Query(alias="hub.verify_token"),
    hub_challenge: str = Query(alias="hub.challenge"),
) -> PlainTextResponse | Response:
    challenge = verify_webhook_challenge(
        hub_mode,
        hub_verify_token,
        hub_challenge,
    )
    if challenge is None:
        return Response(status_code=403)
    return PlainTextResponse(challenge)


@app.post("/webhook", response_model=None)
async def receive_webhook(request: Request) -> Response:
    raw_body = await request.body()
    if not verify_meta_signature(
        raw_body,
        request.headers.get("X-Hub-Signature-256"),
    ):
        return Response(status_code=403)

    payload = await request.json()
    for entry in payload.get("entry", []):
        for change in entry.get("changes", []):
            for message in change.get("value", {}).get("messages", []):
                if message.get("type") != "text":
                    continue
                message_id = message["id"]
                if not mark_seen(message_id):
                    continue

                sender = message["from"]
                user = lookup_user(sender)
                if user is None:
                    logger.warning("Unknown webhook sender: %s", sender)
                    continue

                text = message["text"]["body"]
                reply = send_to_backend(
                    conversation_id=sender,
                    message=text,
                    user=user,
                )
                try:
                    send_text(sender, reply)
                except Exception:
                    logger.exception("Failed to send WhatsApp reply to %s", sender)

    return Response(status_code=200)