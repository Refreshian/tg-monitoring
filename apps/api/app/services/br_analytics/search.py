import logging
import re

from playwright.async_api import Page, TimeoutError as PlaywrightTimeoutError

from app.core.config import settings

logger = logging.getLogger(__name__)

_READ_WEEKLY_JS = """() => {
  const blocks = [...document.querySelectorAll('#statistics .stats > div')];
  for (const block of blocks) {
    const labelEl = [...block.querySelectorAll('p')].find((p) => {
      const t = (p.innerText || '').trim().toLowerCase();
      return t.includes('недел') && !p.classList.contains('count');
    });
    if (!labelEl) continue;
    const raw = block.querySelector('p.count, .count')?.innerText || '';
    const digits = raw.replace(/\\D/g, '');
    if (digits) return Number(digits);
  }
  return null;
}"""

_SET_KEYWORDS_JS = """(el, query) => {
  el.focus();
  el.innerHTML = '';
  el.textContent = '';
  while (el.firstChild) {
    el.removeChild(el.firstChild);
  }
  el.textContent = query;
  el.dispatchEvent(new Event('input', { bubbles: true }));
  el.dispatchEvent(new Event('change', { bubbles: true }));
  return (el.innerText || el.textContent || '').trim();
}"""


def _normalize_for_compare(text: str) -> str:
    lowered = text.lower().replace("ё", "е")
    lowered = re.sub(r"[^\wа-я0-9]+", " ", lowered, flags=re.I)
    return " ".join(lowered.split())


def _keywords_acceptable(actual: str, expected: str) -> bool:
    actual_norm = _normalize_for_compare(actual)
    expected_norm = _normalize_for_compare(expected)
    if not expected_norm:
        return bool(actual_norm)
    # Compare word overlap: user query tokens should appear in the field.
    tokens = [t for t in expected_norm.split() if len(t) >= 3]
    if not tokens:
        tokens = expected_norm.split()
    if not tokens:
        return True
    matched = sum(1 for token in tokens if token in actual_norm)
    return matched >= max(1, len(tokens) // 2)


class BrAnalyticsSearch:
    async def run_query(self, page: Page, query: str) -> tuple[str, str, int | None]:
        """
        Paste the search query into Brand Analytics keywords field,
        confirm keyword-check dialog if shown, click "Показать результаты",
        return (results HTML, statistics HTML, weekly count or None).
        """
        keywords = page.locator("#key_words_operator")
        await keywords.wait_for(state="visible")

        # Theme editor loads saved keywords asynchronously — wait, then replace.
        try:
            await page.wait_for_function(
                """() => {
                    const el = document.getElementById('key_words_operator');
                    return el && (el.innerText || el.textContent || '').trim().length > 0;
                }""",
                timeout=15_000,
            )
        except PlaywrightTimeoutError:
            pass

        before = (await keywords.inner_text()).strip()
        if before:
            logger.info("BA keywords before replace: %r", before[:120])

        await self._replace_keywords(page, keywords, query)
        await self._confirm_keywords_dialog(page)

        actual = (await keywords.inner_text()).strip()
        if not _keywords_acceptable(actual, query):
            logger.warning(
                "BA keywords mismatch after replace: expected %r, got %r",
                query[:120],
                actual[:120],
            )
            await self._replace_keywords(page, keywords, query, force_keyboard=True)
            await self._confirm_keywords_dialog(page)
            actual = (await keywords.inner_text()).strip()
            if not _keywords_acceptable(actual, query):
                raise RuntimeError(
                    f"Failed to set preview keywords. Field contains: {actual!r}"
                )

        logger.info("BA keywords for preview: %r", actual[:160])

        show_results = page.locator("#show_result_btn")
        await show_results.wait_for(state="visible")
        await show_results.click()

        # Dialog may reappear when starting preview search
        await self._confirm_keywords_dialog(page)

        processing = page.locator(".js--processing_box")
        try:
            await processing.wait_for(state="visible", timeout=5_000)
        except PlaywrightTimeoutError:
            pass

        try:
            await page.wait_for_function(
                """() => {
                    const el = document.getElementById('search_content');
                    if (!el) return false;
                    const style = window.getComputedStyle(el);
                    if (style.display === 'none' || style.visibility === 'hidden') return false;
                    const total = el.querySelector('.total_title');
                    const items = el.querySelectorAll('.feed_item');
                    return Boolean(total) || items.length > 0;
                }""",
                timeout=settings.playwright_timeout_ms,
            )
        except PlaywrightTimeoutError:
            await page.screenshot(path="preview_debug.png", full_page=True)
            keywords_text = await keywords.inner_text()
            raise RuntimeError(
                "Brand Analytics preview did not return results. "
                f"Keywords field value was: {keywords_text!r}. "
                "Screenshot saved to preview_debug.png"
            ) from None

        # Wait until right-hand "За неделю" shows a numeric count.
        try:
            await page.wait_for_function(
                f"() => {{ const v = ({_READ_WEEKLY_JS})(); return v != null; }}",
                timeout=30_000,
            )
        except PlaywrightTimeoutError:
            pass

        weekly_count: int | None = None
        stats_html = ""
        results_html = await page.locator("#search_content").inner_html()
        for _ in range(8):
            stats = page.locator("#statistics")
            if await stats.count() > 0:
                try:
                    stats_html = await stats.inner_html()
                except PlaywrightTimeoutError:
                    stats_html = ""
            weekly_count = await self._read_weekly_count(page)
            if weekly_count is not None:
                break
            await page.wait_for_timeout(700)

        return results_html, stats_html, weekly_count

    async def _replace_keywords(
        self,
        page: Page,
        keywords,
        query: str,
        *,
        force_keyboard: bool = False,
    ) -> None:
        await keywords.click()
        await keywords.evaluate(_SET_KEYWORDS_JS, query)

        if force_keyboard:
            await keywords.click()
            await page.keyboard.press("Control+A")
            await page.keyboard.press("Backspace")
            await page.keyboard.insert_text(query)
            await page.keyboard.press("Tab")
        else:
            await page.keyboard.press("Tab")

    async def _read_weekly_count(self, page: Page) -> int | None:
        """Read only the right-hand stats value labeled 'За неделю'."""
        try:
            value = await page.evaluate(_READ_WEEKLY_JS)
        except Exception:  # noqa: BLE001
            return None
        if isinstance(value, (int, float)) and value >= 0:
            return int(value)
        return None

    async def _confirm_keywords_dialog(self, page: Page) -> None:
        """Accept 'Проверка ключевых фраз' modal if Brand Analytics shows it."""
        title = page.get_by_text("Проверка ключевых фраз", exact=False)
        try:
            await title.first.wait_for(state="visible", timeout=4_000)
        except PlaywrightTimeoutError:
            return

        dialog = title.first.locator(
            "xpath=ancestor::div[contains(@class,'ui-dialog') or contains(@class,'dialog')][1]"
        )
        save = dialog.get_by_role("button", name="Сохранить")
        if await save.count() == 0:
            save = dialog.locator(".btn_blue, .custom_btn, button, a").filter(has_text="Сохранить")

        if await save.count() == 0:
            save = page.locator(".ui-dialog:visible, .dialog-window:visible").get_by_text(
                "Сохранить", exact=True
            )

        await save.first.click()
        try:
            await title.first.wait_for(state="hidden", timeout=10_000)
        except PlaywrightTimeoutError:
            pass
