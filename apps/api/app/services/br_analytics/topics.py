from playwright.async_api import Page

from app.core.config import settings


class BrAnalyticsTopics:
    async def open_preview_theme(self, page: Page) -> None:
        """
        Open a theme editor for preview search.

        If "Добавить новую тему" is available (not locked), open create theme.
        Otherwise edit the fallback theme ("Российская креативная неделя").
        """
        await page.goto(settings.summary_url, wait_until="domcontentloaded")
        create_button = page.locator('[data-testid="themes-create"]').first
        await create_button.wait_for(state="visible")

        classes = (await create_button.get_attribute("class")) or ""
        if "lock" in classes.split():
            await self._open_fallback_theme(page)
            return

        await create_button.click()
        await page.wait_for_url("**/action/create_theme/**", timeout=settings.playwright_timeout_ms)
        await page.locator("#key_words_operator").wait_for(state="visible")

    async def _open_fallback_theme(self, page: Page) -> None:
        theme_id = settings.br_analytics_fallback_theme_id
        edit_link = page.locator(f'[data-testid="theme-edit-{theme_id}"]')

        if await edit_link.count() == 0:
            # Fallback by theme title text if data-testid is missing
            row = page.locator("tr").filter(has_text=settings.br_analytics_fallback_theme_name)
            edit_link = row.locator("a", has_text="Редактировать")

        if await edit_link.count() == 0:
            await page.goto(settings.fallback_theme_edit_url, wait_until="domcontentloaded")
        else:
            await edit_link.first.click()

        await page.wait_for_url("**/action/update_theme/**", timeout=settings.playwright_timeout_ms)
        await page.locator("#key_words_operator").wait_for(state="visible")
