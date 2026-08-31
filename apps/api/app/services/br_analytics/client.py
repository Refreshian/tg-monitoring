"""Browser automation for brandanalytics.ru."""

from dataclasses import dataclass

from app.services.br_analytics.auth import BrAnalyticsAuth
from app.services.br_analytics.parser import parse_weekly_count
from app.services.br_analytics.search import BrAnalyticsSearch
from app.services.br_analytics.topics import BrAnalyticsTopics


@dataclass
class PreviewSearchResult:
    weekly_count: int | None = None


class BrAnalyticsClient:
    """
    High-level client that:
    1. Logs into brandanalytics.ru
    2. Opens the measurement theme editor (fallback theme «Энергострой»)
    3. Inserts the user search query and clicks "Показать результаты"
    4. Reads weekly volume from the preview panel (snippets are not scraped for public use)
    """

    async def search_mentions(self, query: str) -> PreviewSearchResult:
        auth = BrAnalyticsAuth()
        topics = BrAnalyticsTopics()
        search = BrAnalyticsSearch()

        async with auth.session() as page:
            await auth.login(page)
            await topics.open_preview_theme(page)
            results_html, stats_html, weekly_from_page = await search.run_query(page, query)
            weekly = (
                weekly_from_page
                or parse_weekly_count(stats_html)
                or parse_weekly_count(results_html)
            )
            return PreviewSearchResult(weekly_count=weekly)
