import logging

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.deps import get_current_user
from app.core.packages import PACKAGES
from app.models.misc import AuditLog, Notification, Payment
from app.models.order import Company, Order
from app.models.tracking import EINApplication, LLCApplication
from app.models.user import User
from app.services import email_service, stripe_service

router = APIRouter(prefix="/api/payments", tags=["payments"])
logger = logging.getLogger("payments")


@router.post("/checkout/{package_id}")
def checkout(package_id: str, current_user: User = Depends(get_current_user)):
    if package_id not in PACKAGES:
        raise HTTPException(404, "Unknown package.")
    url = stripe_service.create_checkout_session(package_id, current_user.email, str(current_user.id))
    return {"checkout_url": url}


@router.post("/webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature", "")
    try:
        event = stripe_service.construct_webhook_event(payload, sig_header)
    except Exception:
        raise HTTPException(400, "Invalid Stripe webhook signature.")

    if event["type"] == "checkout.session.completed":
        _handle_checkout_completed(event["data"]["object"], db)

    return {"received": True}


def _handle_checkout_completed(session: dict, db: Session) -> None:
    """
    This is the join point the original build left as a no-op. It now
    actually creates the Order, Company, LLC/EIN application rows, records
    the payment, writes an audit log entry, creates an in-app notification,
    and sends a real confirmation email.
    """
    metadata = session.get("metadata") or {}
    package_id = metadata.get("package_id")
    user_id = metadata.get("user_id")

    if not package_id or not user_id or package_id not in PACKAGES:
        logger.error("checkout.session.completed missing/invalid metadata: %s", metadata)
        return

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        logger.error("checkout.session.completed for unknown user_id=%s", user_id)
        return

    # Idempotency: Stripe can retry webhook delivery.
    existing_payment = (
        db.query(Payment)
        .filter(Payment.stripe_checkout_session_id == session["id"])
        .first()
    )
    if existing_payment:
        return

    package = PACKAGES[package_id]

    company = Company(owner_id=user.id, state="Wyoming", llc_status="not_started", ein_status="pending")
    db.add(company)
    db.flush()

    order = Order(
        user_id=user.id,
        company_id=company.id,
        package=package_id,
        services=package["services"],
        status="in_progress",
        amount_cents=package["price_cents"],
        currency="usd",
    )
    db.add(order)
    db.flush()

    llc_app = LLCApplication(
        order_id=order.id,
        user_id=user.id,
        company_name=user.full_name and f"{user.full_name} LLC" or "Pending Name Selection",
        state="Wyoming",
        status="not_started",
    )
    db.add(llc_app)
    db.flush()

    if "ein" in package["services"]:
        db.add(EINApplication(order_id=order.id, user_id=user.id, llc_application_id=llc_app.id, status="pending"))

    payment = Payment(
        order_id=order.id,
        stripe_payment_intent_id=session.get("payment_intent"),
        stripe_checkout_session_id=session["id"],
        amount_cents=package["price_cents"],
        currency="usd",
        status="succeeded",
    )
    db.add(payment)

    db.add(
        Notification(
            user_id=user.id,
            title="Order confirmed",
            body=f"Your {package['label']} package is confirmed. We'll guide you through what we need next.",
            link=f"/dashboard/orders/{order.id}",
        )
    )

    db.add(
        AuditLog(
            actor_id=user.id,
            action="checkout.session.completed",
            entity="order",
            entity_id=order.id,
            log_metadata={"package_id": package_id, "stripe_session_id": session["id"]},
        )
    )

    db.commit()

    try:
        email_service.order_confirmation_email(user.email, package["label"], package["price_cents"] / 100)
    except RuntimeError:
        # RESEND_API_KEY not configured — order creation still succeeds.
        logger.warning("Skipped order confirmation email: Resend is not configured.")
