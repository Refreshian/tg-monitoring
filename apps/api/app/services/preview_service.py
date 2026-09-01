import asyncio
import logging

from app.schemas.preview import PreviewResponse
from app.services.br_analytics.client import BrAnalyticsClient
from app.services.preview_samples_cache import get_bundle, store_samples
from app.services.pricing import (
    ensure_fresh_tariffs,
    estimate_monthly_from_weekly,
    quote_access_price,
)
from app.services.query_rewrite_service import QueryRewriteService

logger = logging.getLogger("uvicorn.error")

# Brand Analytics preview edits one shared theme — serialize searches.
_preview_lock = asyncio.Lock()


class PreviewService:
    async def search(self, query: str) -> PreviewResponse:
        rewrite = await QueryRewriteService().rewrite(query)
        search_query = rewrite.query

        async with _preview_lock:
            client = BrAnalyticsClient()
            result = await client.search_mentions(search_query)

        sample_token = store_samples(search_query, result.sample_items)
        bundle = get_bundle(sample_token) if sample_token else None

        estimated_price_rub: int | None = None
        price_is_from = False
        tariff_name: str | None = None
        weekly = result.weekly_count
        monthly = estimate_monthly_from_weekly(weekly) if weekly is not None else None
        if weekly is not None and weekly > 0 and monthly is not None:
            tariffs = await ensure_fresh_tariffs()
            quote = quote_access_price(monthly, tariffs=tariffs)
            if quote is not None:
                estimated_price_rub = quote.quote_price_rub
                price_is_from = quote.price_is_from
                tariff_name = quote.tariff_name

        logger.info(
            "preview original=%r query=%r changed=%s weekly=%s monthly=%s price=%s "
            "samples=%s token=%s",
            rewrite.original_query,
            search_query,
            rewrite.changed,
            weekly,
            monthly,
            estimated_price_rub,
            len(result.sample_items),
            sample_token,
        )

        return PreviewResponse(
            query=search_query,
            original_query=rewrite.original_query,
            query_changed=rewrite.changed,
            query_note=rewrite.note or None,
            weekly_count=weekly,
            estimated_monthly_messages=monthly,
            estimated_price_rub=estimated_price_rub,
            price_is_from=price_is_from,
            tariff_name=tariff_name,
            sample_token=sample_token,
            samples_available=sample_token is not None,
            teasers=bundle.teasers() if bundle else [],
            total=0,
            items=[],
        )

    def get_samples_by_token(self, token: str):
        return get_bundle(token)
