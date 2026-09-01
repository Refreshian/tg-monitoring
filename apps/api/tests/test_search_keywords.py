"""Tests for BA keyword field normalization and weekly fallback."""

from app.services.br_analytics.search import (
    BrAnalyticsSearch,
    _keywords_acceptable,
    _normalize_for_compare,
)


def test_normalize_for_compare() -> None:
    assert _normalize_for_compare('"Энергострой"') == "энергострой"


def test_keywords_acceptable_overlap() -> None:
    assert _keywords_acceptable('"Ромашка" OR ромашка', "Ромашка")
    assert not _keywords_acceptable('Энергострой, "Александр Тевис"~0', "Ромашка")


def test_weekly_from_total_title() -> None:
    search = BrAnalyticsSearch()
    html = "<div class='total_title'>Найдено 1&nbsp;886 сообщений за 2 дня</div>"
    weekly = search._weekly_from_total_title(html)
    assert weekly == 6601  # 1886/2*7

