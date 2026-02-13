from ...utils.exceptions import CalculationError
from ...utils.logger import logger
from datetime import date, datetime
from ...core.config import Setting
import json



class DeliveryRate:

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

    def get_delivery_rate(self) -> float:
        """
        Calculate delivery rate: (delivered / total) * 100

        Returns:
            Float rounded to 1 decimal

        Raises:
            CalculationError: If calculation fails
        """
        try:
            messages = self._get_today_messages()
            total = len(messages)
            if total == 0:
                return 0.0

            delivered = sum(1 for msg in messages if msg.get("status") == Setting.STATUS_DELIVERED)
            rate = (delivered / total) * 100
            return round(rate, 1)

        except Exception as e:
            logger.error(f"Delivery rate calculation error: {str(e)}")
            raise CalculationError(f"Failed to calculate delivery rate: {str(e)}")
