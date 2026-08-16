"""Brand Analytics public tariff scraping and cached pricing estimates."""

from __future__ import annotations

import json
import logging
import re
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

from app.core.config import settings

logger = logging.getLogger(__name__)

# Fallback "Разово" tariffs from brandanalytics.ru/price/ (Aug 2026).
DEFAULT_RAZOVO_TARIFFS: list[dict] = [
    {"name": "Стартовый", "messages_per_month": 10_000, "price_rub": 45_500},
    {"name": "Стартовый плюс", "messages_per_month": 50_000, "price_rub": 68_900},
    {"name": "Базовый", "messages_per_month": 150_000, "price_rub": 100_100},
    {"name": "Расширенный", "messages_per_month": 500_000, "price_rub": 201_500},
]

CACHE_FILENAME = "ba_tariffs_cache.json"


@dataclass(frozen=True)
class Tariff:
    name: str
    messages_per_month: int
    price_rub: int


@dataclass(frozen=True)
class PriceQuote:
    """Quoted access price shown to the visitor (below BA list price)."""

    list_price_rub: int
    quote_price_rub: int
    tariff_name: str
    messages_limit: int
    estimated_monthly_messages: int
    price_is_from: bool = False


def estimate_monthly_from_weekly(weekly_count: int) -> int:
    """Convert BA 'За неделю' volume into an approximate monthly volume."""
    if weekly_count < 0:
        return 0
    return int(round(weekly_count / 7 * 30))


def quote_access_price(
    estimated_monthly_messages: int,
    *,
    tariffs: list[Tariff] | None = None,
    discount_ratio: float | None = None,
) -> PriceQuote | None:
    """
    Pick the cheapest Razovo tariff that covers monthly volume and apply the
    configured discount for the visitor-facing quote.
    """
    if estimated_monthly_messages <= 0:
        return None

    tiers = tariffs or load_tariffs()
    if not tiers:
        return None

    sorted_tiers = sorted(tiers, key=lambda t: t.messages_per_month)
    chosen = next(
        (t for t in sorted_tiers if t.messages_per_month >= estimated_monthly_messages),
        None,
    )
    price_is_from = False
    if chosen is None:
        chosen = sorted_tiers[-1]
        price_is_from = True

    ratio = discount_ratio if discount_ratio is not None else settings.price_quote_discount_ratio
    ratio = min(0.40, max(0.20, ratio))
    raw = chosen.price_rub * (1.0 - ratio)
    # Nearest 100 keeps quotes readable while staying close to BA * (1 - discount).
    quote = int(round(raw / 100.0) * 100)
    quote = max(100, quote)

    return PriceQuote(
        list_price_rub=chosen.price_rub,
        quote_price_rub=quote,
        tariff_name=chosen.name,
        messages_limit=chosen.messages_per_month,
        estimated_monthly_messages=estimated_monthly_messages,
        price_is_from=price_is_from,
    )


def load_tariffs() -> list[Tariff]:
    """Return cached tariffs (even if stale) or built-in Razovo defaults."""
    return _read_cache(allow_stale=True) or [
        _tariff_from_dict(item) for item in DEFAULT_RAZOVO_TARIFFS
    ]


async def refresh_tariffs() -> list[Tariff] | None:
    """Scrape https://brandanalytics.ru/price/ with Playwright (Разово mode)."""
    try:
        tariffs = await _scrape_razovo_tariffs()
    except Exception:  # noqa: BLE001
        logger.exception("Brand Analytics price scrape failed")
        return None

    if not tariffs:
        logger.warning("Brand Analytics price scrape returned no tariffs")
        return None

    _write_cache(tariffs)
    return tariffs


async def ensure_fresh_tariffs() -> list[Tariff]:
    """
    Return tariffs for quoting without blocking the preview request on a scrape.

    Uses a fresh cache when available; otherwise serves stale cache / defaults and
    refreshes in the background when the cache is missing or older than TTL.
    """
    fresh = _read_cache(allow_stale=False)
    if fresh is not None:
        return fresh

    # Missing or expired — refresh off the request path.
    try:
        import asyncio

        asyncio.create_task(_safe_background_refresh())
    except RuntimeError:
        pass

    return load_tariffs()


async def _safe_background_refresh() -> None:
    try:
        await refresh_tariffs()
    except Exception:  # noqa: BLE001
        logger.exception("Background BA tariff refresh failed")


