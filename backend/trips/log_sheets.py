"""
Calendar-day slicing for HOS segments.

Converts elapsed-hour segments into wall-clock datetimes and groups them
by calendar day (midnight-to-midnight, naive-local). Segments that cross
a midnight boundary are split into two halves.
"""

from datetime import datetime, timedelta
from dataclasses import replace
from .hos import Segment


def _round_to_second(dt: datetime) -> datetime:
    """Round a datetime to the nearest whole second."""
    return (dt + timedelta(microseconds=500_000)).replace(microsecond=0)


def split_by_calendar_day(
    segments: list[Segment], start_datetime: datetime
) -> dict[datetime, list[Segment]]:
    """Group segments by calendar day, splitting any that span midnight.

    Parameters
    ----------
    segments : list[Segment]
        Ordered segments from ``calculate_hos()``. Each segment's ``start``
        and ``end`` are elapsed hours from trip start.
    start_datetime : datetime
        The wall-clock time the trip begins (naive-local).

    Returns
    -------
    dict[date, list[Segment]]
        Keys are ``date`` objects. Values are lists of segments (or
        segment-halves) whose wall-clock times fall on that calendar day,
        in chronological order. Each returned segment's ``start`` and ``end``
        are hour-of-day values (0-24) within that calendar day, not elapsed
        hours since trip start.
    """
    if not segments:
        return {}

    def _elapsed_to_dt(elapsed_hours: float) -> datetime:
        return start_datetime + timedelta(hours=elapsed_hours)

    def _date_key(dt: datetime) -> datetime:
        return dt.date()

    def _make_half(seg: Segment, start_dt: datetime, end_dt: datetime) -> Segment:
        midnight = start_dt.replace(hour=0, minute=0, second=0, microsecond=0)
        start_hod = (start_dt - midnight).total_seconds() / 3600
        end_hod = (end_dt - midnight).total_seconds() / 3600
        return replace(
            seg,
            start=round(start_hod, 4),
            end=round(end_hod, 4),
        )

    day_map: dict[datetime, list[Segment]] = {}

    for seg in segments:
        seg_start_dt = _elapsed_to_dt(seg.start)
        seg_end_dt = _elapsed_to_dt(seg.end)

        # Walk through each midnight boundary that this segment crosses
        boundary = seg_start_dt.replace(
            hour=0, minute=0, second=0, microsecond=0
        ) + timedelta(days=1)

        current_start_dt = seg_start_dt
        current_elapsed = seg.start

        while boundary < seg_end_dt:
            boundary = _round_to_second(boundary)
            # First half: current position → midnight
            half1 = _make_half(seg, current_start_dt, boundary)
            dk = _date_key(current_start_dt)
            day_map.setdefault(dk, []).append(half1)

            # Move to the next day
            current_start_dt = boundary
            current_elapsed = (boundary - start_datetime).total_seconds() / 3600
            boundary += timedelta(days=1)

        # Final portion (or the whole segment if no split was needed)
        remaining = _make_half(seg, current_start_dt, seg_end_dt)
        dk = _date_key(current_start_dt)
        day_map.setdefault(dk, []).append(remaining)

    return dict(sorted(day_map.items()))
