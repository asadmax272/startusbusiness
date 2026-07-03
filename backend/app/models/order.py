import uuid

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, ARRAY
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func

from app.core.db import Base


class Company(Base):
    __tablename__ = "companies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    llc_name = Column(String, nullable=True)
    state = Column(String, nullable=False, default="Wyoming")
    llc_status = Column(String, nullable=False, default="not_started")
    ein_status = Column(String, nullable=False, default="pending")
    ein_number = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class Order(Base):
    __tablename__ = "orders"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=True)
    package = Column(String, nullable=False)
    services = Column(ARRAY(String), nullable=False)
    status = Column(String, nullable=False, default="draft")
    amount_cents = Column(Integer, nullable=False)
    currency = Column(String, nullable=False, default="usd")
    ai_recommendation = Column(JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