def _cache_path() -> Path:
    return Path(__file__).resolve().parents[2] / "data" / CACHE_FILENAME


def _read_cache(*, allow_stale: bool = False) -> list[Tariff] | None:
    path = _cache_path()
    if not path.exists():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        fetched_at = datetime.fromisoformat(payload["fetched_at"])
        ttl_days = settings.ba_tariffs_cache_days
        expired = fetched_at + timedelta(days=ttl_days) < datetime.now(timezone.utc)
        if expired and not allow_stale:
            return None
        tariffs = [_tariff_from_dict(item) for item in payload["tariffs"]]
        if not tariffs or not _looks_like_razovo(tariffs):
            logger.warning("Ignoring BA tariffs cache with non-Razovo prices")
            return None
        return tariffs
    except Exception:  # noqa: BLE001
        logger.warning("Invalid BA tariffs cache at %s", path)
        return None


def _write_cache(tariffs: list[Tariff]) -> None:
    path = _cache_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "source": f"{settings.br_analytics_base_url.rstrip('/')}/price/",
        "mode": "Разово",
        "tariffs": [asdict(t) for t in tariffs],
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _tariff_from_dict(item: dict) -> Tariff:
    return Tariff(
        name=str(item["name"]),
        messages_per_month=int(item["messages_per_month"]),
        price_rub=int(item["price_rub"]),
    )


def _parse_int(value: str | None) -> int | None:
    if not value:
        return None
    digits = re.sub(r"\D", "", value)
    return int(digits) if digits else None


async def _scrape_razovo_tariffs() -> list[Tariff]:
    from playwright.async_api import async_playwright

    url = f"{settings.br_analytics_base_url.rstrip('/')}/price/"
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=settings.playwright_headless)
        context = await browser.new_context(locale="ru-RU")
        page = await context.new_page()
        page.set_default_timeout(settings.playwright_timeout_ms)
        try:
            await page.goto(url, wait_until="domcontentloaded")
            await page.get_by_role("button", name="Разово").click()
            await page.wait_for_selector(".plan-messages-count", timeout=30_000)
            # Wait until Razovo list prices appear (Starter is ~45 500, not yearly ~31 500).
            await page.wait_for_function(
                """() => {
                    const prices = [...document.querySelectorAll('.plan-price')]
                      .map((el) => Number((el.innerText || '').replace(/\\D/g, '')))
                      .filter((n) => n > 0);
                    return prices.some((n) => n >= 40000 && n <= 60000);
                }""",
                timeout=15_000,
            )
            await page.wait_for_timeout(500)
            raw_plans = await page.evaluate(
                """() => [...document.querySelectorAll('.plan-messages')].map((el) => {
                    let card = el.parentElement;
                    for (let i = 0; i < 8 && card; i++) {
                      if (card.querySelector('h2') && card.querySelector('.plan-price')) break;
                      card = card.parentElement;
                    }
                    return {
                      name: card?.querySelector('h2')?.innerText?.trim() || '',
                      price: card?.querySelector('.plan-price')?.innerText?.trim() || '',
                      messages: el.querySelector('.plan-messages-count')?.innerText?.trim() || '',
                    };
                })"""
            )
        finally:
            await context.close()
            await browser.close()

    tariffs: list[Tariff] = []
    for item in raw_plans or []:
        name = (item.get("name") or "").strip()
        price = _parse_int(item.get("price"))
        messages = _parse_int(item.get("messages"))
        if not name or price is None or messages is None:
            continue
        # Skip open-ended premium "от N" packages for auto-quoting.
        if "премиум" in name.lower():
            continue
        tariffs.append(Tariff(name=name, messages_per_month=messages, price_rub=price))

    tariffs.sort(key=lambda t: t.messages_per_month)
    if not _looks_like_razovo(tariffs):
        logger.warning("Scraped tariffs do not look like Razovo prices: %s", tariffs)
        return []
    return tariffs


def _looks_like_razovo(tariffs: list[Tariff]) -> bool:
    """Reject yearly/regular discounted prices accidentally scraped from the price page."""
    if not tariffs:
        return False
    starter = next((t for t in tariffs if "стартовый" in t.name.lower() and "плюс" not in t.name.lower()), None)
    if starter is None:
        starter = tariffs[0]
    # Razovo Starter is ~45 500; regular yearly is ~31 500.
    return starter.price_rub >= 40_000

