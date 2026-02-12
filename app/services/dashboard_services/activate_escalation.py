from ...utils.exceptions import CalculationError
from ...utils.logger import logger


class ActiveEscalation:

    def get_active_escalations(self) -> int:
        """
        Count active (escalated and unresolved) today

        Returns:
            Integer count
        """
        try:
            messages = self._get_today_messages()
            return sum(1 for msg in messages if msg.get("escalated") and not msg.get("resolved"))

        except Exception as e:
            logger.error(f"Active escalations calculation error: {str(e)}")
            raise CalculationError(f"Failed to calculate active escalations: {str(e)}")
