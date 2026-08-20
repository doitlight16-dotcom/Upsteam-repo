"""APEX ASSET SUITE — Dynamic White-Label Tenant Configuration
==============================================================
Pydantic v2 schema + FastAPI router for tenant branding CRUD.
Storage: Upstash Redis (JSON serialized).
Admin auth: Bearer token via ADMIN_SECRET env var.
"""

from __future__ import annotations

import base64
import json
import logging
import os
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File, Form
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

ADMIN_SECRET: str = os.getenv("ADMIN_SECRET", "")
REDIS_KEY_PREFIX = "tenant:"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PYDANTIC MODELS (Tenant Config JSON Schema)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class TenantColors(BaseModel):
    """Theme color palette — maps to CSS custom properties."""
    bg: str = Field(default="#141210", description="Page background")
    surface: str = Field(default="#1C1812", description="Card / panel background")
    surface_hi: str = Field(default="#242017", description="Elevated surface")
    border: str = Field(default="#39311F", description="Default border")
    border_hi: str = Field(default="#4E4327", description="High-contrast border")
    gold: str = Field(default="#C9A227", description="Primary accent (gold)")
    gold_bright: str = Field(default="#E9CA73", description="Bright accent highlight")
    text: str = Field(default="#F1EAD9", description="Primary text")
    text_muted: str = Field(default="#9C9384", description="Secondary text")
    text_faint: str = Field(default="#6E6656", description="Tertiary / disabled text")
    accent_danger: str = Field(default="#9C3F35", description="Danger / SOS accent")
    accent_success: str = Field(default="#748A6C", description="Success accent")


class TenantFonts(BaseModel):
    """Typography configuration — Google Fonts families."""
    display: str = Field(default="'Fraunces', serif", description="Display / heading font")
    body: str = Field(default="'Manrope', sans-serif", description="Body text font")
    mono: str = Field(default="'IBM Plex Mono', monospace", description="Monospace / code font")


class TenantContact(BaseModel):
    """Support contact information."""
    support_username: str = Field(default="@appex_support", description="Telegram support handle")
    support_phone: str = Field(default="+971500000000", description="Emergency phone number")
    support_hours: str = Field(default="10:00–20:00 (UTC+4)", description="Availability hours")


class TenantConfig(BaseModel):
    """Complete tenant configuration — the single source of truth for branding."""
    tenant_id: str = Field(default="default", description="Unique tenant identifier")
    brand_name: str = Field(default="APEX ASSET SUITE", description="Brand name shown in headers")
    event_name: str = Field(default="ADIPEC Concierge", description="Event / product name")
    tagline: str = Field(
        default="АО «НК «КазМунайГаз» · закрытый доступ делегатов",
        description="Subtitle / tagline text",
    )
    colors: TenantColors = Field(default_factory=TenantColors)
    fonts: TenantFonts = Field(default_factory=TenantFonts)
    contact: TenantContact = Field(default_factory=TenantContact)
    logo_url: Optional[str] = Field(default=None, description="Logo image URL or base64 data URI")
    banner_url: Optional[str] = Field(default=None, description="Banner image URL or base64 data URI")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# REDIS HELPERS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

_redis_client = None


def _get_redis():
    """Lazy-init Redis client from UPSTASH_REDIS_URL."""
    global _redis_client
    if _redis_client is not None:
        return _redis_client

    redis_url = os.getenv("UPSTASH_REDIS_URL") or os.getenv("REDIS_URL", "")
    if not redis_url:
        logger.warning("No Redis URL configured — tenant config will use in-memory defaults only.")
        return None

    try:
        import redis as redis_lib
        _redis_client = redis_lib.from_url(redis_url, decode_responses=True)
        _redis_client.ping()
        logger.info("✅ Tenant Redis connected")
        return _redis_client
    except Exception as e:
        logger.error("❌ Tenant Redis connection failed: %s", e)
        return None


def _load_tenant(tenant_id: str) -> TenantConfig:
    """Load tenant config from Redis, or return defaults."""
    r = _get_redis()
    if r:
        try:
            raw = r.get(f"{REDIS_KEY_PREFIX}{tenant_id}")
            if raw:
                return TenantConfig.model_validate_json(raw)
        except Exception as e:
            logger.error("Redis load error for tenant '%s': %s", tenant_id, e)

    return TenantConfig(tenant_id=tenant_id)


def _save_tenant(config: TenantConfig) -> bool:
    """Save tenant config to Redis. Returns True on success."""
    r = _get_redis()
    if not r:
        logger.error("Cannot save tenant config — Redis not available.")
        return False
    try:
        r.set(
            f"{REDIS_KEY_PREFIX}{config.tenant_id}",
            config.model_dump_json(),
        )
        return True
    except Exception as e:
        logger.error("Redis save error for tenant '%s': %s", config.tenant_id, e)
        return False


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# AUTH
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

security = HTTPBearer(auto_error=False)


async def require_admin(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> str:
    """Validate admin bearer token."""
    if not ADMIN_SECRET:
        raise HTTPException(
            status_code=503,
            detail="Admin panel disabled — ADMIN_SECRET not configured.",
        )
    if not credentials or credentials.credentials != ADMIN_SECRET:
        raise HTTPException(status_code=401, detail="Invalid admin token.")
    return credentials.credentials


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ROUTER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

router = APIRouter(prefix="/api/tenant", tags=["tenant"])


@router.get("/{tenant_id}", response_model=TenantConfig)
async def get_tenant(tenant_id: str) -> TenantConfig:
    """Fetch tenant branding configuration (public, no auth)."""
    return _load_tenant(tenant_id)


@router.put("/{tenant_id}", response_model=TenantConfig)
async def update_tenant(
    tenant_id: str,
    payload: TenantConfig,
    _admin: str = Depends(require_admin),
) -> TenantConfig:
    """Update tenant branding configuration (admin only)."""
    payload.tenant_id = tenant_id  # Ensure consistency
    if _save_tenant(payload):
        logger.info("Tenant '%s' config updated.", tenant_id)
        return payload
    raise HTTPException(status_code=500, detail="Failed to save tenant config.")


@router.post("/{tenant_id}/upload")
async def upload_asset(
    tenant_id: str,
    field: str = Form(..., description="Field name: 'logo_url' or 'banner_url'"),
    file: UploadFile = File(...),
    _admin: str = Depends(require_admin),
) -> dict:
    """Upload a logo or banner image (admin only).

    Stores as base64 data URI in Redis (Vercel has no persistent filesystem).
    Max file size: ~2 MB.
    """
    if field not in ("logo_url", "banner_url"):
        raise HTTPException(status_code=400, detail="field must be 'logo_url' or 'banner_url'")

    content = await file.read()
    if len(content) > 2 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="File too large (max 2 MB)")

    content_type = file.content_type or "image/png"
    b64 = base64.b64encode(content).decode("ascii")
    data_uri = f"data:{content_type};base64,{b64}"

    config = _load_tenant(tenant_id)
    setattr(config, field, data_uri)
    if _save_tenant(config):
        return {"ok": True, "field": field, "size_bytes": len(content)}
    raise HTTPException(status_code=500, detail="Failed to save uploaded asset.")
