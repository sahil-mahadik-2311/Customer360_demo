from pathlib import Path
from typing import List , Dict , Any
from ...utils.logger import logger
import json
from datetime import date , datetime
from core.config import Setting

class MessageService:
    def load_messages_from_json() -> List[Dict[str, Any]]:
        """
        Safely load messages list from JSON file.
        Returns empty list on any failure.
        """
        if not Setting.MESSAGES_JSON_PATH.is_file():
            logger.warning(f"Messages file not found: {Setting.MESSAGES_JSON_PATH}")
            return []

        try:
            with Setting.MESSAGES_JSON_PATH.open("r", encoding="utf-8") as f:
                data = json.load(f)
                if not isinstance(data, list):
                    logger.error("Messages data is not a list")
                    return []
                return data
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Failed to load messages file: {str(e)}")
            return []


    def count_messages_sent_today_by_employee(
        messages: List[Dict[str, Any]],
        employee_id: int
    ) -> int:
        """
        Count messages sent TODAY by the given employee.
        
        Expected message format (from your sample):
        {
            "message": "Welcome SMS sent to user",
            "status": "SENT",
            "datetime": "2026-02-09T10:15:22",
            "description": "Initial onboarding message delivered successfully"
            // possibly other fields like "employee_id" or "sender_id"
        }
        """
        today = date.today()
        count = 0

        for msg in messages:
            try:
                # Skip if not sent or no datetime
                """ if msg.get("status") != "SENT":
                    continue"""

                datetime_str = msg.get("datetime")
                if not datetime_str:
                    continue

                # Parse the datetime string (your format: "YYYY-MM-DDTHH:MM:SS")
                msg_datetime = datetime.fromisoformat(datetime_str)
                msg_date = msg_datetime.date()

                # Only count if sent today
                if msg_date != today:
                    continue

                # IMPORTANT: You need a field that identifies the employee
                # Here are common possibilities — choose / adjust one:
                sender_id = (
                    msg.get("employee_id") or
                    msg.get("sender_id") or
                    msg.get("emp_id") or
                    msg.get("created_by")
                )

                if sender_id is None:
                    logger.debug(f"Message missing employee identifier: {msg}")
                    continue

                # Convert to int if it's stored as string
                try:
                    sender_id = int(sender_id)
                except (ValueError, TypeError):
                    continue

                if sender_id == employee_id:
                    count += 1

            except ValueError as ve:
                # Invalid datetime format
                logger.debug(f"Invalid datetime in message: {msg.get('message', 'no message')} - {str(ve)}")
                continue
            except Exception as e:
                logger.debug(f"Error processing message: {str(e)}")
                continue

        return count

