from ...utils.exceptions import CalculationError
from ...utils.logger import logger

from core.config import Setting

class FailedMessage:
    
    def get_failed_messages(self) -> int:
            """
            Count failed messages today

            Returns:
                Integer count
            """
            try:
                messages = self._get_today_messages()
                return sum(1 for msg in messages if msg.get("status") == Setting.STATUS_FAILED)

            except Exception as e:
                logger.error(f"Failed messages calculation error: {str(e)}")
                raise CalculationError(f"Failed to calculate failed messages: {str(e)}")
