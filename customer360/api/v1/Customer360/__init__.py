from fastapi import APIRouter

from .customer import  router as customer_router
from .loanbycustID import  router as loanbycustID_router
from .loanbyloanID import  router as loanbyloanID_router


router = APIRouter(prefix="/Customer 360")


router.include_router(customer_router)
router.include_router(loanbycustID_router)
router.include_router(loanbyloanID_router)
