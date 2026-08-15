"""Browser automation for brandanalytics.ru."""

from app.schemas.preview import MentionItem
from app.services.br_analytics.auth import BrAnalyticsAuth
from app.services.br_analytics.parser import parse_search_results
from app.services.br_analytics.search import BrAnalyticsSearch
from app.services.br_analytics.topics import BrAnalyticsTopics


class BrAnalyticsClient:
    """
    High-level client that:
    1. Logs into brandanalytics.ru
    2. Creates a new theme or edits fallback theme when slots are full
    3. Inserts the user search query and clicks "Показать результаты"
    4. Parses mention cards from the preview feed
    """

    async def search_mentions(self, query: str) -> list[MentionItem]:
        auth = BrAnalyticsAuth()
        topics = BrAnalyticsTopics()
        search = BrAnalyticsSearch()

        async with auth.session() as page:
            await auth.login(page)
            await topics.open_preview_theme(page)
            html = await search.run_query(page, query)
            return parse_search_results(html)
