

from .customer import  router as customer_router
from .loanbycustID import  router as loanbycustID_router
from .loanbyloanID import  router as loanbyloanID_router

__all__ = ["customer_router",
           "loanbycustID_router",
           "loanbyloanID_router"
           ]



