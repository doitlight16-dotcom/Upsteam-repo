from fastapi import FastAPI, Request, HTTPException, status, Depends
from pydantic import BaseModel
from app.config import settings
from app.db import vector_store
from app.prompts import build_kmg_system_prompt

app = FastAPI(title=settings.PROJECT_NAME)

class AIQuery(BaseModel):
    prompt: str

def get_tenant_id(request: Request) -> str:
    """Dependency to extract and validate corporate tenant identity from request state."""
    tenant_id = getattr(request.state, "tenant_id", None)
    if not tenant_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Corporate identity (tenant_id) missing or unverified."
        )
    return tenant_id

@app.post(f"{settings.API_V1_STR}/ai/ask")
async def ask_concierge(query: AIQuery, tenant_id: str = Depends(get_tenant_id)):
    # 1. RETRIEVAL: Query vector DB with strict tenant isolation
    retrieved_docs = vector_store.query_tenant_context(
        prompt=query.prompt,
        tenant_id=tenant_id
    )

    if not retrieved_docs:
        return {
            "status": "success",
            "tenant_id": tenant_id,
            "response": "Информация недоступна в рамках вашей корпоративной подписки."
        }

    # 2. CONTEXT & PROMPT CONSTRUCTION
    context_str = "\n\n".join(retrieved_docs)
    system_prompt = build_kmg_system_prompt(context=context_str)

    # 3. DELIVERABLE ASSEMBLY
    return {
        "status": "success",
        "tenant_id": tenant_id,
        "context_retrieved": context_str,
        "system_prompt_prepared": system_prompt
    }