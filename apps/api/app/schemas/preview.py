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
    # Public preview returns volume + price only (no BA search snippets).
    weekly_count: int | None = None
    estimated_monthly_messages: int | None = None
    estimated_price_rub: int | None = None
    price_is_from: bool = False
    tariff_name: str | None = None
    # Kept empty for compatibility; real snippets are not exposed publicly.
    total: int = 0
    items: list[MentionItem] = Field(default_factory=list)
