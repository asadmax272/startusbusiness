from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.deps import get_current_user
from app.models.support import Message, Ticket
from app.models.user import User
from app.schemas.workflow import MessageOut, TicketCreate, TicketOut, TicketReply

router = APIRouter(prefix="/api/tickets", tags=["support"])


@router.post("", response_model=TicketOut)
def create_ticket(payload: TicketCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    ticket = Ticket(user_id=current_user.id, order_id=payload.order_id, subject=payload.subject)
    db.add(ticket)
    db.flush()

    first_message = Message(ticket_id=ticket.id, sender_id=current_user.id, body=payload.message)
    db.add(first_message)
    db.commit()
    db.refresh(ticket)
    return ticket


@router.get("", response_model=list[TicketOut])
def list_my_tickets(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    query = db.query(Ticket)
    if current_user.role == "client":
        query = query.filter(Ticket.user_id == current_user.id)
    return query.order_by(Ticket.created_at.desc()).all()


@router.get("/{ticket_id}/messages", response_model=list[MessageOut])
def get_ticket_messages(ticket_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(404, "Ticket not found.")
    if current_user.role == "client" and str(ticket.user_id) != str(current_user.id):
        raise HTTPException(403, "This ticket doesn't belong to you.")
    return db.query(Message).filter(Message.ticket_id == ticket_id).order_by(Message.created_at).all()


@router.post("/{ticket_id}/reply", response_model=MessageOut)
def reply_to_ticket(ticket_id: str, payload: TicketReply, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(404, "Ticket not found.")
    if current_user.role == "client" and str(ticket.user_id) != str(current_user.id):
        raise HTTPException(403, "This ticket doesn't belong to you.")

    message = Message(ticket_id=ticket_id, sender_id=current_user.id, body=payload.body)
    db.add(message)

    if current_user.role in ("admin", "staff"):
        ticket.status = "pending"
    else:
        ticket.status = "open"
    db.commit()
    db.refresh(message)
    return message


@router.post("/{ticket_id}/close", response_model=TicketOut)
def close_ticket(ticket_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role not in ("admin", "staff"):
        raise HTTPException(403, "Only staff can close tickets.")
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(404, "Ticket not found.")
    ticket.status = "closed"
    db.commit()
    db.refresh(ticket)
    return ticket
