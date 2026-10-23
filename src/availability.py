"""Explicit modelling policy; this does not reconstruct historical releases."""

import pandas as pd


def assumed_maturity_utc(interval_starts):
    """Return next local month start plus six months, using hourly ends.

    An interval ending in February matures on September 1. An interval
    starting February 29 at 23:00 ends in March and matures on October 1.
    Inputs must be timezone-aware and represent hourly starts.
    """
    starts = pd.DatetimeIndex(interval_starts)
    if starts.tz is None or starts.hasnans:
        raise ValueError("Interval starts must be timezone-aware and not missing.")
    local_ends = (
        starts.tz_convert("UTC") + pd.Timedelta(hours=1)
    ).tz_convert("Europe/Zurich").tz_localize(None)
    maturity = (
        local_ends.to_period("M").to_timestamp()
        + pd.offsets.MonthBegin(1)
        + pd.DateOffset(months=6)
    )
    return maturity.tz_localize("Europe/Zurich").tz_convert("UTC")
