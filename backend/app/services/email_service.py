"""
Email service — real Resend API integration. Requires RESEND_API_KEY to
actually send; without it, send() raises loudly rather than silently
no-opping, so a missing key is caught in testing, not in production.
"""

import httpx

from app.core.config import settings

RESEND_API_URL = "https://api.resend.com/emails"


def send(to: str, subject: str, html: str) -> None:
    if not settings.resend_api_key:
        raise RuntimeError(
            "RESEND_API_KEY is not set — email sending is not configured."
        )
    resp = httpx.post(
        RESEND_API_URL,
        headers={"Authorization": f"Bearer {settings.resend_api_key}"},
        json={"from": settings.email_from_address, "to": [to], "subject": subject, "html": html},
        timeout=10,
    )
    resp.raise_for_status()


def welcome_email(to: str, full_name: str) -> None:
    send(
        to,
        "Welcome to StartUSBusiness",
        f"<p>Hi {full_name},</p><p>Your account is set up. You can track your "
        f"LLC and EIN application progress any time from your dashboard.</p>",
    )


def order_confirmation_email(to: str, package_label: str, amount_usd: float) -> None:
    send(
        to,
        "Order confirmed — StartUSBusiness",
        f"<p>Thanks — your <strong>{package_label}</strong> order "
        f"(${amount_usd:.2f}) is confirmed. We'll email you as soon as we "
        f"need anything from you, and you can follow progress in your "
        f"dashboard at any time.</p>",
    )


def status_update_email(to: str, entity: str, new_status: str) -> None:
    send(
        to,
        f"Update on your {entity}",
        f"<p>Your {entity} status is now: <strong>{new_status.replace('_', ' ').title()}</strong>. "
        f"Full details are in your dashboard.</p>",
    )
