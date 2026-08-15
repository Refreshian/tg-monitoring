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
    total: int
    items: list[MentionItem]
