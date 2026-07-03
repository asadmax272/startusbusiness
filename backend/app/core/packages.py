"""
Single source of truth for packages, services, and pricing.
Frontend pricing page and Stripe checkout both read from this (via the API),
so numbers never drift out of sync.
"""

SERVICES = {
    "wyoming_llc": "Wyoming LLC Formation",
    "ein": "EIN Application Assistance",
    "registered_agent": "Registered Agent Service (1 year)",
    "us_address": "US Business Address",
    "us_phone": "US Phone Number",
    "mercury_support": "Mercury Bank Application Assistance",
    "payoneer_support": "Payoneer Setup Assistance",
    "seller_permit": "Seller Permit",
    "resale_certificate": "Resale Certificate",
    "annual_report": "Annual Report Filing",
    "compliance_reminders": "Compliance Reminders",
    "consultation": "1:1 Business Consultation",
}

PACKAGES = {
    "starter": {
        "label": "Starter",
        "price_cents": 14900,
        "services": ["wyoming_llc", "registered_agent"],
        "description": "The minimum to legally exist as a US company.",
    },
    "business": {
        "label": "Business",
        "price_cents": 29900,
        "services": [
            "wyoming_llc", "ein", "registered_agent", "us_address",
        ],
        "description": "Everything most Shopify, Amazon, and SaaS founders need.",
    },
    "premium": {
        "label": "Premium",
        "price_cents": 49900,
        "services": [
            "wyoming_llc", "ein", "registered_agent", "us_address", "us_phone",
            "mercury_support", "payoneer_support",
        ],
        "description": "Formation plus banking and payments application support.",
    },
    "enterprise": {
        "label": "Enterprise",
        "price_cents": 99900,
        "services": list(SERVICES.keys()),
        "description": "Full setup, compliance, and ongoing support for growing brands.",
    },
}
