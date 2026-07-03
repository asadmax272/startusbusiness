from typing import Literal, Optional

from pydantic import BaseModel, Field


class SalesAssistantRequest(BaseModel):
    country: str = Field(..., examples=["UAE", "Pakistan", "India", "Other"])
    business_type: str = Field(..., examples=["Amazon", "Shopify", "SaaS", "Freelancer", "Agency"])
    payment_processor: str = Field(..., examples=["Stripe", "PayPal", "Not Sure"])
    banking_need: str = Field(..., examples=["Mercury", "Payoneer", "Not Sure"])
    free_text: Optional[str] = Field(None, description="Anything else the user typed to the assistant")


class SalesAssistantResponse(BaseModel):
    recommended_state: str
    recommended_services: list[str]
    recommended_package: Literal["starter", "business", "premium", "enterprise"]
    estimated_cost_usd: int
    reasoning: str
    disclaimer: str = (
        "This is guidance based on common setups for founders in your situation. "
        "It isn't legal, tax, or immigration advice, and no outcome — including "
        "bank or payment processor approval — is guaranteed."
    )


class OnboardingSubmission(BaseModel):
    full_name: str
    email: str
    phone: str
    address: str
    business_name_preferences: list[str]
    passport_document_key: Optional[str] = None


class OnboardingValidationResponse(BaseModel):
    is_complete: bool
    missing_fields: list[str]
    issues: list[str]
    notes: str
