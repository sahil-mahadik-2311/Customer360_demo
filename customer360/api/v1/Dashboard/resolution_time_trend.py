from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Annotated, Dict, Any, Optional

from ....utils.exceptions import CalculationError
from ...dependencies import db_dependency, emp_dependency
from ....utils.logger import logger
from customer360.services import ResolutionTimeTrendService

router = APIRouter()


@router.get("/resolution-time-trend", response_model=Dict[str, Any])
async def resolution_time_trend(
    emp: emp_dependency,
    db: db_dependency,
    timeline: Annotated[str, Query(enum=["24h", "7days", "30days"])] = "7days",
    channel: Annotated[Optional[str], Query()] = None
):
    """
    Resolution time trend over selected timeline and channel.
    - timeline: 24h | 7days | 30days
    - channel: optional single channel (e.g. Email) — omit for all
    """
    if emp is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed")

    logger.info("resolution-time-trend endpoint called")

    try:
        service = ResolutionTimeTrendService()
        return service.get_resolution_trend(timeline=timeline, channel=channel)
    except CalculationError as ce:
        raise HTTPException(status_code=500, detail=str(ce))
    except Exception as e:
        logger.error(f"Error in resolution-time-trend: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch resolution trend")