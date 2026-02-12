from typing import List
from ...utils.exceptions import CalculationError
from ...utils.logger import logger



class CSAT_Score:
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
