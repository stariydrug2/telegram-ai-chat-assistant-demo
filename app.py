"""Local preview of the TeleFlow neurochatting demo limits."""

from __future__ import annotations

from dataclasses import dataclass

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="TeleFlow Neurochatting Demo")
DEMO_MAX_ACCOUNTS = 1
DEMO_MAX_CHATS = 2
DEMO_DRAFTS_PER_SESSION = 1


class Setup(BaseModel):
    account_count: int = Field(ge=0)
    chats: list[str] = Field(default_factory=list)


class PreviewRequest(BaseModel):
    chat: str
    sample_message: str = Field(min_length=1, max_length=2000)
    instruction: str = Field(default="Answer helpfully and stay on topic.", max_length=1000)


@dataclass
class DemoState:
    account_count: int = 0
    chats: tuple[str, ...] = ()
    drafts_created: int = 0


state = DemoState()


@app.get("/")
def home():
    return {
        "product": "TeleFlow Neurochatting Demo",
        "full_version": "https://teleflow.space/",
        "limits": {"accounts": DEMO_MAX_ACCOUNTS, "chats": DEMO_MAX_CHATS, "drafts_per_session": DEMO_DRAFTS_PER_SESSION},
        "notice": "Demo only: drafts are not sent to Telegram.",
    }


@app.post("/demo/setup")
def setup(payload: Setup):
    if payload.account_count > DEMO_MAX_ACCOUNTS:
        raise HTTPException(400, "Demo supports one Telegram account. Full workspace: https://teleflow.space/")
    chats = tuple(dict.fromkeys(chat.strip() for chat in payload.chats if chat.strip()))
    if len(chats) > DEMO_MAX_CHATS:
        raise HTTPException(400, "Demo supports up to two chats. Full workspace: https://teleflow.space/")
    state.account_count, state.chats, state.drafts_created = payload.account_count, chats, 0
    return {"account_count": state.account_count, "chats": state.chats, "full_version": "https://teleflow.space/"}


@app.post("/demo/preview")
def preview(payload: PreviewRequest):
    if payload.chat not in state.chats:
        raise HTTPException(400, "Choose one of the two configured demo chats.")
    if state.drafts_created >= DEMO_DRAFTS_PER_SESSION:
        raise HTTPException(429, "Demo draft limit reached. Continue at https://teleflow.space/")
    state.drafts_created += 1
    return {
        "status": "preview_only",
        "message": "Local demo preview only. There is no Telegram connection or AI generation.",
        "example": f"Preview input received for {payload.chat}. In the full product, AI drafts are generated using your own key and Telegram context.",
        "full_version": "https://teleflow.space/",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
