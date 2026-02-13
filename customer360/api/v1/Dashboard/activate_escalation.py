from ...dependencies import db_dependency , emp_dependency
from fastapi import APIRouter, Depends, HTTPException, status
from ....utils.logger import logger
from ....services.dashboard_services import activate_escalation_service

router = APIRouter()


@router.get("/active-escalations", response_model=int)
async def active_escalations(
    emp: emp_dependency,
    db: db_dependency,
):
    if emp is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed")

    logger.info("active-escalations endpoint called")
    return activate_escalation_service.get_active_escalations()
