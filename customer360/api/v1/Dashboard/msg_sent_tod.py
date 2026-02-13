"""
Endpoint: Messages Sent Today by Current Employee
- Reads from JSON file
- Filters messages by employee (using Emp_id from JWT)
- Counts only messages sent TODAY
- Uses the exact datetime format from your sample
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

# Your existing dependencies
from ....Database.session import get_db
from ...dependencies import  get_current_employee 
from ....utils.logger import logger
from ....services.dashboard_services.message_service import MessageService


router = APIRouter()


@router.get("/msg-sent-today", response_model=int)
async def get_messages_sent_today_by_employee(
    emp: Annotated[dict, Depends(get_current_employee)],
    db: Annotated[Session, Depends(get_db)]
):
    """
    Get number of messages SENT TODAY by the currently logged-in employee.
    
    Returns:
        Integer count (0 if none or error)
    """
    if emp is None or "Emp_id" not in emp:
        logger.warning("Unauthorized or invalid employee data")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
            headers={"WWW-Authenticate": "Bearer"},
        )

    employee_id = emp["Emp_id"]
    logger.info(f"Counting today's messages for employee ID: {employee_id} ({emp.get('Emp_email', 'unknown')})")

    try:
        messages = MessageService.load_messages_from_json()

        if not messages:
            logger.info("No messages found in file")
            return 0

        count = MessageService.count_messages_sent_today_by_employee(messages, employee_id)

        logger.info(f"Employee {employee_id} sent {count} messages today")
        return count

    except Exception as e:
        logger.error(f"Critical error in msg-sent-today endpoint: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to calculate message count"
        )