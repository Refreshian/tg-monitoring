import logging

from playwright.async_api import Page

from app.core.config import settings

logger = logging.getLogger(__name__)


class BrAnalyticsTopics:
    async def open_preview_theme(self, page: Page) -> None:
        """
        Open a theme editor for preview search.

        Prefer the configured measurement theme (e.g. «Энергострой»). If it was removed
        from the account, create a new theme via «Добавить новую тему» on the summary page.
        """
        await page.goto(settings.summary_url, wait_until="domcontentloaded")
        create_button = page.locator('[data-testid="themes-create"]').first
        await create_button.wait_for(state="visible")

        edit_link = await self._find_measurement_theme_edit_link(page)
        if edit_link is not None:
            logger.info(
                "Opening measurement theme %s (%s) for preview",
                settings.br_analytics_fallback_theme_name,
                settings.br_analytics_fallback_theme_id,
            )
            await edit_link.click()
            await page.wait_for_url("**/action/update_theme/**", timeout=settings.playwright_timeout_ms)
            await page.locator("#key_words_operator").wait_for(state="visible")
            return

        logger.warning(
            "Measurement theme %s not found; creating a new theme for preview",
            settings.br_analytics_fallback_theme_name,
        )
        await self._open_create_theme(page)

    async def _find_measurement_theme_edit_link(self, page: Page):
        theme_id = settings.br_analytics_fallback_theme_id
        theme_name = settings.br_analytics_fallback_theme_name
        edit_link = page.locator(f'[data-testid="theme-edit-{theme_id}"]')

        if await edit_link.count() > 0:
            return edit_link.first

        row = page.locator("tr").filter(has_text=theme_name)
        if await row.count() > 0:
            link = row.locator("a", has_text="Редактировать")
            if await link.count() > 0:
                return link.first

        return None

    async def _open_create_theme(self, page: Page) -> None:
        create_button = page.locator('[data-testid="themes-create"]').first
        classes = (await create_button.get_attribute("class")) or ""
        if "lock" in classes.split():
            raise RuntimeError(
                f"Тема «{settings.br_analytics_fallback_theme_name}» не найдена, "
                "и создание новой темы недоступно (нет свободных слотов в Brand Analytics)."
            )

        await create_button.click()
        await page.wait_for_url("**/action/create_theme/**", timeout=settings.playwright_timeout_ms)
        await page.locator("#key_words_operator").wait_for(state="visible")
