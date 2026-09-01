"""Test keyboard-only keyword replacement."""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from playwright.async_api import async_playwright

from app.core.config import settings
from app.services.br_analytics.parser import parse_search_results
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

        html_inner = await keywords.evaluate("el => el.innerHTML")
        print("innerHTML:", html_inner[:300])

        await page.locator("#show_result_btn").click()
        await search._confirm_keywords_dialog(page)

        await page.wait_for_timeout(5000)
        total = await page.evaluate(
            "() => document.querySelector('#search_content .total_title')?.innerText"
        )
        items = parse_search_results(await page.locator("#search_content").inner_html())
        print("total:", total)
        print("items:", len(items))
        if items:
            print("first:", items[0].text[:100])

        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
