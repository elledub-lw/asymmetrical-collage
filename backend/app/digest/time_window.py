"""
Time window calculation for Market Watch newsletter.
Calculates a rolling 24-hour window anchored to Paris time (18:00 cycle).
"""

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo


PARIS_TZ = ZoneInfo("Europe/Paris")
UTC_TZ = ZoneInfo("UTC")


def get_time_window() -> dict:
    """
    Calculate the 24-hour news window anchored to 18:00 Paris time.

    The window runs from 18:00 Paris yesterday to 18:00 Paris today.
    This accounts for CET (UTC+1) and CEST (UTC+2) dynamically.

    Returns:
        dict with startISO, endISO, startDate, endDate, todayStr
    """
    # Current time in Paris
    now_paris = datetime.now(PARIS_TZ)

    # Today's 18:00 Paris time
    today_anchor = now_paris.replace(hour=18, minute=0, second=0, microsecond=0)

    # If we haven't reached 18:00 today, use yesterday's anchor as end
    if now_paris < today_anchor:
        end_time = today_anchor
        start_time = today_anchor - timedelta(days=1)
    else:
        # We're past 18:00, so window is from today's 18:00 to tomorrow's 18:00
        # But for the digest, we want the completed window
        end_time = today_anchor
        start_time = today_anchor - timedelta(days=1)

    # Convert to UTC for API calls
    start_utc = start_time.astimezone(UTC_TZ)
    end_utc = end_time.astimezone(UTC_TZ)

    return {
        "startISO": start_utc.isoformat(),
        "endISO": end_utc.isoformat(),
        "startDate": start_time.strftime("%Y-%m-%d"),
        "endDate": end_time.strftime("%Y-%m-%d"),
        "todayStr": end_time.strftime("%B %d, %Y"),  # e.g., "February 11, 2026"
        "dateISO": end_time.strftime("%Y-%m-%d"),    # For database storage
    }


def is_weekend() -> bool:
    """Check if today is Saturday (5) or Sunday (6) in Paris time."""
    now_paris = datetime.now(PARIS_TZ)
    return now_paris.weekday() in (5, 6)


def get_today_iso() -> str:
    """Get today's date in ISO format (YYYY-MM-DD) in Paris timezone."""
    now_paris = datetime.now(PARIS_TZ)
    return now_paris.strftime("%Y-%m-%d")
