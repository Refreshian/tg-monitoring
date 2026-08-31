import logging
from datetime import datetime
from email.message import EmailMessage

import aiosmtplib

from app.core.config import settings
from app.schemas.access_request import AccessRequestCreate
from app.schemas.preview import MentionItem

logger = logging.getLogger(__name__)

SAMPLE_TEXT_MAX = 400


def _format_published(value: datetime | None) -> str:
    if value is None:
        return "—"
    return value.strftime("%d.%m.%Y %H:%M")


def _truncate(text: str, limit: int = SAMPLE_TEXT_MAX) -> str:
    cleaned = " ".join(text.split())
    if len(cleaned) <= limit:
        return cleaned
    return cleaned[: limit - 1].rstrip() + "…"


def _samples_magic_link(token: str) -> str:
    base = settings.public_site_url.rstrip("/")
    return f"{base}/samples/{token}"


def _build_samples_plain(query: str, items: list[MentionItem], magic_link: str) -> str:
    lines = [
        "Примеры упоминаний по вашему запросу — TG-Monitoring",
        "",
        f"Запрос: {query}",
        "",
        "Подготовлено сервисом TG-Monitoring по вашему поисковому запросу.",
        "Тексты сообщений не публикуются на открытой странице сайта.",
        "",
    ]
    for index, item in enumerate(items, start=1):
        lines.extend(
            [
                f"--- Пример {index} ---",
                f"Источник: {item.source}",
                f"Дата: {_format_published(item.published_at)}",
                _truncate(item.text),
            ]
        )
        if item.url:
            lines.append(f"Ссылка: {item.url}")
        lines.append("")
    lines.extend(
        [
            "Посмотреть примеры на сайте:",
            magic_link,
            "",
            "Ссылка действует ограниченное время.",
            "",
            "Оставить заявку на мониторинг:",
            f"{settings.public_site_url.rstrip('/')}/preview#monitoring-request",
        ]
    )
    return "\n".join(lines)


def _build_samples_html(query: str, items: list[MentionItem], magic_link: str) -> str:
    cards = []
    for index, item in enumerate(items, start=1):
        link_html = (
            f'<p><a href="{item.url}">Открыть источник</a></p>' if item.url else ""
        )
        cards.append(
            f"""
            <div style="margin:16px 0;padding:12px 14px;border:1px solid #e0e0e0;border-radius:8px;">
              <p style="margin:0 0 6px;color:#4cc9f0;font-size:13px;">Пример {index} · {item.source}</p>
              <p style="margin:0 0 6px;color:#666;font-size:12px;">{_format_published(item.published_at)}</p>
              <p style="margin:0;line-height:1.45;">{_truncate(item.text)}</p>
              {link_html}
            </div>
            """
        )
    return f"""
    <div style="font-family:Arial,sans-serif;color:#222;line-height:1.5;">
      <h2 style="margin:0 0 12px;">Примеры упоминаний по вашему запросу</h2>
      <p style="margin:0 0 16px;color:#555;">Запрос: <strong>{query}</strong></p>
      <p style="margin:0 0 16px;color:#555;font-size:14px;">
        Подготовлено сервисом TG-Monitoring. Тексты не публикуются на открытой странице сайта.
      </p>
      {"".join(cards)}
      <p style="margin:20px 0 8px;">
        <a href="{magic_link}" style="color:#4cc9f0;">Открыть примеры на сайте</a>
      </p>
      <p style="margin:0;color:#888;font-size:12px;">Ссылка действует ограниченное время.</p>
    </div>
    """


async def send_preview_samples_email(
    recipient: str,
    query: str,
    items: list[MentionItem],
    sample_token: str,
) -> None:
    """Email 3 sample mentions to the visitor with a magic link."""
    if not settings.smtp_configured:
        raise RuntimeError(
            "SMTP is not configured. Set SMTP_PASSWORD (and related SMTP_* vars) in apps/api/.env"
        )

    magic_link = _samples_magic_link(sample_token)
    message = EmailMessage()
    message["From"] = settings.smtp_from
    message["To"] = recipient
    message["Subject"] = f"Примеры упоминаний по запросу — TG-Monitoring"
    plain = _build_samples_plain(query, items, magic_link)
    message.set_content(plain)
    message.add_alternative(_build_samples_html(query, items, magic_link), subtype="html")

    await aiosmtplib.send(
        message,
        hostname=settings.smtp_host,
        port=settings.smtp_port,
        username=settings.smtp_username,
        password=settings.smtp_password,
        use_tls=settings.smtp_use_tls,
    )
    logger.info("Preview samples email sent to %s for query %r", recipient, query[:80])


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
