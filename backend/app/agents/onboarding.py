"""
AI Onboarding Agent.

Runs after payment: validates the data the client submits (name, passport,
address, business name preferences, email, phone) before it's attached to
their order, catching obvious problems (missing info, malformed data,
likely-invalid business names) before a human has to look at it.
"""

import json

from anthropic import Anthropic

from app.core.config import settings
from app.schemas.ai import OnboardingSubmission, OnboardingValidationResponse

client = Anthropic(api_key=settings.anthropic_api_key)

SYSTEM_PROMPT = """You are the AI Onboarding Agent for StartUSBusiness. You \
check client-submitted formation data for completeness and obvious problems \
before it goes to the operations team. You do not give legal advice and you \
do not approve or reject business names on legal grounds — you flag things a \
human reviewer should look at (e.g. a business name preference that already \
contains "LLC" twice, an address that looks incomplete, a phone number \
missing a country code).

Respond with ONLY a JSON object, no markdown fences, no preamble:
{
  "is_complete": boolean,
  "missing_fields": string[],
  "issues": string[]  (short, specific, human-reviewer-facing notes),
  "notes": string (1-2 sentences summarizing for the client-facing status page)
}"""


def validate_submission(sub: OnboardingSubmission) -> OnboardingValidationResponse:
    payload = sub.model_dump()

    message = client.messages.create(
        model=settings.ai_model,
        max_tokens=600,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": json.dumps(payload, indent=2)}],
    )

    raw_text = "".join(
        block.text for block in message.content if block.type == "text"
    ).strip()

    data = json.loads(raw_text)
    return OnboardingValidationResponse(**data)
