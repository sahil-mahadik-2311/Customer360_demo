from ...utils.exceptions import CalculationError
from ...utils.logger import logger

from core.config import Setting




class DeliveryRate:


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
