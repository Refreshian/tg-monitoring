from pathlib import Path

from app.services.br_analytics.parser import parse_search_results


def test_parse_saved_edit_theme_results() -> None:
    html_path = Path(r"c:\Users\alex\Documents\edit_theme.html")
    if not html_path.exists():
        # CI / machines without the local BA dump skip this fixture-based test
        return

    html = html_path.read_text(encoding="utf-8", errors="ignore")
    # Isolate results block like Playwright returns from #search_content
    start = html.find('id="search_content"')
    assert start > 0
    fragment = html[start : start + 200_000]

    items = parse_search_results(fragment)
    assert len(items) > 0
    assert items[0].text
    assert items[0].source
