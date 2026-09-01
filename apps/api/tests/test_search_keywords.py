"""Tests for BA keyword field normalization."""

from app.services.br_analytics.search import _keywords_acceptable, _normalize_for_compare


def test_normalize_for_compare() -> None:
    assert _normalize_for_compare('"Энергострой"') == "энергострой"


def test_keywords_acceptable_overlap() -> None:
    assert _keywords_acceptable('"Ромашка" OR ромашка', "Ромашка")
    assert not _keywords_acceptable('Энергострой, "Александр Тевис"~0', "Ромашка")

