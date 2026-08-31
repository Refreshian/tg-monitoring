from playwright.async_api import Page

from app.core.config import settings


class BrAnalyticsTopics:
    async def open_preview_theme(self, page: Page) -> None:
        """
        Open the configured measurement theme editor for preview search.

        Always edits the fallback theme (e.g. «Энергострой») so preview does not depend
        on free theme slots or themes that may be removed from the account.
        """
        await page.goto(settings.summary_url, wait_until="domcontentloaded")
        await page.locator('[data-testid="themes-create"]').first.wait_for(state="visible")
        await self._open_measurement_theme(page)

    async def _open_measurement_theme(self, page: Page) -> None:
        theme_id = settings.br_analytics_fallback_theme_id
        theme_name = settings.br_analytics_fallback_theme_name
        edit_link = page.locator(f'[data-testid="theme-edit-{theme_id}"]')

        if await edit_link.count() == 0:
            row = page.locator("tr").filter(has_text=theme_name)
            edit_link = row.locator("a", has_text="Редактировать")

        if await edit_link.count() == 0:
            await page.goto(settings.fallback_theme_edit_url, wait_until="domcontentloaded")
        else:
            await edit_link.first.click()

        await page.wait_for_url("**/action/update_theme/**", timeout=settings.playwright_timeout_ms)
        await page.locator("#key_words_operator").wait_for(state="visible")
