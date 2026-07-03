from fastapi import APIRouter

from app.core.packages import PACKAGES, SERVICES

router = APIRouter(prefix="/api/packages", tags=["packages"])


@router.get("")
def list_packages():
    return {"packages": PACKAGES, "services": SERVICES}
