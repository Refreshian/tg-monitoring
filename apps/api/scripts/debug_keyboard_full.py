"""Full keyboard keyword flow with show results wait."""

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
        keywords = page.locator("#key_words_operator")
        await keywords.wait_for(state="visible")
        await page.wait_for_timeout(2000)

        await keywords.click()
        await page.keyboard.press("Control+A")
        await page.keyboard.press("Backspace")
        await page.keyboard.type(QUERY, delay=25)
        await page.keyboard.press("Tab")

        search = BrAnalyticsSearch()
        await search._confirm_keywords_dialog(page)

        print("innerHTML:", (await keywords.evaluate("el => el.innerHTML"))[:300])

        await page.locator("#show_result_btn").click()
        await search._confirm_keywords_dialog(page)

        await page.wait_for_function(
            """() => {
                const el = document.getElementById('search_content');
                if (!el) return false;
                const total = el.querySelector('.total_title');
                const items = el.querySelectorAll('.feed_item');
                return Boolean(total) || items.length > 0;
            }""",
            timeout=90000,
        )

        html = await page.locator("#search_content").inner_html()
        stats = await page.locator("#statistics").inner_html()
        total = await page.evaluate(
            "() => document.querySelector('#search_content .total_title')?.innerText"
        )
        items = parse_search_results(html)
        weekly = parse_weekly_count(stats)
        print("total:", total)
        print("weekly:", weekly)
        print("items:", len(items))
        for i, it in enumerate(items[:3]):
            print(i, (it.text or "")[:100])

        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
