"""APEX ASSET SUITE — AI Concierge Chat Endpoint
=================================================
POST /api/concierge/chat — Accepts user messages, returns AI response.
Uses OpenAI GPT-4o with injected domain context from context_builder.
"""

from __future__ import annotations

import logging
import os
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from .context_builder import build_system_prompt
from .tenant import _load_tenant

logger = logging.getLogger(__name__)

OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o")
MAX_HISTORY_MESSAGES: int = 20  # Cap conversation history sent to LLM


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# REQUEST / RESPONSE MODELS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class ChatMessage(BaseModel):
    role: str = Field(..., description="'user' or 'assistant'")
    content: str = Field(..., description="Message text")


class ChatRequest(BaseModel):
    messages: list[ChatMessage] = Field(..., description="Conversation history")
    tenant_id: str = Field(default="default", description="Tenant identifier for branding context")


class ChatResponse(BaseModel):
    reply: str = Field(..., description="AI concierge response text")
    model: str = Field(..., description="Model used for generation")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# OPENAI CLIENT (lazy init)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

_openai_client = None


def _get_openai():
    """Lazy-initialize OpenAI client."""
    global _openai_client
    if _openai_client is not None:
        return _openai_client

    if not OPENAI_API_KEY:
        return None

    try:
        from openai import OpenAI
        _openai_client = OpenAI(api_key=OPENAI_API_KEY)
        logger.info("✅ OpenAI client initialized (model: %s)", OPENAI_MODEL)
        return _openai_client
    except Exception as e:
        logger.error("❌ OpenAI init failed: %s", e)
        return None


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ROUTER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

router = APIRouter(prefix="/api/concierge", tags=["concierge"])


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """Process a chat message through the AI concierge.

    Injects tenant metadata and domain data as system prompt context.
    Maintains conversation history from the client side (stateless backend).
    """
    client = _get_openai()
    if not client:
        raise HTTPException(
            status_code=503,
            detail="AI Concierge unavailable — OPENAI_API_KEY not configured.",
        )

    # Load tenant config for system prompt injection
    tenant_config = _load_tenant(request.tenant_id)
    system_prompt = build_system_prompt(
        tenant_config=tenant_config.model_dump(),
    )

    # Build messages array for OpenAI
    openai_messages = [{"role": "system", "content": system_prompt}]

    # Trim conversation history to prevent token overflow
    recent_messages = request.messages[-MAX_HISTORY_MESSAGES:]
    for msg in recent_messages:
        if msg.role in ("user", "assistant"):
            openai_messages.append({"role": msg.role, "content": msg.content})

    try:
        completion = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=openai_messages,
            max_tokens=1024,
            temperature=0.7,
        )
        reply = completion.choices[0].message.content or "Не удалось сгенерировать ответ."
        model_used = completion.model or OPENAI_MODEL

        logger.info(
            "Concierge chat: tenant=%s, user_msgs=%d, model=%s, tokens=%s",
            request.tenant_id,
            len(recent_messages),
            model_used,
            getattr(completion.usage, "total_tokens", "?"),
        )

        return ChatResponse(reply=reply, model=model_used)

    except Exception as e:
        logger.exception("OpenAI chat completion error: %s", e)
        raise HTTPException(
            status_code=500,
            detail=f"AI processing error: {str(e)}",
        )
