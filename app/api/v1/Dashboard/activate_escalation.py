from dependencies import dash_act_esc , db_dependency , emp_dependency
from fastapi import APIRouter, Depends, HTTPException, status

router = APIRouter()


@router.get("/active-escalations", response_model=int)
async def active_escalations(
    emp: emp_dependency,
    db: db_dependency,
    kpi: dash_act_esc,
):
    if emp is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed")

    logger.info("active-escalations endpoint called")
    return kpi.get_active_escalations()
