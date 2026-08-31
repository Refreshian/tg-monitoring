"""List BA themes with IDs from summary page (one-off helper)."""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from playwright.async_api import async_playwright

from app.core.config import settings


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
        await page.wait_for_selector("#username", state="detached", timeout=settings.playwright_timeout_ms)
        await page.goto(settings.summary_url, wait_until="domcontentloaded")
        try:
            await page.locator('[data-testid="themes-create"]').first.wait_for(state="visible", timeout=30000)
        except Exception as exc:
            print("themes-create wait failed:", exc)
        await page.wait_for_timeout(2000)
        print("url:", page.url)
        testids = await page.evaluate(
            """() => [...document.querySelectorAll('[data-testid^=\"theme-edit-\"]')].map((el) => ({
                testid: el.getAttribute('data-testid'),
                text: (el.closest('tr')?.innerText || el.parentElement?.innerText || '').slice(0, 100).replace(/\s+/g, ' '),
            }))"""
        )
        print("theme-edit count:", len(testids))
        for item in testids:
            print(item)
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
