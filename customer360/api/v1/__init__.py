from fastapi import APIRouter
from . import auth
from . import Dashboard

router = APIRouter(prefix="/api/v1")
router.include_router(auth.router)
router.include_router(Dashboard.router)