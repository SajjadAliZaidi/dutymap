"""
Calendar-day slicing for HOS segments.

Converts elapsed-hour segments into wall-clock datetimes and groups them
by calendar day (midnight-to-midnight, naive-local). Segments that cross
a midnight boundary are split into two halves.
"""

from datetime import datetime, timedelta
from dataclasses import replace
from .hos import Segment


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
        in chronological order.
    """
    if not segments:
        return {}

    def _elapsed_to_dt(elapsed_hours: float) -> datetime:
        return start_datetime + timedelta(hours=elapsed_hours)

    def _date_key(dt: datetime) -> datetime:
        return dt.date()

    def _make_half(seg: Segment, new_start: float, new_end: float) -> Segment:
        return replace(seg, start=round(new_start, 4), end=round(new_end, 4))

    day_map: dict[datetime, list[Segment]] = {}

    for seg in segments:
        seg_start_dt = _elapsed_to_dt(seg.start)
        seg_end_dt = _elapsed_to_dt(seg.end)

        # Elapsed hours at each midnight boundary relative to trip start
        first_midnight = seg_start_dt.replace(
            hour=0, minute=0, second=0, microsecond=0
        ) + timedelta(days=1)
        # How many elapsed hours from trip start to this midnight
        midnight_elapsed = (first_midnight - start_datetime).total_seconds() / 3600

        current_elapsed = seg.start

        # Walk through each midnight boundary that this segment crosses
        boundary = first_midnight
        while boundary < seg_end_dt:
            boundary_elapsed = (boundary - start_datetime).total_seconds() / 3600
            # First half: current position → midnight
            half1 = _make_half(seg, current_elapsed, boundary_elapsed)
            dk = _date_key(_elapsed_to_dt(current_elapsed))
            day_map.setdefault(dk, []).append(half1)

            current_elapsed = boundary_elapsed
            boundary += timedelta(days=1)

        # Final portion (or the whole segment if no split was needed)
        remaining = _make_half(seg, current_elapsed, seg.end)
        dk = _date_key(_elapsed_to_dt(current_elapsed))
        day_map.setdefault(dk, []).append(remaining)

    return dict(sorted(day_map.items()))


if __name__ == "__main__":
    from datetime import datetime

    print("=" * 60)
    print("TEST: Segment crossing midnight")
    print("=" * 60)

    # A trip starting at 2026-09-11 18:00 (6 PM).
    # We build two synthetic segments:
    #   1. Driving from t=0 to t=4 (18:00–22:00 on Sep 11)
    #   2. 10-hr rest from t=4 to t=14 (22:00 Sep 11 – 08:00 Sep 12) ← crosses midnight
    start = datetime(2026, 9, 11, 18, 0)
    segs = [
        Segment(day_number=1, status="driving", start=0.0, end=4.0, label="Driving"),
        Segment(day_number=1, status="off_duty", start=4.0, end=14.0, label="10-hr rest"),
        Segment(day_number=2, status="driving", start=14.0, end=18.0, label="Driving"),
    ]

    result = split_by_calendar_day(segs, start)

    print(f"\nStart datetime: {start}")
    print(f"Segments input:")
    for s in segs:
        s_start = start + timedelta(hours=s.start)
        s_end = start + timedelta(hours=s.end)
        print(f"  {s.label:<12} {s_start} → {s_end}  ({s.duration}h)")

    print(f"\nResult: {len(result)} calendar day(s)")
    for day, day_segs in result.items():
        print(f"\n  {day}:")
        for s in day_segs:
            s_start = start + timedelta(hours=s.start)
            s_end = start + timedelta(hours=s.end)
            print(f"    {s.status:<24} {s_start.strftime('%H:%M')}–{s_end.strftime('%H:%M')}  ({s.duration}h)  {s.label}")

    # Assertions
    assert len(result) == 2, f"Expected 2 days, got {len(result)}"
    sep11 = datetime(2026, 9, 11).date()
    sep12 = datetime(2026, 9, 12).date()

    assert sep11 in result, "Missing Sep 11"
    assert sep12 in result, "Missing Sep 12"

    # Sep 11 should have: Driving (4h), first half of rest
    d11 = result[sep11]
    assert len(d11) == 2, f"Sep 11: expected 2 segments, got {len(d11)}"
    assert d11[0].label == "Driving"
    assert d11[0].start == 0.0
    assert d11[0].end == 4.0
    assert d11[1].label == "10-hr rest"
    # Rest first half: 22:00–00:00 = 2 hours
    assert d11[1].end - d11[1].start == 2.0, (
        f"First half of rest should be 2h, got {d11[1].end - d11[1].start}"
    )

    # Sep 12 should have: second half of rest, Driving
    d12 = result[sep12]
    assert len(d12) == 2, f"Sep 12: expected 2 segments, got {len(d12)}"
    assert d12[0].label == "10-hr rest"
    # Second half: 00:00–08:00 = 8 hours, starting at elapsed t=6
    assert d12[0].start == 6.0
    assert d12[0].end - d12[0].start == 8.0, (
        f"Second half of rest should be 8h, got {d12[0].end - d12[0].start}"
    )
    assert d12[1].label == "Driving"
    assert d12[1].start == 14.0
    assert d12[1].end == 18.0

    # Total duration preserved
    total = sum(s.duration for day_segs in result.values() for s in day_segs)
    expected = sum(s.duration for s in segs)
    assert abs(total - expected) < 0.01, f"Duration mismatch: {total} vs {expected}"

    # No segment lost its day_number
    for day_segs in result.values():
        for s in day_segs:
            assert s.day_number in (1, 2), f"Unexpected day_number: {s.day_number}"

    print("\n  ✓ PASS")
