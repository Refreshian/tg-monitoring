from fastapi import APIRouter

from app.schemas.access_request import AccessRequestCreate, AccessRequestRead

router = APIRouter()


@router.post("", response_model=AccessRequestRead, status_code=201)
async def create_access_request(payload: AccessRequestCreate) -> AccessRequestRead:
    """Store a lead request after the user reviewed preview results."""
    # TODO: persist to database and notify sales team
    return AccessRequestRead(
        id=1,
        query=payload.query,
        contact_name=payload.contact_name,
        contact_email=payload.contact_email,
        contact_phone=payload.contact_phone,
        message=payload.message,
    )
