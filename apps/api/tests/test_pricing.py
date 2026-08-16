from app.services.br_analytics.parser import parse_weekly_count
from app.services.pricing import (
    DEFAULT_RAZOVO_TARIFFS,
    Tariff,
    estimate_monthly_from_weekly,
    quote_access_price,
)


def test_parse_weekly_count_from_statistics_panel() -> None:
    html = """
    <div id="statistics">
      <aside>
        <div class="stats">
          <div class="period_0"><p class="count">3</p><p>За сегодня</p></div>
          <div class="period_1"><p class="count">19</p><p>За неделю</p></div>
          <div class="period_2"><p class="count">236</p><p>За месяц</p></div>
        </div>
      </aside>
    </div>
    """
    assert parse_weekly_count(html) == 19


def test_parse_weekly_count_when_week_is_period_2() -> None:
    """Live BA UI currently uses: сегодня / вчера / неделю."""
    html = """
    <aside>
      <div class="stats">
        <div class="period_0"><p class="count">4</p><p>За сегодня</p></div>
        <div class="period_1"><p class="count">2</p><p>За вчера</p></div>
        <div class="period_2"><p class="count">77</p><p>За неделю</p></div>
      </div>
    </aside>
    """
    assert parse_weekly_count(html) == 77


def test_parse_weekly_count_with_spaced_digits() -> None:
    html = """
    <div class="stats">
      <div class="period_1"><p class="count">1 234</p><p>За неделю</p></div>
    </div>
    """
    assert parse_weekly_count(html) == 1234


def test_estimate_monthly_from_weekly() -> None:
    # 19 / 7 * 30 ≈ 81.428 → 81
    assert estimate_monthly_from_weekly(19) == 81
    assert estimate_monthly_from_weekly(0) == 0


def test_quote_picks_smallest_fitting_tariff() -> None:
    tariffs = [Tariff(**item) for item in DEFAULT_RAZOVO_TARIFFS]
    # 81 messages → Стартовый (10_000), 28% off 45500 → 32760 → 33000
    quote = quote_access_price(81, tariffs=tariffs, discount_ratio=0.28)
    assert quote is not None
    assert quote.tariff_name == "Стартовый"
    assert quote.list_price_rub == 45_500
    assert quote.quote_price_rub == 33_000
    assert quote.price_is_from is False


def test_quote_uses_next_tier_when_over_limit() -> None:
    tariffs = [Tariff(**item) for item in DEFAULT_RAZOVO_TARIFFS]
    quote = quote_access_price(12_000, tariffs=tariffs, discount_ratio=0.28)
    assert quote is not None
    assert quote.tariff_name == "Стартовый плюс"
    assert quote.list_price_rub == 68_900


def test_quote_marks_from_when_above_max_tier() -> None:
    tariffs = [Tariff(**item) for item in DEFAULT_RAZOVO_TARIFFS]
    quote = quote_access_price(600_000, tariffs=tariffs, discount_ratio=0.28)
    assert quote is not None
    assert quote.tariff_name == "Расширенный"
    assert quote.price_is_from is True
