from fastapi import APIRouter
from . import v1
from .dependencies import db_dependency, emp_dependency

router = APIRouter()
router.include_router(v1.router)