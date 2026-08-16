"""AI module -- placeholder service.

This is a stand-in for whichever AI backend gets chosen later (an LLM API
wrapper, a custom model service, or something else). Its only job right
now is to implement a stable HTTP contract so the backend's AIModulePort
adapter can be built and tested against something real, instead of a mock.

Replacing this with the actual implementation should never require
changing the backend -- only this service and, if the contract genuinely
needs to grow, the AIModulePort interface it implements.
"""

from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Appex AI Module (placeholder)")


class InsightRequest(BaseModel):
    tenant_id: str
    subject: str
    context: dict[str, object] = {}


class InsightResponse(BaseModel):
    summary: str
    confidence: float


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/v1/insights", response_model=InsightResponse)
async def generate_insight(request: InsightRequest) -> InsightResponse:
    # Placeholder logic only -- real implementation TBD.
    return InsightResponse(
        summary=f"Placeholder insight for tenant '{request.tenant_id}' on '{request.subject}'.",
        confidence=0.0,
    )
