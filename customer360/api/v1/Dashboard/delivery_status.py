from typing import Dict
from ....utils.exceptions import CalculationError
from ...dependencies import db_dependency , emp_dependency
from fastapi import APIRouter, Depends, HTTPException, status
from ....utils.logger import logger
from customer360.services import DeliveryRate

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])




@router.get("/delivery-status", response_model=Dict[str, Dict[str, float | int]])
async def delivery_status(
    emp: emp_dependency,
    db: db_dependency
    ):
    """
    Returns delivery status summary (today counts + % change vs previous 6 days)
    Format matches the donut chart data: Delivered / Failed / Pending
    """
    if emp is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication Failed",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        return DeliveryRate.get_delivery_status()
    except CalculationError as ce:
        raise HTTPException(status_code=500, detail=str(ce))
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Internal error while calculating delivery status"
        )
    

