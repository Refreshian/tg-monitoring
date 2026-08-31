import json
import logging
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, HTTPException

from app.schemas.access_request import AccessRequestCreate, AccessRequestRead
from app.services.email_service import send_monitoring_request_email
from app.services.preview_samples_delivery import deliver_preview_samples
from app.services.telegram_service import send_monitoring_request_telegram

logger = logging.getLogger(__name__)

router = APIRouter()

_STORAGE = Path("data") / "access_requests.jsonl"


@router.post("", response_model=AccessRequestRead, status_code=201)
async def create_access_request(payload: AccessRequestCreate) -> AccessRequestRead:
    """Accept a monitoring lead, email it, and notify Telegram."""
    _STORAGE.parent.mkdir(parents=True, exist_ok=True)
    request_id = int(datetime.now(timezone.utc).timestamp() * 1000)
    record = {
        "id": request_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        **payload.model_dump(mode="json"),
    }
    with _STORAGE.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")

    errors: list[str] = []

    try:
        await send_monitoring_request_email(request_id, payload)
    except Exception:  # noqa: BLE001
        logger.exception("Failed to email monitoring request %s", request_id)
        errors.append("email")

    try:
        await send_monitoring_request_telegram(request_id, payload)
    except Exception:  # noqa: BLE001
        logger.exception("Failed to send Telegram notification for request %s", request_id)
        errors.append("telegram")

    if payload.sample_token and payload.contact_email:
        try:
            await deliver_preview_samples(payload.sample_token, str(payload.contact_email))
        except Exception:  # noqa: BLE001
            logger.exception(
                "Failed to auto-send preview samples for request %s to %s",
                request_id,
                payload.contact_email,
            )

    if errors:
        channels = " и ".join(errors)
        raise HTTPException(
            status_code=502,
            detail=(
                f"Заявка сохранена, но не удалось отправить уведомление ({channels}). "
                "Попробуйте позже или напишите нам напрямую."
            ),
        )

    return AccessRequestRead(id=request_id, **payload.model_dump())
