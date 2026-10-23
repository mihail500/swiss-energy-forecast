import numpy as np
import pandas as pd
def _swiss_times(times):
    times = pd.DatetimeIndex(times)
    if times.tz is None or times.hasnans:
        raise ValueError("Feature timestamps must be timezone-aware and not missing.")
    return times.tz_convert("Europe/Zurich")


def calendar_features(local_times):
    """Build 168 Swiss weekday/hour indicators and two annual cycle features.

    Both occurrences of an autumn repeated local hour share features.
    UTC inputs are converted to Swiss time before feature calculation.
    """
    local_times = _swiss_times(local_times)
    hour_of_week = local_times.dayofweek * 24 + local_times.hour
    weekly_profile = np.eye(168)[hour_of_week]
    days_in_year = np.where(local_times.is_leap_year, 366, 365)
    year_fraction = (
        local_times.dayofyear - 1 + local_times.hour / 24
    ) / days_in_year
    angle = 2 * np.pi * np.asarray(year_fraction)
    return np.column_stack([
        weekly_profile, np.sin(angle), np.cos(angle),
    ])


def holiday_indicator(local_times):
    """Mark January 1 and December 25-26; not a complete holiday calendar."""
    local_times = _swiss_times(local_times)
    return np.asarray(
        ((local_times.month == 1) & (local_times.day == 1))
        | ((local_times.month == 12) & np.isin(local_times.day, [25, 26])),
        dtype=float,
    )
