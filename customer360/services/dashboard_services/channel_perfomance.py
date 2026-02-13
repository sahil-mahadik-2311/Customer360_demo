"""
Channel Performance Service
Calculates volume, delivery rate, and avg resolution time per channel
Supports sorting by volume or delivery_rate
"""

from ...utils.exceptions import CalculationError
from ...utils.logger import logger
from datetime import datetime
import json
from ...core.config import Setting


class ChannelPerformanceService:
    
    def _get_all_messages(self):
        """Load all messages from JSON file"""
        try:
            if not Setting.MESSAGES_JSON_PATH.is_file():
                logger.warning(f"Messages file not found: {Setting.MESSAGES_JSON_PATH}")
                return []
            
            with Setting.MESSAGES_JSON_PATH.open("r", encoding="utf-8") as f:
                data = json.load(f)
                if not isinstance(data, list):
                    logger.error("Messages data is not a list")
                    return []
                
                return data
                
        except Exception as e:
            logger.error(f"Error loading messages: {str(e)}")
            return []

    def get_channel_performance(self, sort_by: str = "volume") -> list:
        """
        Calculate performance metrics per channel
        - Volume: total messages
        - Delivery Rate: (delivered / total) * 100, rounded to 1 decimal
        - Avg Resolution Time: average resolution_time_seconds for delivered, rounded to 1 decimal
        
        Sorts by 'volume' (desc) or 'delivery_rate' (desc)
        
        Returns list of dicts:
        [{"channel": "SMS", "volume": 21000, "delivery_rate": 95.8, "avg_time": 2.3}, ...]
        """
        try:
            messages = self._get_all_messages()
            if not messages:
                return []
            
            # Aggregate per channel
            channels = {}
            for msg in messages:
                channel = msg.get("channel")
                if not channel:
                    continue
                    
                if channel not in channels:
                    channels[channel] = {
                        "volume": 0,
                        "delivered_count": 0,
                        "resolution_times": []
                    }
                
                channels[channel]["volume"] += 1
                
                if msg.get("status") == "DELIVERED":
                    channels[channel]["delivered_count"] += 1
                    res_time = msg.get("resolution_time_seconds")
                    if isinstance(res_time, (int, float)):
                        channels[channel]["resolution_times"].append(res_time)
            
            # Calculate rates and avgs
            result = []
            for ch, data in channels.items():
                volume = data["volume"]
                if volume == 0:
                    continue
                    
                delivery_rate = round((data["delivered_count"] / volume) * 100, 1)
                
                avg_time = 0.0
                if data["resolution_times"]:
                    avg_time = round(sum(data["resolution_times"]) / len(data["resolution_times"]), 1)
                
                result.append({
                    "channel": ch,
                    "volume": volume,
                    "delivery_rate": delivery_rate,
                    "avg_time": avg_time
                })
            
            # Sort
            if sort_by == "delivery_rate":
                result.sort(key=lambda x: x["delivery_rate"], reverse=True)
            else:  # default volume desc
                result.sort(key=lambda x: x["volume"], reverse=True)
            
            logger.info(f"Channel performance calculated, sorted by {sort_by}: {len(result)} channels")
            return result

        except Exception as e:
            logger.error(f"Channel performance calculation error: {str(e)}")
            raise CalculationError(f"Failed to calculate channel performance: {str(e)}")


