"""
Top Issues Service
Aggregates top issues by volume over last 7 days
Includes affected channel and % change vs previous 7 days
"""

from ...utils.exceptions import CalculationError
from ...utils.logger import logger
from datetime import date, datetime, timedelta
from ...core.config import Setting
import json
from typing import List, Dict, Any, Optional
from collections import Counter


class TopIssuesService:
    
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

    def _get_date_range(self, days_back: int) -> tuple[date, date]:
        today = date.today()
        start = today - timedelta(days=days_back - 1)
        return start, today

    def _filter_messages(
        self,
        messages: List[Dict[str, Any]],
        start_date: date,
        end_date: date,
    ) -> List[Dict[str, Any]]:
        filtered = []
        for msg in messages:
            dt_str = msg.get("datetime")
            if not dt_str:
                continue
            try:
                msg_date = datetime.fromisoformat(dt_str).date()
                if start_date <= msg_date <= end_date and msg.get("issue_type"):
                    filtered.append(msg)
            except (ValueError, TypeError):
                continue
        return filtered

    def _aggregate_issues(self, messages: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        issues = {}
        for msg in messages:
            issue_type = msg["issue_type"]
            if issue_type not in issues:
                issues[issue_type] = {
                    "volume": 0,
                    "channels": Counter()
                }
            issues[issue_type]["volume"] += 1
            ch = msg.get("channel")
            if ch:
                issues[issue_type]["channels"][ch] += 1
        return issues

    def get_top_issues(self) -> List[Dict[str, Any]]:
        """
        Returns top issues ranked by volume (desc) for last 7 days.
        Includes: issue_type, volume, primary_channel, percent_change vs previous 7 days.
        """
        try:
            all_msgs = self._load_messages()
            if not all_msgs:
                return []

            # Current period: last 7 days
            curr_start, curr_end = self._get_date_range(7)
            curr_filtered = self._filter_messages(all_msgs, curr_start, curr_end)
            curr_issues = self._aggregate_issues(curr_filtered)

            # Previous period: days 8-14 before today
            prev_start = curr_start - timedelta(days=7)
            prev_end = curr_start - timedelta(days=1)
            prev_filtered = self._filter_messages(all_msgs, prev_start, prev_end)
            prev_issues = self._aggregate_issues(prev_filtered)

            # Build result
            result = []
            for issue, data in curr_issues.items():
                volume = data["volume"]
                if volume == 0:
                    continue

                # Primary channel (most common)
                channels = data["channels"]
                primary_channel = max(channels, key=channels.get) if channels else None

                # Percent change
                prev_volume = prev_issues.get(issue, {"volume": 0})["volume"]
                if prev_volume == 0:
                    change = 100.0 if volume > 0 else 0.0
                else:
                    change = round(((volume - prev_volume) / prev_volume) * 100, 1)

                result.append({
                    "issue_type": issue,
                    "volume": volume,
                    "primary_channel": primary_channel,
                    "percent_change": change
                })

            # Sort by volume desc
            result.sort(key=lambda x: x["volume"], reverse=True)

            logger.info(f"Top issues calculated: {len(result)} issues")
            return result

        except Exception as e:
            logger.error(f"Top issues calculation failed: {e}")
            raise CalculationError(f"Failed to calculate top issues: {str(e)}")


def get_top_issues_service() -> TopIssuesService:
    return TopIssuesService()