from app.schemas.preview import PreviewResponse
from app.services.br_analytics.client import BrAnalyticsClient
from app.services.pricing import (
    ensure_fresh_tariffs,
    estimate_monthly_from_weekly,
    quote_access_price,
)


class PreviewService:
    async def search(self, query: str) -> PreviewResponse:
        client = BrAnalyticsClient()
        result = await client.search_mentions(query)

        estimated_price_rub: int | None = None
        price_is_from = False
        if result.weekly_count is not None and result.weekly_count > 0:
            monthly = estimate_monthly_from_weekly(result.weekly_count)
            tariffs = await ensure_fresh_tariffs()
            quote = quote_access_price(monthly, tariffs=tariffs)
            if quote is not None:
                estimated_price_rub = quote.quote_price_rub
                price_is_from = quote.price_is_from

        return PreviewResponse(
            query=query,
            total=len(result.items),
            items=result.items,
            estimated_price_rub=estimated_price_rub,
            price_is_from=price_is_from,
        )
