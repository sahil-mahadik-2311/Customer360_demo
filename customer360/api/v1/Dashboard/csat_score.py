from ...dependencies import db_dependency , emp_dependency
from fastapi import APIRouter, Depends, HTTPException, status
from ....utils.logger import logger
from ....services.dashboard_services import csat_score_service

router = APIRouter()


@router.get("/csat-score", response_model=float)
async def csat_score(
    emp: emp_dependency,
    db: db_dependency,
):
    if emp is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed")

    logger.info("/csat-score endpoint called")
    return csat_score_service.get_csat_score()
