from fastapi import APIRouter, HTTPException

from app.schemas.preview import (
    PreviewRequest,
    PreviewResponse,
    PreviewSamplesResponse,
    SendSamplesRequest,
    SendSamplesResponse,
)
from app.services.preview_samples_delivery import deliver_preview_samples
from app.services.preview_service import PreviewService

router = APIRouter()


@router.post("/search", response_model=PreviewResponse)
async def preview_search(payload: PreviewRequest) -> PreviewResponse:
    """Run a one-time mention search on br-analytics.ru for the landing preview."""
    service = PreviewService()
    try:
        return await service.search(payload.query)
    except Exception as exc:  # noqa: BLE001 — mapped to HTTP error at API boundary
        raise HTTPException(status_code=502, detail=f"br-analytics preview failed: {exc}") from exc


@router.post("/send-samples", response_model=SendSamplesResponse)
async def send_preview_samples(payload: SendSamplesRequest) -> SendSamplesResponse:
    """Email up to 3 sample mentions to the visitor (not shown on the public preview page)."""
    return await deliver_preview_samples(payload.sample_token, str(payload.email))


@router.get("/samples/{token}", response_model=PreviewSamplesResponse)
async def get_preview_samples(token: str) -> PreviewSamplesResponse:
    """Magic-link API: full sample texts for a limited-time token."""
    bundle = PreviewService().get_samples_by_token(token)
    if bundle is None:
        raise HTTPException(status_code=404, detail="Примеры не найдены или срок ссылки истёк.")
    return PreviewSamplesResponse(query=bundle.query, items=bundle.items)
