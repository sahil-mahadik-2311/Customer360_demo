"""
Resolution Time Trend Service
Calculates resolution time metrics by timeline and channel
Includes per-bucket details for hover and overall improvement
"""

from ...utils.exceptions import CalculationError
from ...utils.logger import logger
from datetime import datetime, date, timedelta
from ...core.config import Setting
import json
from typing import List, Dict, Any, Optional
from statistics import mean, median
from collections import Counter


class ResolutionTimeTrendService:
    
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

    def _get_date_range(self, timeline: str) -> tuple[datetime, datetime]:
        now = datetime.now()
        if timeline == "24h":
            start = now - timedelta(hours=24)
        elif timeline == "7days":
            start = now - timedelta(days=7)
        elif timeline == "30days":
            start = now - timedelta(days=30)
        else:
            raise ValueError(f"Invalid timeline: {timeline}")
        return start, now

    def _filter_messages(
        self,
        messages: List[Dict[str, Any]],
        start: datetime,
        end: datetime,
        channel: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        filtered = []
        for msg in messages:
            dt_str = msg.get("datetime")
            res_time = msg.get("resolution_time_seconds")
            if not dt_str or not isinstance(res_time, (int, float)) or res_time <= 0:
                continue
            try:
                msg_dt = datetime.fromisoformat(dt_str)
                if start <= msg_dt <= end and msg.get("status") == "RESOLVED":
                    ch = msg.get("channel")
                    if channel is None or ch == channel:
                        filtered.append(msg)
            except (ValueError, TypeError):
                continue
        return filtered

    def _bucket_messages(
        self,
        messages: List[Dict[str, Any]],
        timeline: str,
    ) -> Dict[str, List[Dict[str, Any]]]:
        buckets = {}
        for msg in messages:
            dt = datetime.fromisoformat(msg["datetime"])
            if timeline == "24h":
                bucket_key = dt.strftime("%H:00")  # hourly
            else:
                bucket_key = dt.date().isoformat()  # daily
            buckets.setdefault(bucket_key, []).append(msg)
        return buckets

    def _calculate_improvement(self, current_avg: float, previous_avg: float) -> float:
        if previous_avg == 0:
            return 0.0
        return round(((previous_avg - current_avg) / previous_avg) * 100, 1)

    def get_resolution_trend(
        self,
        timeline: str = "7days",
        channel: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Returns resolution time trend data.
        - timeline: 24h | 7days | 30days
        - channel: optional single channel (or None for all)
        Buckets by hour (24h) or day (others)
        Includes per-bucket hover details and overall improvement
        """
        try:
            all_msgs = self._load_messages()
            if not all_msgs:
                return {"data": [], "improvement": 0.0, "note": "No data available"}

            curr_start, curr_end = self._get_date_range(timeline)
            curr_filtered = self._filter_messages(all_msgs, curr_start, curr_end, channel)

            if not curr_filtered:
                return {"data": [], "improvement": 0.0, "note": "No resolutions in period"}

            # Aggregate per bucket
            buckets = self._bucket_messages(curr_filtered, timeline)
            trends = []

            total_res_times = []
            resolved_count = len(curr_filtered)

            for bucket_key in sorted(buckets):
                bucket_msgs = buckets[bucket_key]
                res_times = [m["resolution_time_seconds"] for m in bucket_msgs]

                if not res_times:
                    continue

                avg = round(mean(res_times) / 60, 1)  # in minutes
                fastest = min(res_times) / 60
                slowest = max(res_times) / 60

                # Top cause
                causes = Counter(m.get("issue_type") for m in bucket_msgs if m.get("issue_type"))
                top_cause = causes.most_common(1)
                top_cause_type = top_cause[0][0] if top_cause else None
                top_cause_pct = round(top_cause[0][1] / len(bucket_msgs) * 100, 1) if top_cause else 0.0

                # SLA (assume SLA threshold = 30 min, adjust if needed)
                sla_met = round(sum(t/60 < 30 for t in res_times) / len(res_times) * 100, 1)

                trends.append({
                    "bucket": bucket_key,
                    "avg_resolution": avg,
                    "sla_met": sla_met,
                    "fastest": round(fastest, 1),
                    "slowest": round(slowest, 1),
                    "resolved": len(bucket_msgs),
                    "top_cause": {
                        "type": top_cause_type,
                        "percentage": top_cause_pct
                    }
                })

                total_res_times.extend(res_times)

            if not trends:
                return {"data": [], "improvement": 0.0, "note": "No resolutions in period"}

            # Overall avg for current period (in minutes)
            current_avg = round(mean(total_res_times) / 60, 1)

            # Previous period for improvement (same length as current)
            prev_end = curr_start - timedelta(seconds=1)
            prev_start = prev_end - (curr_end - curr_start)
            prev_filtered = self._filter_messages(all_msgs, prev_start, prev_end, channel)
            prev_res_times = [m["resolution_time_seconds"] for m in prev_filtered]

            previous_avg = mean(prev_res_times) / 60 if prev_res_times else 0.0
            improvement = self._calculate_improvement(current_avg, previous_avg)

            note = f"Resolution Time Improved by {improvement}% vs last {timeline.replace('h', ' hours').replace('days', ' days')}." if improvement > 0 else "No improvement in resolution time."

            return {
                "data": trends,
                "improvement": improvement,
                "note": note,
                "total_resolved": resolved_count,
                "overall_avg": current_avg
            }

        except ValueError as ve:
            logger.error(f"Invalid input: {ve}")
            raise CalculationError(str(ve))
        except Exception as e:
            logger.error(f"Resolution trend failed: {e}", exc_info=True)
            raise CalculationError(f"Failed to calculate resolution trend: {str(e)}")


def get_resolution_trend_service() -> ResolutionTimeTrendService:
    return ResolutionTimeTrendService()