from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Annotated, Dict, Any, Optional

from ....utils.exceptions import CalculationError
from ...dependencies import db_dependency, emp_dependency
from ....utils.logger import logger
from customer360.services import CustomerListService

router = APIRouter(prefix="/Customer360", tags=["Customer360"])


@router.get("/customer-list", response_model=Dict[str, Any])
async def customer_list(
    emp: emp_dependency,
    db: db_dependency,
    search: Annotated[Optional[str], Query(max_length=100, description="Search by name, ID, mobile, email, PAN")] = None,
    limit: Annotated[int, Query(ge=1, le=100, description="Items per page")] = 20,
    offset: Annotated[int, Query(ge=0, description="Skip this many items")] = 0
):
    """
    Paginated list of all customers (basic details only)
    - search: partial match on name/customer_id/mobile/email/PAN
    - limit: max 100
    - offset: for pagination
    Returns customers list + total count
    """
    if emp is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed")

    logger.info(f"customer-list endpoint called (search: '{search}', limit: {limit}, offset: {offset})")

    try:
        service = CustomerListService()
        return service.get_customers(search=search, limit=limit, offset=offset)
    except CalculationError as ce:
        raise HTTPException(status_code=500, detail=str(ce))
    except Exception as e:
        logger.error(f"Error in customer-list: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch customer list")