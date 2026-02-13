from ...dependencies import db_dependency , emp_dependency
from fastapi import APIRouter, Depends, HTTPException, status
from ....utils.logger import logger
from ....services.dashboard_services import average_resolution_service

router = APIRouter()


@router.get("/average-resoltion", response_model=float)
async def average_reslotion(
    emp: emp_dependency,
    db: db_dependency,
):
    if emp is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed")

    logger.info("average-resoltion endpoint called")
    return average_resolution_service.get_avg_resolution_time()
