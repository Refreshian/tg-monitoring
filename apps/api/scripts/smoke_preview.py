import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.services.br_analytics.client import BrAnalyticsClient


async def main() -> None:
    query = "creativityweek"
    print(f"Running preview for: {query}")
    result = await BrAnalyticsClient().search_mentions(query)
    print(f"weekly_count={result.weekly_count}")


if __name__ == "__main__":
    asyncio.run(main())
