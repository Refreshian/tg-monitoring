from fastapi import APIRouter, HTTPException

from app.schemas.preview import PreviewRequest, PreviewResponse
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
