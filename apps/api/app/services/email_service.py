import logging
from email.message import EmailMessage

import aiosmtplib

from app.core.config import settings
from app.schemas.access_request import AccessRequestCreate

logger = logging.getLogger(__name__)


async def send_monitoring_request_email(request_id: int, payload: AccessRequestCreate) -> None:
    """Send a monitoring lead notification to the configured mailbox."""
    if not settings.smtp_configured:
        raise RuntimeError(
            "SMTP is not configured. Set SMTP_PASSWORD (and related SMTP_* vars) in apps/api/.env"
        )

    message = EmailMessage()
    message["From"] = settings.smtp_from
    message["To"] = settings.leads_email_to
    message["Subject"] = f"Заявка на мониторинг #{request_id}: {payload.contact_name}"
    message.set_content(
        "\n".join(
            [
                "Новая заявка на мониторинг с сайта TG-Monitoring",
                "",
                f"ID: {request_id}",
                f"Имя: {payload.contact_name}",
                f"Телефон: {payload.contact_phone}",
                f"Объект мониторинга: {payload.monitoring_object}",
                f"Email клиента: {payload.contact_email or '—'}",
                f"Поисковый запрос (preview): {payload.query or '—'}",
                f"Комментарий: {payload.message or '—'}",
            ]
        )
    )

    await aiosmtplib.send(
        message,
        hostname=settings.smtp_host,
        port=settings.smtp_port,
        username=settings.smtp_username,
        password=settings.smtp_password,
        use_tls=settings.smtp_use_tls,
    )
    logger.info("Lead email sent to %s for request %s", settings.leads_email_to, request_id)
