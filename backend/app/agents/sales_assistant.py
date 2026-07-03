"""
AI Sales Assistant.

Runs the 4-question flow (country, business type, payment processor, banking
need) through Claude, and returns a *strict JSON* recommendation that the
frontend renders directly. We never show raw model prose for structured
fields — only `reasoning` is free text, everything else is validated against
SalesAssistantResponse before it leaves the API.
"""

import json

from anthropic import Anthropic

from app.core.config import settings
from app.core.packages import PACKAGES, SERVICES
from app.schemas.ai import SalesAssistantRequest, SalesAssistantResponse

client = Anthropic(api_key=settings.anthropic_api_key)

SYSTEM_PROMPT = f"""You are the AI Sales Assistant for StartUSBusiness, a platform \
that helps non-US residents form US companies (primarily Wyoming LLCs) and get \
set up with the supporting services they need.

Available services (id: label):
{json.dumps(SERVICES, indent=2)}

Available packages (id: details):
{json.dumps(PACKAGES, indent=2)}

Rules you must always follow:
- Recommend Wyoming as the state unless the user's business type clearly calls \
for something else (explain briefly if so).
- NEVER imply guaranteed approval for Mercury, Stripe, Payoneer, or EIN. Use \
"application assistance" / "setup support" language only.
- Pick the package whose included services best match what the user needs — \
don't upsell services they didn't indicate a need for.
- Respond with ONLY a JSON object, no markdown fences, no preamble, matching \
exactly this shape:
{{
  "recommended_state": string,
  "recommended_services": string[]  (service ids from the list above),
  "recommended_package": "starter" | "business" | "premium" | "enterprise",
  "estimated_cost_usd": number (use the package's price_cents / 100),
  "reasoning": string (2-3 sentences, plain language, addressed to the user)
}}"""


def get_recommendation(req: SalesAssistantRequest) -> SalesAssistantResponse:
    user_message = (
        f"Country: {req.country}\n"
        f"Business type: {req.business_type}\n"
        f"Payment processor interest: {req.payment_processor}\n"
        f"Banking need: {req.banking_need}\n"
        + (f"Additional context: {req.free_text}\n" if req.free_text else "")
    )

    message = client.messages.create(
        model=settings.ai_model,
        max_tokens=1000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}],
    )

    raw_text = "".join(
        block.text for block in message.content if block.type == "text"
    ).strip()

    data = json.loads(raw_text)
    return SalesAssistantResponse(**data)
