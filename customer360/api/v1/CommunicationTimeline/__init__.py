from fastapi import APIRouter

from . import customer_details

router = APIRouter(prefix="/Communication Timeline")


router.include_router(customer_details.router)