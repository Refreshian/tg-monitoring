from pydantic import BaseModel, EmailStr, Field


class AccessRequestCreate(BaseModel):
    query: str = Field(min_length=2, max_length=500)
    contact_name: str = Field(min_length=2, max_length=200)
    contact_email: EmailStr
    contact_phone: str | None = Field(default=None, max_length=50)
    message: str | None = Field(default=None, max_length=2000)


class AccessRequestRead(AccessRequestCreate):
    id: int
