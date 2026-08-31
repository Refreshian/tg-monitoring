"""Browser automation for brandanalytics.ru."""

from dataclasses import dataclass, field

from app.schemas.preview import MentionItem
from app.services.br_analytics.auth import BrAnalyticsAuth
from app.services.br_analytics.parser import parse_search_results, parse_weekly_count
from app.services.br_analytics.search import BrAnalyticsSearch
from app.services.br_analytics.topics import BrAnalyticsTopics
from app.services.preview_sample_selection import PARSE_POOL_LIMIT


@dataclass
class PreviewSearchResult:
    weekly_count: int | None = None
    sample_items: list[MentionItem] = field(default_factory=list)


class BrAnalyticsClient:
    """
    High-level client that:
    1. Logs into brandanalytics.ru
    2. Opens the measurement theme editor (fallback theme «Энергострой»)
    3. Inserts the user search query and clicks "Показать результаты"
    4. Reads weekly volume and parses a pool of snippets for private delivery
    """

    async def search_mentions(self, query: str) -> PreviewSearchResult:
        auth = BrAnalyticsAuth()
        topics = BrAnalyticsTopics()
        search = BrAnalyticsSearch()

        async with auth.session() as page:
            await auth.login(page)
            await topics.open_preview_theme(page)
            results_html, stats_html, weekly_from_page = await search.run_query(page, query)
            items = parse_search_results(results_html)[:PARSE_POOL_LIMIT]
            weekly = (
                weekly_from_page
                or parse_weekly_count(stats_html)
                or parse_weekly_count(results_html)
            )
            return PreviewSearchResult(weekly_count=weekly, sample_items=items)
