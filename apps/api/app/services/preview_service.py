from app.schemas.preview import PreviewResponse
from app.services.br_analytics.client import BrAnalyticsClient


class PreviewService:
    async def search(self, query: str) -> PreviewResponse:
        client = BrAnalyticsClient()
        items = await client.search_mentions(query)
        return PreviewResponse(query=query, total=len(items), items=items)
