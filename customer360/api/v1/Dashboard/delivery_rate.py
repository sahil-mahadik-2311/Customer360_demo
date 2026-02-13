from ...dependencies import db_dependency , emp_dependency
from fastapi import APIRouter, Depends, HTTPException, status
from ....utils.logger import logger
from ....services.dashboard_services import delivery_rate_service

router = APIRouter()


@router.get("/delivery-rate", response_model=float)
async def delivery_rate(
    emp: emp_dependency,
    db: db_dependency,
):
    if emp is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed")

    logger.info("delivery-rate endpoint called")
    return delivery_rate_service.get_delivery_rate()
