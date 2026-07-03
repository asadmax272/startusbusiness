from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.deps import get_current_user
from app.models.order import Order
from app.models.tracking import EINApplication, LLCApplication
from app.models.user import User
from app.schemas.workflow import EINApplicationOut, LLCApplicationOut, OrderOut

router = APIRouter(prefix="/api/orders", tags=["orders"])


@router.get("", response_model=list[OrderOut])
def list_my_orders(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Order).filter(Order.user_id == current_user.id).order_by(Order.created_at.desc()).all()


@router.get("/{order_id}/llc", response_model=LLCApplicationOut)
def get_llc_status(order_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    app_row = (
        db.query(LLCApplication)
        .filter(LLCApplication.order_id == order_id, LLCApplication.user_id == current_user.id)
        .first()
    )
    if not app_row:
        raise HTTPException(404, "No LLC application found for this order.")
    return app_row


@router.get("/{order_id}/ein", response_model=EINApplicationOut)
def get_ein_status(order_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    app_row = (
        db.query(EINApplication)
        .filter(EINApplication.order_id == order_id, EINApplication.user_id == current_user.id)
        .first()
    )
    if not app_row:
        raise HTTPException(404, "No EIN application found for this order.")
    return app_row
