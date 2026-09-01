"""Pick preview samples from BA feed: VK preference for teasers, shuffled batch for email."""

from __future__ import annotations

import random
import re

from app.schemas.preview import MentionItem

TEASER_COUNT = 3
EMAIL_SAMPLE_COUNT = 10
PARSE_POOL_LIMIT = 45

_VK_HOST_RE = re.compile(r"(?:^|//|\.)(?:vk\.com|vk\.ru|m\.vk\.com)", re.I)
_VK_LABEL_RE = re.compile(r"(?:^|\s)(vk|vkontakte|вконтакте)(?:\s|$|[.,])", re.I)


def is_vk_item(item: MentionItem) -> bool:
    url = (item.url or "").lower()
    if _VK_HOST_RE.search(url):
        return True
    label = f"{item.source} {item.title or ''}"
    return bool(_VK_LABEL_RE.search(label.lower()))


def pick_teaser_items(pool: list[MentionItem], count: int = TEASER_COUNT) -> list[MentionItem]:
    """Site teasers: prefer vk.com when present, keep BA order within each group."""
    if not pool or count <= 0:
        return []
    vk = [item for item in pool if is_vk_item(item)]
    other = [item for item in pool if not is_vk_item(item)]
    picked: list[MentionItem] = []
    for group in (vk, other):
        for item in group:
            if len(picked) >= count:
                return picked
            picked.append(item)
    return picked


def pick_delivery_items(
    pool: list[MentionItem],
    count: int = EMAIL_SAMPLE_COUNT,
) -> list[MentionItem]:
    """
    Email / magic link: up to `count` examples, predominantly VK when available,
    then shuffled so order does not match Brand Analytics feed.
    """
    if not pool:
        return []
    target = min(count, len(pool))
    vk = [item for item in pool if is_vk_item(item)]
    other = [item for item in pool if not is_vk_item(item)]

    if len(vk) >= target:
        selected = random.sample(vk, target)
    else:
        selected = list(vk)
        need = target - len(selected)
        if need > 0 and other:
            selected.extend(random.sample(other, min(need, len(other))))

    random.shuffle(selected)
    return selected
