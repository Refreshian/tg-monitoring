"""Debug BA keyword replacement on theme editor."""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from playwright.async_api import async_playwright

from app.core.config import settings
from app.services.br_analytics.search import BrAnalyticsSearch


QUERY = '"Сидни Суини"~1'


async def main() -> None:
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=True)
        context = await browser.new_context(locale="ru-RU")
        page = await context.new_page()
        page.set_default_timeout(settings.playwright_timeout_ms)

        await page.goto(settings.login_url, wait_until="domcontentloaded")
        await page.fill("#username", settings.br_analytics_login)
        await page.fill("#ba_password", settings.br_analytics_password)
        await page.click("#button_submit")
        await page.wait_for_selector("#username", state="detached")

        await page.goto(settings.fallback_theme_edit_url, wait_until="domcontentloaded")
        await page.locator("#key_words_operator").wait_for(state="visible")
        await page.wait_for_timeout(2000)

        keywords = page.locator("#key_words_operator")
        before = await keywords.inner_text()
        print("BEFORE:", repr(before[:200]))

        search = BrAnalyticsSearch()
        results_html, stats_html, weekly = await search.run_query(page, QUERY)

        after = await keywords.inner_text()
        print("AFTER:", repr(after[:200]))
        print("WEEKLY:", weekly)

        items = results_html.count("feed_item")
        print("feed_item mentions in html (rough):", results_html.count("feed_item"))

        await page.screenshot(path="preview_debug_after.png", full_page=True)
        print("screenshot: preview_debug_after.png")

        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
