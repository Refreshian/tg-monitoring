import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.services.br_analytics.client import BrAnalyticsClient


async def main() -> None:
    query = "creativityweek"
    print(f"Running preview for: {query}")
    items = await BrAnalyticsClient().search_mentions(query)
    print(f"Got {len(items)} items")
    for item in items[:5]:
        print("---")
        print(item.source, item.published_at)
        print(item.title)
        print((item.text or "")[:200])
        print(item.url)


if __name__ == "__main__":
    asyncio.run(main())
