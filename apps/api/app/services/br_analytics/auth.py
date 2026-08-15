from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from playwright.async_api import Browser, Page, async_playwright

from app.core.config import settings


class BrAnalyticsAuth:
    @asynccontextmanager
    async def session(self) -> AsyncIterator[Page]:
        async with async_playwright() as playwright:
            browser: Browser = await playwright.chromium.launch(headless=settings.playwright_headless)
            context = await browser.new_context(locale="ru-RU")
            page = await context.new_page()
            page.set_default_timeout(settings.playwright_timeout_ms)
            try:
                yield page
            finally:
                await context.close()
                await browser.close()

    async def login(self, page: Page) -> None:
        if not settings.br_analytics_login or not settings.br_analytics_password:
            raise RuntimeError("BR_ANALYTICS_LOGIN and BR_ANALYTICS_PASSWORD must be set in .env")

        await page.goto(settings.login_url, wait_until="domcontentloaded")
        await page.fill("#username", settings.br_analytics_login)
        await page.fill("#ba_password", settings.br_analytics_password)
        await page.click("#button_submit")
        # Successful login leaves the login form
        await page.wait_for_selector("#username", state="detached", timeout=settings.playwright_timeout_ms)
