import asyncio
import logging

from app.schemas.preview import PreviewResponse
from app.services.br_analytics.client import BrAnalyticsClient
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

        estimated_price_rub: int | None = None
        price_is_from = False
        weekly = result.weekly_count
        monthly = estimate_monthly_from_weekly(weekly) if weekly else None
        if weekly is not None and weekly > 0:
            tariffs = await ensure_fresh_tariffs()
            quote = quote_access_price(monthly or 0, tariffs=tariffs)
            if quote is not None:
                estimated_price_rub = quote.quote_price_rub
                price_is_from = quote.price_is_from

        logger.info(
            "preview original=%r query=%r changed=%s items=%s weekly=%s monthly=%s price=%s",
            rewrite.original_query,
            search_query,
            rewrite.changed,
            len(result.items),
            weekly,
            monthly,
            estimated_price_rub,
        )

        return PreviewResponse(
            query=search_query,
            original_query=rewrite.original_query,
            query_changed=rewrite.changed,
            query_note=rewrite.note or None,
            total=len(result.items),
            items=result.items,
            estimated_price_rub=estimated_price_rub,
            price_is_from=price_is_from,
        )
