from fastapi import APIRouter
from . import auth

from .Dashboard import kpi_router
from .Dashboard import delivery_status_router
from .Dashboard import message_volume_trends_router
from .Dashboard import resolution_time_trend_router
from .Dashboard import top_issue_router
from .Dashboard import channel_router

from .Customer360 import customer_router
from .Customer360 import loanbycustID_router
from .Customer360 import loanbyloanID_router

from .CommunicationTimeline import  customer_details_router

router = APIRouter(prefix="/api/v1")

router.include_router(auth.router)


router.include_router(kpi_router)
router.include_router(delivery_status_router)
router.include_router(message_volume_trends_router)
router.include_router(top_issue_router)
router.include_router(resolution_time_trend_router)
router.include_router(channel_router)

router.include_router(customer_router)
router.include_router(loanbycustID_router)
router.include_router(loanbyloanID_router)

router.include_router(customer_details_router)