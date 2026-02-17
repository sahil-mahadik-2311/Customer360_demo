from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Annotated, Dict, Any

from ....utils.exceptions import CalculationError
from ...dependencies import db_dependency, emp_dependency
from ....utils.logger import logger
from ....services.Customer360_services.loanBYloanid_service import get_payment_behaviour_service

router = APIRouter()


@router.get("/loan_detailsbyloanID", response_model=Dict[str, Any])
async def payment_behaviour(
    emp: emp_dependency,
    db: db_dependency,
    customer_id: Annotated[str, Query(min_length=1, description="Required: Customer ID")],
    lan: Annotated[str, Query(min_length=1, description="Required: Loan Account Number (LAN)")]
):
    """
    Fetch customer info + **one specific loan** summary + payment behaviour (last 6 EMIs)
    - Required: customer_id and lan
    - Only returns data for that exact loan
    """
    if emp is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed")

    customer_id_clean = customer_id.strip()
    lan_clean = lan.strip()

    if not customer_id_clean or not lan_clean:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Both customer_id and lan are required")

    logger.info(f"payment-behaviour called for customer {customer_id_clean}, loan {lan_clean}")

    try:
        service = get_payment_behaviour_service()
        result = service.get_payment_behaviour(customer_id=customer_id_clean, lan=lan_clean)
        
        if result["customer"] is None or result["loan"] is None:
            return {
                "customer": None,
                "loan": None,
                "payment_behaviour": {},
                "message": f"No data found for customer {customer_id_clean} and loan {lan_clean}"
            }
            
        return result
    
    except CalculationError as ce:
        raise HTTPException(status_code=500, detail=str(ce))
    except Exception as e:
        logger.error(f"Error in payment-behaviour: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch payment behaviour")