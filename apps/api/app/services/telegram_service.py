import logging
import socket
from contextlib import contextmanager

import httpx

from app.core.config import settings
from app.schemas.access_request import AccessRequestCreate

logger = logging.getLogger(__name__)

# Some RU VPS resolve api.telegram.org to a blocked anycast IP.
# Prefer a known working Bot API endpoint IP when configured.
_FORCE_IP = "149.154.167.220"
_original_getaddrinfo = socket.getaddrinfo


def _escape_html(value: str) -> str:
    return value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


@contextmanager
def _forced_telegram_ip(ip: str):
    def patched(host, port, family=0, type=0, proto=0, flags=0):  # noqa: A002
        if host == "api.telegram.org" and ip:
            host = ip
        return _original_getaddrinfo(host, port, family, type, proto, flags)

    socket.getaddrinfo = patched
    try:
        yield
    finally:
        socket.getaddrinfo = _original_getaddrinfo


async def send_monitoring_request_telegram(request_id: int, payload: AccessRequestCreate) -> None:
    """Send a monitoring lead notification to the configured Telegram chat."""
    if not settings.telegram_configured:
        logger.warning("Telegram is not configured; skipping notification for request %s", request_id)
        return

    text = "\n".join(
        [
            "<b>Новая заявка на мониторинг</b>",
            "",
            f"<b>ID:</b> {request_id}",
            f"<b>Имя:</b> {_escape_html(payload.contact_name)}",
            f"<b>Телефон:</b> {_escape_html(payload.contact_phone)}",
            f"<b>Объект мониторинга:</b> {_escape_html(payload.monitoring_object)}",
            f"<b>Email:</b> {_escape_html(payload.contact_email or '—')}",
            f"<b>Запрос preview:</b> {_escape_html(payload.query or '—')}",
            f"<b>Комментарий:</b> {_escape_html(payload.message or '—')}",
        ]
    )

    base = settings.telegram_api_base.rstrip("/")
    url = f"{base}/bot{settings.telegram_bot_token}/sendMessage"
    client_kwargs: dict = {"timeout": 45.0}
    if settings.telegram_proxy:
        client_kwargs["proxy"] = settings.telegram_proxy

    force_ip = settings.telegram_force_ip or _FORCE_IP
    last_error: Exception | None = None

    for attempt in range(1, 4):
        try:
            with _forced_telegram_ip(force_ip):
                async with httpx.AsyncClient(**client_kwargs) as client:
                    response = await client.post(
                        url,
                        json={
                            "chat_id": settings.telegram_chat_id,
                            "text": text,
                            "parse_mode": "HTML",
                            "disable_web_page_preview": True,
                        },
                    )
                    if response.status_code >= 400:
                        raise RuntimeError(
                            f"Telegram API error {response.status_code}: {response.text}"
                        )
            logger.info(
                "Lead Telegram message sent to chat %s for request %s (attempt %s)",
                settings.telegram_chat_id,
                request_id,
                attempt,
            )
            return
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            logger.warning(
                "Telegram send attempt %s failed for request %s: %s",
                attempt,
                request_id,
                exc,
            )

    raise RuntimeError(f"Telegram notification failed after retries: {last_error}")
