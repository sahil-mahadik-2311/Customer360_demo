from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Annotated, Dict, Any, Optional

from ...dependencies import db_dependency, emp_dependency
from ....utils.logger import logger
from ....utils.exceptions import CalculationError
from customer360.services import CustomerDetailsService

router = APIRouter()


@router.get("/customer-details", response_model=Dict[str, Any])
async def customer_details(
    emp: emp_dependency,
    db: db_dependency,
    customer_id: Annotated[Optional[str], Query()] = None,
    name: Annotated[Optional[str], Query()] = None,
    mobile: Annotated[Optional[str], Query()] = None,
    email: Annotated[Optional[str], Query()] = None,
    pan: Annotated[Optional[str], Query()] = None,
    lan: Annotated[Optional[str], Query()] = None,
    filter_type: Annotated[str, Query(enum=["ALL", "Email", "SMS", "WhatsApp", "Post", "IVR", "Failed", "Delivered"])] = "ALL"
):
    """
    Retrieve single customer details, loans, and loan communications.
    Search by one: customer_id, name, mobile, email, pan (first match).
    Communications for specific lan (optional) and filtered by type/status.
    """
    if emp is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed")

    logger.info("customer-details endpoint called")

    try:
        service = CustomerDetailsService()
        return service.get_customer_details(
            customer_id=customer_id,
            name=name,
            mobile=mobile,
            email=email,
            pan=pan,
            lan=lan,
            filter_type=filter_type
        )
    except CalculationError as ce:
        raise HTTPException(status_code=500, detail=str(ce))
    except Exception as e:
        logger.error(f"Error in customer-details: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch customer details")