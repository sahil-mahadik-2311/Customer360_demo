from fastapi import APIRouter
from . import (activate_escalation , avg_resolution_time , csat_score , delivery_rate,failed_message ,msg_sent_tod , delivery_status, channel_performance)

router = APIRouter(prefix="/dashboard")
router.include_router(activate_escalation.router)
router.include_router(msg_sent_tod.router)
router.include_router(avg_resolution_time.router)
router.include_router(csat_score.router)
router.include_router(delivery_rate.router)
router.include_router(failed_message.router)

router.include_router(delivery_status.router)
router.include_router(channel_performance.router)