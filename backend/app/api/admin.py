from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.deps import require_role
from app.models.misc import Notification
from app.models.order import Order
from app.models.support import Ticket
from app.models.tracking import EINApplication, LLCApplication
from app.models.user import User
from app.schemas.workflow import (
    EINApplicationOut,
    EINStatusUpdate,
    LLCApplicationOut,
    LLCStatusUpdate,
    OrderOut,
    TicketOut,
)
from app.services import email_service

router = APIRouter(prefix="/api/admin", tags=["admin"])
admin_or_staff = require_role("admin", "staff")


@router.get("/orders", response_model=list[OrderOut])
def list_orders(
    status: Optional[str] = None,
    q: Optional[str] = None,
    _: User = Depends(admin_or_staff),
    db: Session = Depends(get_db),
):
    query = db.query(Order)
    if status:
        query = query.filter(Order.status == status)
    if q:
        query = query.join(User).filter(User.email.ilike(f"%{q}%"))
    return query.order_by(Order.created_at.desc()).all()


@router.get("/users", response_model=list[dict])
def list_users(q: Optional[str] = None, _: User = Depends(admin_or_staff), db: Session = Depends(get_db)):
    query = db.query(User)
    if q:
        query = query.filter(User.email.ilike(f"%{q}%"))
    users = query.order_by(User.created_at.desc()).all()
    return [
        {"id": str(u.id), "email": u.email, "full_name": u.full_name, "role": u.role, "country": u.country}
        for u in users
    ]


@router.get("/tickets", response_model=list[TicketOut])
def list_all_tickets(status: Optional[str] = None, _: User = Depends(admin_or_staff), db: Session = Depends(get_db)):
    query = db.query(Ticket)
    if status:
        query = query.filter(Ticket.status == status)
    return query.order_by(Ticket.created_at.desc()).all()


@router.patch("/llc-applications/{app_id}", response_model=LLCApplicationOut)
def update_llc_status(
    app_id: str, payload: LLCStatusUpdate, admin_user: User = Depends(admin_or_staff), db: Session = Depends(get_db)
):
    app_row = db.query(LLCApplication).filter(LLCApplication.id == app_id).first()
    if not app_row:
        raise HTTPException(404, "LLC application not found.")

    app_row.status = payload.status
    if payload.admin_notes is not None:
        app_row.admin_notes = payload.admin_notes

    db.add(
        Notification(
            user_id=app_row.user_id,
            title="LLC status updated",
            body=f"Your LLC application is now: {payload.status.replace('_', ' ').title()}.",
            link=f"/dashboard/llc-status",
        )
    )
    db.commit()
    db.refresh(app_row)

    user = db.query(User).filter(User.id == app_row.user_id).first()
    if user:
        try:
            email_service.status_update_email(user.email, "LLC application", payload.status)
        except RuntimeError:
            pass

    return app_row


@router.patch("/ein-applications/{app_id}", response_model=EINApplicationOut)
def update_ein_status(
    app_id: str, payload: EINStatusUpdate, admin_user: User = Depends(admin_or_staff), db: Session = Depends(get_db)
):
    app_row = db.query(EINApplication).filter(EINApplication.id == app_id).first()
    if not app_row:
        raise HTTPException(404, "EIN application not found.")

    app_row.status = payload.status
    if payload.ein_number is not None:
        app_row.ein_number = payload.ein_number
    if payload.admin_notes is not None:
        app_row.admin_notes = payload.admin_notes

    db.add(
        Notification(
            user_id=app_row.user_id,
            title="EIN status updated",
            body=f"Your EIN application is now: {payload.status.replace('_', ' ').title()}.",
            link=f"/dashboard/ein-status",
        )
    )
    db.commit()
    db.refresh(app_row)

    user = db.query(User).filter(User.id == app_row.user_id).first()
    if user:
        try:
            email_service.status_update_email(user.email, "EIN application", payload.status)
        except RuntimeError:
            pass

    return app_row
