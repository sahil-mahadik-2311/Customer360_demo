from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Annotated, Dict, Any

from ....utils.exceptions import CalculationError
from ...dependencies import db_dependency, emp_dependency
from ....utils.logger import logger
from customer360.services import CustomerByIdService

router = APIRouter(prefix="/Customer360", tags=["Customer360"])


@router.get("/customer-by-id", response_model=Dict[str, Any])
async def customer_by_id(
    emp: emp_dependency,
    db: db_dependency,
    customer_id: Annotated[str, Query(min_length=1, description="Required: Customer ID")]
):
    """
    Fetch full details of one customer by customer_id
    - Returns customer profile + all loans
    - 404-style empty response if not found
    """
    if emp is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed")

    if not customer_id.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="customer_id is required")

    logger.info(f"customer-by-id endpoint called for ID: {customer_id}")

    try:
        service = CustomerByIdService()
        result = service.get_customer_by_id(customer_id=customer_id.strip())
        
        if result["customer"] is None:
            return {
                "customer": None,
                "loans": [],
                "total_loans": 0,
                "message": f"No customer found with ID: {customer_id}"
            }
            
        return result
    
    except CalculationError as ce:
        raise HTTPException(status_code=500, detail=str(ce))
    except Exception as e:
        logger.error(f"Error in customer-by-id: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch customer details")