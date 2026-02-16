from ...utils.exceptions import CalculationError
from ...utils.logger import logger
from datetime import date, datetime, timedelta
from ...core.config import Setting
import json
from typing import List, Dict, Any, Optional


class VolumeTrendsService:
    """Handles message volume trends calculation by period and channels."""

    def _load_messages(self) -> List[Dict[str, Any]]:
        path = Setting.MESSAGES_JSON_PATH
        if not path.is_file():
            logger.warning(f"Messages file not found: {path}")
            return []

        try:
            with path.open("r", encoding="utf-8") as f:
                data = json.load(f)
            return data if isinstance(data, list) else []
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            return []
        except Exception as e:
            logger.error(f"Failed to load messages: {e}")
            return []

    def _get_date_range(self, period: str) -> tuple[date, date]:
        today = date.today()
        ranges = {
            "today": (today, today),
            "7days": (today - timedelta(days=6), today),
            "30days": (today - timedelta(days=29), today),
            "90days": (today - timedelta(days=89), today),
        }
        if period not in ranges:
            raise ValueError(f"Invalid period: {period}")
        return ranges[period]

    def _filter_messages(
        self,
        messages: List[Dict[str, Any]],
        start_date: date,
        end_date: date,
        channels: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        filtered = []
        for msg in messages:
            dt_str = msg.get("datetime")
            if not dt_str:
                continue
            try:
                msg_date = datetime.fromisoformat(dt_str).date()
                if start_date <= msg_date <= end_date:
                    ch = msg.get("channel")
                    if channels is None or ch in channels:
                        filtered.append(msg)
            except (ValueError, TypeError):
                continue
        return filtered

    def _aggregate_daily(self, messages: List[Dict[str, Any]]) -> Dict[str, Dict[str, int]]:
        daily = {}
        hour_counts = {}

        for msg in messages:
            dt = datetime.fromisoformat(msg["datetime"])
            day_str = dt.date().isoformat()
            hour = dt.hour

            if day_str not in daily:
                daily[day_str] = {"sent": 0, "delivered": 0, "failed": 0}

            daily[day_str]["sent"] += 1
            status = msg.get("status")
            if status == "DELIVERED":
                daily[day_str]["delivered"] += 1
            elif status == "FAILED":
                daily[day_str]["failed"] += 1

            hour_counts[hour] = hour_counts.get(hour, 0) + 1

        return daily, hour_counts

    def get_volume_trends(
        self,
        period: str = "7days",
        channels: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Returns daily volume trends with totals, rates, peak hour, and spike note.
        """
        try:
            all_msgs = self._load_messages()
            if not all_msgs:
                return {"data": [], "peak_hour": None, "note": "No data available"}

            start_date, end_date = self._get_date_range(period)
            filtered = self._filter_messages(all_msgs, start_date, end_date, channels)

            if not filtered:
                return {"data": [], "peak_hour": None, "note": "No messages in period"}

            daily, hour_counts = self._aggregate_daily(filtered)

            # Build result list (sorted by date)
            trends = []
            total_sent = total_delivered = 0

            for day_str in sorted(daily):
                d = daily[day_str]
                sent = d["sent"]
                delivered = d["delivered"]
                failed = d["failed"]
                failure_rate = round(failed / sent * 100, 1) if sent > 0 else 0.0

                total_sent += sent
                total_delivered += delivered

                trends.append({
                    "date": day_str,
                    "sent": sent,
                    "delivered": delivered,
                    "failed": failed,
                    "failure_rate": failure_rate,
                })

            # Peak hour
            peak_hour = max(hour_counts, key=hour_counts.get, default=None)
            peak_str = f"{peak_hour:02d}:00 – {peak_hour+1:02d}:00" if peak_hour is not None else None

            return {
                "data": trends,
                "peak_hour": peak_str,
                "total_sent": total_sent,
                "total_delivered": total_delivered,
                "total_failure_rate": round((1 - total_delivered / total_sent) * 100, 1) if total_sent > 0 else 0.0,
            }

        except ValueError as ve:
            logger.error(f"Invalid input: {ve}")
            raise CalculationError(str(ve))
        except Exception as e:
            logger.error(f"Volume trends failed: {e}", exc_info=True)
            raise CalculationError(f"Failed to calculate trends: {str(e)}")


def get_volume_trends_service() -> VolumeTrendsService:
    return VolumeTrendsService()