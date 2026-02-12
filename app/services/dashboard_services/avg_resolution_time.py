from ...utils.exceptions import CalculationError
from ...utils.logger import logger
from typing import List

class AverageResolutionTime:

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
