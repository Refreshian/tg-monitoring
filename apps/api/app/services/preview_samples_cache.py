"""Temporary cache for preview mention samples (not exposed on public search API)."""

from __future__ import annotations

import json
import logging
import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

from app.core.config import settings
from app.schemas.preview import MentionItem, MentionTeaser

logger = logging.getLogger(__name__)

SAMPLE_COUNT = 3


@dataclass
class PreviewSamplesBundle:
    token: str
    query: str
    items: list[MentionItem]
    created_at: datetime
    emails_sent: list[str]

    def is_expired(self) -> bool:
        ttl = timedelta(hours=settings.preview_samples_ttl_hours)
        return self.created_at + ttl < datetime.now(timezone.utc)

    def teasers(self) -> list[MentionTeaser]:
        return [
            MentionTeaser(
                source=item.source,
                url=item.url,
                published_at=item.published_at,
            )
            for item in self.items
        ]


def _cache_dir() -> Path:
    path = Path(__file__).resolve().parents[2] / "data" / "preview_samples"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _bundle_path(token: str) -> Path:
    safe = token.replace("/", "_").replace("\\", "_")
    return _cache_dir() / f"{safe}.json"


def store_samples(query: str, items: list[MentionItem]) -> str | None:
    """Persist up to SAMPLE_COUNT items and return a public token."""
    trimmed = items[:SAMPLE_COUNT]
    if not trimmed:
        return None

    token = secrets.token_urlsafe(24)
    bundle = PreviewSamplesBundle(
        token=token,
        query=query,
        items=trimmed,
        created_at=datetime.now(timezone.utc),
        emails_sent=[],
    )
    _write_bundle(bundle)
    return token


def get_bundle(token: str) -> PreviewSamplesBundle | None:
    path = _bundle_path(token)
    if not path.exists():
        return None
    try:
        bundle = _read_bundle(path)
    except Exception:  # noqa: BLE001
        logger.warning("Invalid preview samples cache at %s", path)
        return None
    if bundle.is_expired():
        try:
            path.unlink(missing_ok=True)
        except OSError:
            pass
        return None
    return bundle


def mark_email_sent(token: str, email: str) -> None:
    bundle = get_bundle(token)
    if bundle is None:
        return
    normalized = email.strip().lower()
    if normalized in bundle.emails_sent:
        return
    bundle.emails_sent.append(normalized)
    _write_bundle(bundle)


def was_email_sent(token: str, email: str) -> bool:
    bundle = get_bundle(token)
    if bundle is None:
        return False
    return email.strip().lower() in bundle.emails_sent


def _write_bundle(bundle: PreviewSamplesBundle) -> None:
    payload = {
        "token": bundle.token,
        "query": bundle.query,
        "created_at": bundle.created_at.isoformat(),
        "emails_sent": bundle.emails_sent,
        "items": [item.model_dump(mode="json") for item in bundle.items],
    }
    _bundle_path(bundle.token).write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _read_bundle(path: Path) -> PreviewSamplesBundle:
    payload = json.loads(path.read_text(encoding="utf-8"))
    created_at = datetime.fromisoformat(payload["created_at"])
    if created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=timezone.utc)
    items = [MentionItem.model_validate(item) for item in payload["items"]]
    return PreviewSamplesBundle(
        token=payload["token"],
        query=payload["query"],
        items=items,
        created_at=created_at,
        emails_sent=list(payload.get("emails_sent") or []),
    )
