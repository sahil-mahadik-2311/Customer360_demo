from ...utils.exceptions import CalculationError
from ...utils.logger import logger
from datetime import date, datetime, timedelta
from ...core.config import Setting
import json


class DeliveryStatusService:
    
    def _get_period_messages(self, days_back: int = 7) -> list:
        """
        Load messages from JSON and filter by date range (today + previous days)
        Returns list of messages in the period
        """
        try:
            if not Setting.MESSAGES_JSON_PATH.is_file():
                logger.warning(f"Messages file not found: {Setting.MESSAGES_JSON_PATH}")
                return []
            
            with Setting.MESSAGES_JSON_PATH.open("r", encoding="utf-8") as f:
                data = json.load(f)
                if not isinstance(data, list):
                    logger.error("Messages data is not a list")
                    return []
                
                today = date.today()
                start_date = today - timedelta(days=days_back - 1)  # inclusive
                
                period_messages = []
                for msg in data:
                    try:
                        datetime_str = msg.get("datetime")
                        if datetime_str:
                            msg_datetime = datetime.fromisoformat(datetime_str)
                            msg_date = msg_datetime.date()
                            if start_date <= msg_date <= today:
                                period_messages.append(msg)
                    except (ValueError, TypeError):
                        continue
                
                return period_messages
                
        except Exception as e:
            logger.error(f"Error loading messages for delivery status: {str(e)}")
            return []

    def get_delivery_status(self) -> dict:
        """
        Calculate today's delivery counts and % change compared to previous 6 days
        
        Returns dict in format:
        {
            "delivered": {"count": float, "change": float},
            "failed":    {"count": float, "change": float},
            "pending":   {"count": float, "change": float}
        }
        """
        try:
            messages = self._get_period_messages(days_back=7)
            if not messages:
                return {
                    "delivered": {"count": 0, "change": 0.0},
                    "failed":    {"count": 0, "change": 0.0},
                    "pending":   {"count": 0, "change": 0.0}
                }

            today = date.today()
            today_messages = [m for m in messages if datetime.fromisoformat(m["datetime"]).date() == today]
            prev_messages  = [m for m in messages if datetime.fromisoformat(m["datetime"]).date() < today]

            def count_status(records: list, status: str) -> int:
                return sum(1 for m in records if m.get("status") == status)

            # Today's counts
            current = {
                "delivered": count_status(today_messages, "DELIVERED"),
                "failed":    count_status(today_messages, "FAILED"),
                "pending":   count_status(today_messages, "PENDING"),
            }

            # Previous period counts (last 6 days)
            previous = {
                "delivered": count_status(prev_messages, "DELIVERED"),
                "failed":    count_status(prev_messages, "FAILED"),
                "pending":   count_status(prev_messages, "PENDING"),
            }

            def percent_change(curr: int, prev: int) -> float:
                if prev == 0:
                    return 0.0 if curr == 0 else 100.0
                return round(((curr - prev) / prev) * 100, 1)

            result = {
                "delivered": {
                    "count": current["delivered"],
                    "change": percent_change(current["delivered"], previous["delivered"])
                },
                "failed": {
                    "count": current["failed"],
                    "change": percent_change(current["failed"], previous["failed"])
                },
                "pending": {
                    "count": current["pending"],
                    "change": percent_change(current["pending"], previous["pending"])
                }
            }

            logger.info(f"Delivery status calculated: {result}")
            return result

        except Exception as e:
            logger.error(f"Delivery status calculation error: {str(e)}")
            raise CalculationError(f"Failed to calculate delivery status: {str(e)}")

