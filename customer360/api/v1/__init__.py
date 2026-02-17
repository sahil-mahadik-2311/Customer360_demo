from fastapi import APIRouter
from . import auth , Dashboard , CommunicationTimeline , Customer360


router = APIRouter(prefix="/api/v1")

router.include_router(auth.router)
router.include_router(Dashboard.router)
router.include_router(CommunicationTimeline.router)
router.include_router(Customer360.router)