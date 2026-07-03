from fastapi import APIRouter, Depends, HTTPException

from app.agents import onboarding, sales_assistant
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.ai import (
    OnboardingSubmission,
    OnboardingValidationResponse,
    SalesAssistantRequest,
    SalesAssistantResponse,
)

router = APIRouter(prefix="/api/ai", tags=["ai"])


@router.post("/sales-assistant", response_model=SalesAssistantResponse)
def sales_assistant_recommendation(payload: SalesAssistantRequest):
    """Public endpoint — no login required, powers the on-site chat widget."""
    try:
        return sales_assistant.get_recommendation(payload)
    except Exception as e:
        raise HTTPException(502, f"AI assistant is temporarily unavailable: {e}")


@router.post("/onboarding/validate", response_model=OnboardingValidationResponse)
def onboarding_validate(
    payload: OnboardingSubmission, current_user: User = Depends(get_current_user)
):
    """Runs after checkout — validates the client's submitted formation data."""
    try:
        return onboarding.validate_submission(payload)
    except Exception as e:
        raise HTTPException(502, f"AI onboarding check is temporarily unavailable: {e}")
