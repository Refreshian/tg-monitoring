"""Tests for preview sample selection (VK preference, shuffle)."""

from app.schemas.preview import MentionItem
from app.services.preview_sample_selection import (
    EMAIL_SAMPLE_COUNT,
    is_vk_item,
    pick_delivery_items,
    pick_teaser_items,
)


def _item(source: str, url: str | None = None, text: str = "msg") -> MentionItem:
    return MentionItem(source=source, text=text, url=url)


def test_is_vk_item_by_url() -> None:
    assert is_vk_item(_item("blog", "https://vk.com/wall123"))
    assert is_vk_item(_item("blog", "https://m.vk.com/wall123"))
    assert not is_vk_item(_item("blog", "https://example.com/post"))


def test_pick_teasers_prefers_vk() -> None:
    pool = [
        _item("СМИ", "https://news.ru/a"),
        _item("ВКонтакте", "https://vk.com/wall1"),
        _item("СМИ", "https://news.ru/b"),
        _item("vk", "https://vk.com/wall2"),
    ]
    teasers = pick_teaser_items(pool, count=3)
    assert len(teasers) == 3
    assert is_vk_item(teasers[0])
    assert is_vk_item(teasers[1])
    assert teasers[2].url == "https://news.ru/a"


def test_pick_delivery_shuffled_not_ba_order() -> None:
    pool = [_item(f"src{i}", f"https://example.com/{i}", text=f"t{i}") for i in range(15)]
    # Fixed seed would help but we check shuffle property: not always same order
    results = [pick_delivery_items(pool, EMAIL_SAMPLE_COUNT) for _ in range(20)]
    orders = [tuple(i.url for i in r) for r in results]
    assert len(set(orders)) > 1
    assert all(len(r) == EMAIL_SAMPLE_COUNT for r in results)


def test_pick_delivery_vk_majority_when_available() -> None:
    pool = [
        _item("СМИ", "https://news.ru/a"),
        _item("vk", "https://vk.com/1"),
        _item("vk", "https://vk.com/2"),
        _item("vk", "https://vk.com/3"),
        _item("vk", "https://vk.com/4"),
        _item("vk", "https://vk.com/5"),
        _item("vk", "https://vk.com/6"),
        _item("vk", "https://vk.com/7"),
        _item("vk", "https://vk.com/8"),
        _item("vk", "https://vk.com/9"),
        _item("vk", "https://vk.com/10"),
        _item("vk", "https://vk.com/11"),
    ]
    delivery = pick_delivery_items(pool, EMAIL_SAMPLE_COUNT)
    assert len(delivery) == EMAIL_SAMPLE_COUNT
    assert sum(1 for i in delivery if is_vk_item(i)) == EMAIL_SAMPLE_COUNT
