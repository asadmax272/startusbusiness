import stripe

from app.core.config import settings
from app.core.packages import PACKAGES

stripe.api_key = settings.stripe_secret_key


def create_checkout_session(package_id: str, user_email: str, user_id: str) -> str:
    package = PACKAGES[package_id]
    session = stripe.checkout.Session.create(
        mode="payment",
        customer_email=user_email,
        line_items=[
            {
                "price_data": {
                    "currency": "usd",
                    "unit_amount": package["price_cents"],
                    "product_data": {
                        "name": f"StartUSBusiness — {package['label']} Package",
                        "description": package["description"],
                    },
                },
                "quantity": 1,
            }
        ],
        success_url=f"{settings.frontend_url}/dashboard?checkout=success",
        cancel_url=f"{settings.frontend_url}/pricing?checkout=cancelled",
        metadata={"package_id": package_id, "user_id": user_id},
    )
    return session.url


def construct_webhook_event(payload: bytes, sig_header: str):
    return stripe.Webhook.construct_event(
        payload, sig_header, settings.stripe_webhook_secret
    )
