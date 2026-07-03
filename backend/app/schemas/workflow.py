import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel

# NOTE: id / foreign-key fields below are typed as uuid.UUID, not str.
# SQLAlchemy returns live uuid.UUID objects for postgresql.UUID(as_uuid=True)
# columns, and Pydantic v2 does NOT auto-coerce UUID -> str for a `str`
# field (unlike str -> UUID, which does work on input). Typing these as
# uuid.UUID lets Pydantic validate the ORM attribute directly; FastAPI's
# JSON encoder still serializes UUID -> string in the response body, so the
# frontend still receives plain strings. Typing them `str` here would raise
# a ResponseValidationError on every request that returns one of these
# schemas from an ORM object.


class OrderOut(BaseModel):
    id: uuid.UUID
    package: str
    services: list[str]
    status: str
    amount_cents: int
    created_at: datetime

    class Config:
        from_attributes = True


class LLCApplicationOut(BaseModel):
    id: uuid.UUID
    company_name: str
    state: str
    status: str
    admin_notes: Optional[str]
    updated_at: datetime

    class Config:
        from_attributes = True


class EINApplicationOut(BaseModel):
    id: uuid.UUID
    status: str
    ein_number: Optional[str]
    admin_notes: Optional[str]
    updated_at: datetime

    class Config:
        from_attributes = True


class LLCStatusUpdate(BaseModel):
    status: str
    admin_notes: Optional[str] = None


class EINStatusUpdate(BaseModel):
    status: str
    ein_number: Optional[str] = None
    admin_notes: Optional[str] = None


class DocumentOut(BaseModel):
    id: uuid.UUID
    order_id: uuid.UUID
    type: str
    file_name: str
    verified: bool
    created_at: datetime

    class Config:
        from_attributes = True


class TicketCreate(BaseModel):
    subject: str
    message: str
    order_id: Optional[str] = None  # input from JSON — plain str is fine here


class MessageOut(BaseModel):
    id: uuid.UUID
    sender_id: uuid.UUID
    body: str
    is_ai_generated: bool
    created_at: datetime

    class Config:
        from_attributes = True


class TicketOut(BaseModel):
    id: uuid.UUID
    subject: str
    status: str
    assigned_to: Optional[uuid.UUID]
    created_at: datetime

    class Config:
        from_attributes = True


class TicketReply(BaseModel):
    body: str


class NotificationOut(BaseModel):
    id: uuid.UUID
    title: str
    body: str
    link: Optional[str]
    read_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True
