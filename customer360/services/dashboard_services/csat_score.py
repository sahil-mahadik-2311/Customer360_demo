from typing import List
from ...utils.exceptions import CalculationError
from ...utils.logger import logger
from datetime import date, datetime
from ...core.config import Setting
import json


class CSAT_Score:
    
    def _get_today_messages(self):
        """Load messages from JSON file and filter by today's date"""
        try:
            if not Setting.MESSAGES_JSON_PATH.is_file():
                logger.warning(f"Messages file not found: {Setting.MESSAGES_JSON_PATH}")
                return []
            
            with Setting.MESSAGES_JSON_PATH.open("r", encoding="utf-8") as f:
                data = json.load(f)
                if not isinstance(data, list):
                    return []
                
                today = date.today()
                today_messages = []
                for msg in data:
                    try:
                        datetime_str = msg.get("datetime")
                        if datetime_str:
                            msg_datetime = datetime.fromisoformat(datetime_str)
                            if msg_datetime.date() == today:
                                today_messages.append(msg)
                    except (ValueError, TypeError):
                        continue
                return today_messages
        except Exception as e:
            logger.error(f"Error loading messages: {str(e)}")
            return []
    
    def get_csat_score(self) -> float:
        """
        Average CSAT score (assuming 0-100 scale) today

        Returns:
            Float rounded to 1 decimal
        """
        try:
            messages = self._get_today_messages()
            scores: List[float] = [
                msg["csat_score"]
                for msg in messages
                if isinstance(msg.get("csat_score"), (int, float))
            ]

            if not scores:
                return 0.0

            avg = sum(scores) / len(scores)
            return round(avg, 1)

        except Exception as e:
            logger.error(f"CSAT score calculation error: {str(e)}")
            raise CalculationError(f"Failed to calculate CSAT score: {str(e)}")
