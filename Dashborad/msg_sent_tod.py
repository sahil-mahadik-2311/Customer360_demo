import logging

from Raw_data.json_data import today_msgs


from fastapi import APIRouter

logging.basicConfig(
    filename="LoggerFile.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

router = APIRouter()


@router.get("/dashboard/msg-sent-tod")
async def message_sent_today():
    logging.info("msg-sent-avg endpoint called")
    total = today_msgs()
    return f"Message Sent Today : {total}" 

