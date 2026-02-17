from fastapi import APIRouter

from . import customer ,  loanbycustID , loanbyloanID

router = APIRouter(prefix="/Customer 360")


router.include_router(customer.router)
router.include_router(loanbycustID.router)
router.include_router(loanbyloanID.router)
