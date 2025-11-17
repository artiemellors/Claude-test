"""
Week Assembler - Collects designed workouts into structured week
"""
from typing import Dict, Any, List


class WeekAssembler:
    """Non-LLM agent that assembles completed workouts into a structured week"""

    def __init__(self):
        self.name = "week_assembler"

    def assemble(
        self,
        week_number: int,
        sessions: List[Dict[str, Any]],
        week_strategy: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Assemble all designed sessions into a complete week structure

        Args:
            week_number: Week number in the block
            sessions: List of completed session designs from specialist coaches
            week_strategy: Original strategy for this week

        Returns:
            Complete week structure with all sessions organized
        """
        # Sort sessions by day of week
        day_order = {
            "monday": 1, "tuesday": 2, "wednesday": 3, "thursday": 4,
            "friday": 5, "saturday": 6, "sunday": 7
        }
        sorted_sessions = sorted(sessions, key=lambda s: day_order.get(s.get("dayOfWeek", "monday"), 1))

        # Calculate week-level metrics
        total_duration = sum(self._extract_duration(s) for s in sorted_sessions)
        session_count = len(sorted_sessions)

        # Count sessions by type
        session_types = {}
        for session in sorted_sessions:
            session_type = session.get("sessionType", "unknown")
            session_types[session_type] = session_types.get(session_type, 0) + 1

        # Identify rest days
        scheduled_days = {s.get("dayOfWeek") for s in sorted_sessions}
        all_days = {"monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"}
        rest_days = list(all_days - scheduled_days)

        return {
            "weekNumber": week_number,
            "weekStrategy": week_strategy,
            "sessions": sorted_sessions,
            "weekMetrics": {
                "totalSessions": session_count,
                "totalDurationMinutes": total_duration,
                "sessionsByType": session_types,
                "restDays": sorted(rest_days, key=lambda d: day_order[d])
            },
            "weekStatus": "assembled"
        }

    def _extract_duration(self, session: Dict[str, Any]) -> int:
        """Extract estimated duration in minutes from a session"""
        # Try to get duration from workout
        workout = session.get("workout", {})

        # Check for totalDuration field
        total_duration = workout.get("totalDuration", "")
        if total_duration:
            # Try to parse duration like "45min", "60-75min", etc.
            import re
            match = re.search(r'(\d+)', str(total_duration))
            if match:
                return int(match.group(1))

        # Try sessionConstraints
        constraints = session.get("sessionConstraints", {})
        duration = constraints.get("duration", "")
        if duration:
            match = re.search(r'(\d+)', str(duration))
            if match:
                return int(match.group(1))

        # Default estimate based on session type
        session_type = session.get("sessionType", "")
        defaults = {
            "runningQuality": 50,
            "maxStrength": 70,
            "strengthEndurance": 60,
            "hyroxCombo": 65,
            "recovery": 30
        }
        return defaults.get(session_type, 60)
