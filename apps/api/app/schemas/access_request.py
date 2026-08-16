from pydantic import BaseModel, EmailStr, Field


class AccessRequestCreate(BaseModel):
    contact_name: str = Field(min_length=2, max_length=200)
    contact_phone: str = Field(min_length=5, max_length=50)
    monitoring_object: str = Field(
        min_length=2,
        max_length=1000,
        description="What the client wants to monitor",
    )
    contact_email: EmailStr | None = None
    query: str | None = Field(default=None, max_length=500)
    message: str | None = Field(default=None, max_length=2000)


class AccessRequestRead(AccessRequestCreate):
    id: int
