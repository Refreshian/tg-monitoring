import logging

from app.schemas.preview import SendSamplesResponse
from app.services.email_service import send_preview_samples_email
from app.services.preview_samples_cache import get_bundle, mark_email_sent, was_email_sent

logger = logging.getLogger(__name__)


async def deliver_preview_samples(sample_token: str, email: str) -> SendSamplesResponse:
    bundle = get_bundle(sample_token)
    if bundle is None:
        return SendSamplesResponse(
            sent=False,
            message="Примеры не найдены или срок ссылки истёк. Запустите оценку заново.",
        )

    normalized = email.strip().lower()
    if was_email_sent(sample_token, normalized):
        return SendSamplesResponse(
            sent=True,
            message="Примеры уже были отправлены на этот адрес.",
        )

    try:
        await send_preview_samples_email(
            recipient=email,
            query=bundle.query,
            items=bundle.items,
            sample_token=sample_token,
        )
    except Exception:  # noqa: BLE001
        logger.exception("Failed to send preview samples to %s", email)
        return SendSamplesResponse(
            sent=False,
            message="Не удалось отправить письмо. Попробуйте позже.",
        )

    mark_email_sent(sample_token, normalized)
    return SendSamplesResponse(
        sent=True,
        message="Примеры отправлены на указанный email.",
    )
