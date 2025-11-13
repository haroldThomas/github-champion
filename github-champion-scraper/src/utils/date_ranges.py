from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple

ISO_FORMAT = "%Y-%m-%d"

@dataclass
class DateRange:
    since: datetime
    until: datetime

    def as_iso_strings(self) -> Tuple[str, str]:
        return self.since.strftime(ISO_FORMAT), self.until.strftime(ISO_FORMAT)

def _parse_date(date_str: str) -> datetime:
    """
    Parse a YYYY-MM-DD string into an aware datetime in UTC.
    """
    return datetime.strptime(date_str, ISO_FORMAT).replace(tzinfo=timezone.utc)

def _today_utc() -> datetime:
    return datetime.now(timezone.utc)

def preset_to_range(preset: str) -> DateRange:
    """
    Map human-friendly presets to a concrete DateRange.
    Supported presets:
        - last_7_days
        - last_30_days
        - last_90_days
        - this_month
        - this_year
    """
    preset = preset.lower()
    now = _today_utc()

    if preset == "last_7_days":
        until = now
        since = until - timedelta(days=7)
    elif preset == "last_30_days":
        until = now
        since = until - timedelta(days=30)
    elif preset == "last_90_days":
        until = now
        since = until - timedelta(days=90)
    elif preset == "this_month":
        first_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        since = first_of_month
        until = now
    elif preset == "this_year":
        first_of_year = now.replace(
            month=1, day=1, hour=0, minute=0, second=0, microsecond=0
        )
        since = first_of_year
        until = now
    else:
        raise ValueError(f"Unsupported date preset: {preset}")

    return DateRange(since=since, until=until)

def parse_date_range(
    preset: Optional[str] = None,
    since_str: Optional[str] = None,
    until_str: Optional[str] = None,
) -> DateRange:
    """
    Resolve a date range from either explicit dates or a preset.

    Precedence:
        1. since_str and until_str (both required if provided)
        2. preset
        3. default to last_30_days
    """
    if since_str and until_str:
        since = _parse_date(since_str)
        until = _parse_date(until_str)
        if since > until:
            raise ValueError("since date must be <= until date")
        return DateRange(since=since, until=until)

    if preset:
        return preset_to_range(preset)

    # Default
    return preset_to_range("last_30_days")