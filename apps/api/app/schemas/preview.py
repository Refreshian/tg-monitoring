from datetime import datetime

from pydantic import BaseModel, Field


class MentionItem(BaseModel):
    source: str = Field(description="Platform or media outlet")
    title: str | None = None
    text: str
    url: str | None = None
    published_at: datetime | None = None


class PreviewRequest(BaseModel):
    query: str = Field(min_length=2, max_length=500, description="Search query for br-analytics.ru")


class PreviewResponse(BaseModel):
    query: str
    original_query: str | None = None
    query_changed: bool = False
    query_note: str | None = None
    total: int
    items: list[MentionItem]
    # Approximate access price for the visitor (BA Razovo tariff minus ~32%).
    # Monthly volume is computed server-side and not shown in the UI yet.
    estimated_price_rub: int | None = None
    price_is_from: bool = False
