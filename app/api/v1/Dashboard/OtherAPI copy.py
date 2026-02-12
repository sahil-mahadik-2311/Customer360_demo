"""
Dashboard KPI Module - OOP, Exception Handling, Logging for Production
Calculates KPIs from messages.json data
"""

import json
import logging
from datetime import date , datetime
from pathlib import Path
from typing import Annotated, Dict, Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

# Existing project imports
from app.Database.session import get_db
from app.api.v1.Auth.auth import get_current_employee

# Dependencies (match past structure)

# Logging setup
logging.basicConfig(
    filename="LoggerFile.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filemode="a"  # append mode
)
logger = logging.getLogger(__name__)

# Router setup (extend existing or new)
router = APIRouter(prefix="/dashboard", tags=["dashboard"])




# ==================== KPI Service ====================
class KPIService:
    """Handles loading data and calculating KPIs"""

    def __init__(self):
        self.messages = self._load_messages()

    def _load_messages(self) -> List[Dict[str, Any]]:
        """
        Load messages from JSON file safely

        Raises:
            DataLoadError: If loading fails
        """
        try:
            if not KPIConfig.MESSAGES_JSON_PATH.is_file():
                raise FileNotFoundError(f"File not found: {KPIConfig.MESSAGES_JSON_PATH}")

            with KPIConfig.MESSAGES_JSON_PATH.open("r", encoding="utf-8") as f:
                data = json.load(f)

            if not isinstance(data, list):
                raise ValueError("Data must be a list of messages")

            logger.info(f"Loaded {len(data)} messages from JSON")
            return data

        except (FileNotFoundError, json.JSONDecodeError, ValueError) as e:
            logger.error(f"Data load error: {str(e)}")
            raise DataLoadError(f"Failed to load data: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected data load error: {str(e)}")
            raise DataLoadError(f"Unexpected error: {str(e)}")

    def _get_today_messages(self) -> List[Dict[str, Any]]:
        """Filter messages for today only"""
        today = date.today()
        return [
            msg for msg in self.messages
            if msg.get("datetime") and datetime.fromisoformat(msg["datetime"]).date() == today
        ]

    

# ==================== Dependencies ====================
def get_kpi_service() -> KPIService:
    """Dependency to get KPI service instance"""
    return KPIService()

kpi_dependency = Annotated[KPIService, Depends(get_kpi_service)]


# ==================== API Endpoints ====================
@router.get("/delivery-rate", response_model=float)
async def delivery_rate(
    emp: emp_dependency,
    db: db_dependency,
    kpi: kpi_dependency
):
    if emp is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed")

    logger.info("delivery-rate endpoint called")
    return kpi.get_delivery_rate()

