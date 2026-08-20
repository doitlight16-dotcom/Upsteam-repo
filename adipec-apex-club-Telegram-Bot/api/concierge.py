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

GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
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
# LLM CLIENT (Google Gemini via OpenAI SDK)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

_llm_client = None


def _get_llm_client():
    """Lazy-initialize Google Gemini client."""
    global _llm_client
    if _llm_client is not None:
        return _llm_client, GEMINI_MODEL

    from openai import OpenAI

    if not GEMINI_API_KEY:
        return None, None

    try:
        _llm_client = OpenAI(
            api_key=GEMINI_API_KEY,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        )
        logger.info("✅ Gemini client initialized (model: %s)", GEMINI_MODEL)
        return _llm_client, GEMINI_MODEL
    except Exception as e:
        logger.error("❌ Gemini init failed: %s", e)
        return None, None


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
    client, model_name = _get_llm_client()
    if not client:
        raise HTTPException(
            status_code=503,
            detail="AI Concierge unavailable — GEMINI_API_KEY or OPENAI_API_KEY not configured.",
        )

    # Load tenant config for system prompt injection
    tenant_config = _load_tenant(request.tenant_id)
    system_prompt = build_system_prompt(
        tenant_config=tenant_config.model_dump(),
    )

    # Build messages array for LLM
    llm_messages = [{"role": "system", "content": system_prompt}]

    # Trim conversation history to prevent token overflow
    recent_messages = request.messages[-MAX_HISTORY_MESSAGES:]
    for msg in recent_messages:
        if msg.role in ("user", "assistant"):
            llm_messages.append({"role": msg.role, "content": msg.content})

    try:
        completion = client.chat.completions.create(
            model=model_name,
            messages=llm_messages,
            max_tokens=1024,
            temperature=0.7,
        )
        reply = completion.choices[0].message.content or "Не удалось сгенерировать ответ."
        model_used = completion.model or model_name

        logger.info(
            "Concierge chat: tenant=%s, user_msgs=%d, model=%s, tokens=%s",
            request.tenant_id,
            len(recent_messages),
            model_used,
            getattr(completion.usage, "total_tokens", "?"),
        )

        return ChatResponse(reply=reply, model=model_used)

    except Exception as e:
        logger.exception("LLM chat completion error: %s", e)
        raise HTTPException(
            status_code=500,
            detail=f"AI processing error: {str(e)}",
        )
