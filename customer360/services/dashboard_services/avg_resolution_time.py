from ...utils.exceptions import CalculationError
from ...utils.logger import logger
from typing import List
from datetime import date, datetime
from ...core.config import Setting
import json

class AverageResolutionTime:
    
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

    def get_avg_resolution_time(self) -> float:
        """
        Average resolution time in seconds for resolved messages today

        Returns:
            Float rounded to 1 decimal
        """
        try:
            messages = self._get_today_messages()
            times: List[float] = [
                msg["resolution_time_seconds"]
                for msg in messages
                if msg.get("resolved") and isinstance(msg.get("resolution_time_seconds"), (int, float))
            ]

            if not times:
                return 0.0

            avg = sum(times) / len(times)
            return round(avg, 1)

        except Exception as e:
            logger.error(f"Avg resolution time calculation error: {str(e)}")
            raise CalculationError(f"Failed to calculate avg resolution time: {str(e)}")
