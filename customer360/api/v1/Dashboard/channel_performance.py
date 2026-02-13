from typing import Dict , List , Annotated
from ....utils.exceptions import CalculationError
from ...dependencies import db_dependency , emp_dependency
from fastapi import APIRouter, Depends, HTTPException, status , Query
from ....utils.logger import logger
from ....services.dashboard_services import channel_perfomance_service

router = APIRouter()



@router.get("/channel-performance", response_model=List[Dict[str, float | int | str]])
async def channel_performance(
    emp: emp_dependency,
    db: db_dependency,
    sort_by: Annotated[str, Query(enum=["volume", "delivery_rate"])] = "volume"
):
    """
    Get channel performance metrics (volume, delivery_rate, avg_time)
    Sorted by 'volume' (desc) or 'delivery_rate' (desc)
    Single endpoint handles both sorting modes
    """
    if emp is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication Failed",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        return channel_perfomance_service.get_channel_performance(sort_by=sort_by)
    except CalculationError as ce:
        raise HTTPException(status_code=500, detail=str(ce))
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Internal error while calculating channel performance"
        )