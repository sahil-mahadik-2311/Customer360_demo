from ...dependencies import db_dependency , emp_dependency
from fastapi import APIRouter, Depends, HTTPException, status
from ....utils.logger import logger

from customer360.services import (MessageService,
           AverageResolutionTime,
           FailedMessage,
           ActiveEscalation,
           DeliveryRate,
           CSAT_Score)


router = APIRouter(prefix="/kpi", tags=["Dashboard KPI"])



@router.get("/active-escalations", response_model=int)
async def active_escalations(
    emp: emp_dependency,
    db: db_dependency,
):
    if emp is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed")

    logger.info("active-escalations endpoint called")
    return ActiveEscalation.get_active_escalations()


@router.get("/average-resoltion", response_model=float)
async def average_reslotion(
    emp: emp_dependency,
    db: db_dependency,
):
    if emp is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed")

    logger.info("average-resoltion endpoint called")
    return AverageResolutionTime.get_avg_resolution_time()



@router.get("/delivery-rate", response_model=float)
async def delivery_rate(
    emp: emp_dependency,
    db: db_dependency,
):
    if emp is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed")

    logger.info("delivery-rate endpoint called")
    return DeliveryRate.get_delivery_rate()



@router.get("/failed-message", response_model=int)
async def failed_message(
    emp: emp_dependency,
    db: db_dependency,
):
    if emp is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed")

    logger.info("failed-message endpoint called")
    return FailedMessage.get_failed_messages()



@router.get("/csat-score", response_model=float)
async def csat_score(
    emp: emp_dependency,
    db: db_dependency,
):
    if emp is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed")

    logger.info("/csat-score endpoint called")
    return CSAT_Score.get_csat_score()



@router.get("/msg-sent-today", response_model=float)
async def csat_score(
    emp: emp_dependency,
    db: db_dependency,
):
    if emp is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed")

    logger.info("/csat-score endpoint called")
    return MessageService.count_messages_sent_today_by_employee()
