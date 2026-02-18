from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Annotated, List, Dict, Optional ,Any

from ...dependencies import db_dependency, emp_dependency
from ....utils.logger import logger
from customer360.services import VolumeTrendsService

router = APIRouter()


@router.get("/volume-trends", response_model=Dict[str, Any])
async def volume_trends(
    emp: emp_dependency,
    db: db_dependency,
    period: Annotated[str, Query(enum=["today", "7days", "30days", "90days"])] = "7days",
    channels: Annotated[Optional[List[str]], Query()] = None
):
    """
    Message volume trends over selected period.
    - period: today | 7days | 30days | 90days
    - channels: optional (e.g. SMS, WhatsApp) — omit for all
    """
    if emp is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed")

    logger.info("volume-trends endpoint called")

    try:
        service = VolumeTrendsService()
        return service.get_volume_trends(period=period, channels=channels)
    except Exception as e:
        logger.error(f"Error in volume-trends: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch volume trends")