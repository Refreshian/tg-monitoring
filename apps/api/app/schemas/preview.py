from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class MentionItem(BaseModel):
    source: str = Field(description="Platform or media outlet")
    title: str | None = None
    text: str
    url: str | None = None
    published_at: datetime | None = None


class MentionTeaser(BaseModel):
    """Public teaser: source and link only (no message text)."""

    source: str
    url: str | None = None
    published_at: datetime | None = None


class PreviewRequest(BaseModel):
    query: str = Field(min_length=2, max_length=500, description="Search query for br-analytics.ru")


class PreviewResponse(BaseModel):
    query: str
    original_query: str | None = None
    query_changed: bool = False
    query_note: str | None = None
    weekly_count: int | None = None
    estimated_monthly_messages: int | None = None
    estimated_price_rub: int | None = None
    price_is_from: bool = False
    tariff_name: str | None = None
    sample_token: str | None = None
    samples_available: bool = False
    teasers: list[MentionTeaser] = Field(default_factory=list)
    # Kept empty; full snippets are delivered by email / magic link only.
    total: int = 0
    items: list[MentionItem] = Field(default_factory=list)


class SendSamplesRequest(BaseModel):
    sample_token: str = Field(min_length=8, max_length=128)
    email: EmailStr


class SendSamplesResponse(BaseModel):
    sent: bool
    message: str


class PreviewSamplesResponse(BaseModel):
    query: str
    items: list[MentionItem]
    expires_note: str = "Ссылка действует ограниченное время."
