"""Debug BA preview totals vs weekly stats."""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from playwright.async_api import async_playwright

from app.core.config import settings
from app.services.br_analytics.parser import parse_search_results, parse_weekly_count
from app.services.br_analytics.search import BrAnalyticsSearch

QUERY = '"Сидни Суини"~1'


async def main() -> None:
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=True)
        context = await browser.new_context(locale="ru-RU")
        page = await context.new_page()
        page.set_default_timeout(settings.playwright_timeout_ms)

        await page.goto(settings.login_url)
        await page.fill("#username", settings.br_analytics_login)
        await page.fill("#ba_password", settings.br_analytics_password)
        await page.click("#button_submit")
        await page.wait_for_selector("#username", state="detached")
        await page.goto(settings.fallback_theme_edit_url)
        await page.locator("#key_words_operator").wait_for(state="visible")
        await page.wait_for_timeout(2000)

        search = BrAnalyticsSearch()
        html, stats, weekly = await search.run_query(page, QUERY)

        total_text = await page.evaluate(
            """() => {
                const el = document.querySelector('#search_content .total_title');
                return el ? el.innerText : null;
            }"""
        )
        stats_text = await page.evaluate(
            """() => {
                const el = document.querySelector('#statistics');
                return el ? el.innerText.slice(0, 600) : null;
            }"""
        )
        items = parse_search_results(html)
        weekly_parsed = parse_weekly_count(stats)
        print("weekly_from_search:", weekly)
        print("weekly_parsed:", weekly_parsed)
        print("total_title:", total_text)
        print("stats_text:", stats_text)
        print("items:", len(items))
        for index, item in enumerate(items[:3]):
            print("---", index, item.source, (item.text or "")[:120])

        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
