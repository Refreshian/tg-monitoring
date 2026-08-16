import re
from datetime import datetime

from bs4 import BeautifulSoup

from app.schemas.preview import MentionItem


def parse_search_results(html: str) -> list[MentionItem]:
    """Parse Brand Analytics preview feed (#search_content / #messages_container)."""
    soup = BeautifulSoup(html, "html.parser")
    items: list[MentionItem] = []

    for feed_item in soup.select(".feed_item"):
        text_node = feed_item.select_one(".msg_text div") or feed_item.select_one(".msg_text")
        text = text_node.get_text(" ", strip=True) if text_node else ""
        if not text:
            continue

        source_link = feed_item.select_one("a.js--source_link")
        author = feed_item.select_one("a.author_name")
        date_node = feed_item.select_one(".msg_date")

        source = ""
        if source_link:
            source = source_link.get_text(strip=True)
        if not source and author:
            source = author.get_text(strip=True)
        if not source:
            source = "unknown"

        title = author.get_text(strip=True) if author else None
        url = source_link.get("href") if source_link else None
        if isinstance(url, list):
            url = url[0] if url else None

        published_at = _parse_ba_date(date_node.get_text(strip=True) if date_node else "")

        items.append(
            MentionItem(
                source=source,
                title=title,
                text=text,
                url=url,
                published_at=published_at,
            )
        )

    return items


def parse_weekly_count(html: str) -> int | None:
    """
    Extract the 'За неделю' value from BA's right-hand statistics panel
    (#statistics .stats .period_1 or label match).
    """
    soup = BeautifulSoup(html, "html.parser")
    stats = soup.select_one("#statistics .stats") or soup.select_one(".stats")
    if not stats:
        return None

    # Prefer label match: BA may put "За неделю" in period_1 or period_2 depending on UI.
    for block in stats.find_all("div", recursive=False):
        labels = [p.get_text(" ", strip=True).lower() for p in block.find_all("p")]
        if any("недел" in label for label in labels):
            count_node = block.select_one(".count")
            if count_node:
                return _parse_count_text(count_node.get_text())

    return None


def _parse_count_text(value: str) -> int | None:
    digits = re.sub(r"\D", "", value or "")
    return int(digits) if digits else None


def _parse_ba_date(value: str) -> datetime | None:
    if not value:
        return None
    for fmt in ("%d.%m.%Y %H:%M", "%d.%m.%Y"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    return None
