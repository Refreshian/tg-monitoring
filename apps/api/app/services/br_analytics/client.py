"""Browser automation for brandanalytics.ru."""

from dataclasses import dataclass

from app.schemas.preview import MentionItem
from app.services.br_analytics.auth import BrAnalyticsAuth
from app.services.br_analytics.parser import parse_search_results, parse_weekly_count
from app.services.br_analytics.search import BrAnalyticsSearch
from app.services.br_analytics.topics import BrAnalyticsTopics


@dataclass
class PreviewSearchResult:
    items: list[MentionItem]
    weekly_count: int | None = None


class BrAnalyticsClient:
    """
    High-level client that:
    1. Logs into brandanalytics.ru
    2. Creates a new theme or edits fallback theme when slots are full
    3. Inserts the user search query and clicks "Показать результаты"
    4. Parses mention cards and weekly volume from the preview panel
    """

    async def search_mentions(self, query: str) -> PreviewSearchResult:
        auth = BrAnalyticsAuth()
        topics = BrAnalyticsTopics()
        search = BrAnalyticsSearch()

        async with auth.session() as page:
            await auth.login(page)
            await topics.open_preview_theme(page)
            results_html, stats_html, weekly_from_page = await search.run_query(page, query)
            items = parse_search_results(results_html)
            weekly = (
                weekly_from_page
                or parse_weekly_count(stats_html)
                or parse_weekly_count(results_html)
            )
            return PreviewSearchResult(items=items, weekly_count=weekly)
