from fastapi import APIRouter, Depends, HTTPException, status
from typing import Annotated, List, Dict, Any

from ...dependencies import db_dependency, emp_dependency
from ....utils.logger import logger
from ....services.dashboard_services.top_issues_service import get_top_issues_service

router = APIRouter()


@router.get("/top-issues", response_model=List[Dict[str, Any]])
async def top_issues(
    emp: emp_dependency,
    db: db_dependency,
):
    if emp is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed")

    logger.info("top-issues endpoint called")
    service = get_top_issues_service()
    return service.get_top_issues()