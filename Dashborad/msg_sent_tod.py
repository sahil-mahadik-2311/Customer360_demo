import logging
from typing import Annotated 
from fastapi import APIRouter , Depends 
from sqlalchemy.orm import Session
from Database.init_db import get_db
from Auth.JWTauth import get_current_emp
from Raw_data.json_data import today_msgs

db_dependncy = Annotated[Session, Depends(get_db)]
emp_dependency = Annotated[dict, Depends(get_current_emp)]


logging.basicConfig(
    filename="LoggerFile.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

router = APIRouter()


@router.get("/dashboard/msg-sent-tod")
async def message_sent_today(emp: emp_dependency , 
                             db: db_dependncy):
    if emp is None:
        raise HTTPException(status_code=401, detail="Authenticatin Failed")

    logging.info("msg-sent-avg endpoint called")
    total = today_msgs()
    return f"Message Sent Today : {total}" 

