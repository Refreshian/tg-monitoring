"""Inspect BA keywords editor DOM structure."""

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

        await page.goto(settings.login_url)
        await page.fill("#username", settings.br_analytics_login)
        await page.fill("#ba_password", settings.br_analytics_password)
        await page.click("#button_submit")
        await page.wait_for_selector("#username", state="detached")
        await page.goto(settings.fallback_theme_edit_url)
        await page.locator("#key_words_operator").wait_for(state="visible")
        await page.wait_for_timeout(2000)

        info = await page.evaluate(
            """() => {
                const el = document.getElementById('key_words_operator');
                const parent = el?.parentElement;
                const hidden = [...document.querySelectorAll('input[type=hidden], textarea')]
                  .filter((n) => (n.id || '').includes('key') || (n.name || '').includes('key'))
                  .map((n) => ({ id: n.id, name: n.name, value: (n.value || '').slice(0, 120) }));
                return {
                    tag: el?.tagName,
                    className: el?.className,
                    contentEditable: el?.isContentEditable,
                    innerHTML: (el?.innerHTML || '').slice(0, 300),
                    innerText: (el?.innerText || '').slice(0, 200),
                    parentClass: parent?.className,
                    hidden,
                };
            }"""
        )
        print(info)

        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
