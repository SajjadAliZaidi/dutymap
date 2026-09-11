"""
Hours of Service (HOS) calculation for property-carrying drivers.

70-hour / 8-day cycle. No adverse driving conditions.
"""

from dataclasses import dataclass


@dataclass
class Segment:
    day_number: int
    status: str  # "off_duty", "sleeper_berth", "driving", "on_duty_not_driving"
    start: float  # hours from trip start
    end: float
    label: str

    @property
    def duration(self):
        return round(self.end - self.start, 2)


DAY_DRIVING_LIMIT = 11
DAY_ON_DUTY_LIMIT = 14
BREAK_AFTER_DRIVING = 8
CYCLE_LIMIT = 70
OFF_DUTY_BETWEEN_DAYS = 10
RESTART_OFF_DUTY = 34
PICKUP_HOURS = 1
DROPOFF_HOURS = 1
BREAK_LENGTH = 0.5
FUEL_STOP_LENGTH = 0.5
FUEL_EVERY_MILES = 1000


def _estimate_on_duty_remaining(driving_hours: float, distance_miles: float, extra_stops_hours: float = 0.0) -> float:
    """Rough estimate of on-duty hours still needed (for cycle restart check)."""
    breaks = (driving_hours / BREAK_AFTER_DRIVING) * BREAK_LENGTH
    fuel_stops = (distance_miles / FUEL_EVERY_MILES) * FUEL_STOP_LENGTH
    return driving_hours + extra_stops_hours + breaks + fuel_stops


class _HosState:
    """Mutable scheduling state threaded through both driving legs and stops.

    `day_driving`/`day_on_duty`/`break_taken` describe the *current* duty
    day and persist across leg and stop boundaries — they only reset when a
    rest (10-hr or 34-hr) is actually taken, exactly as if the whole trip
    (leg 1, pickup, leg 2, drop-off) were one continuous duty period.
    """

    def __init__(self, current_cycle_used: float):
        self.cycle_used = current_cycle_used
        self.time = 0.0
        self.segments: list[Segment] = []
        self.day = 1
        self.need_rest = False
        self.miles_since_fuel = 0.0
        self.day_driving = 0.0
        self.day_on_duty = 0.0
        self.break_taken = False

    def take_rest(self, hours: float, label: str, reset_cycle: bool = False):
        self.segments.append(Segment(self.day, "off_duty", self.time, self.time + hours, label))
        self.time += hours
        self.day += 1
        self.day_driving = 0.0
        self.day_on_duty = 0.0
        self.break_taken = False
        self.need_rest = False
        if reset_cycle:
            self.cycle_used = 0


def _drive_leg(state: _HosState, driving_hours: float, distance_miles: float, extra_stops_hours: float):
    """Schedule one driving leg, mutating `state` in place.

    `extra_stops_hours` is the on-duty time known to follow this leg before
    the next rest decision (e.g. the pickup or drop-off stop), so the 34-hr
    restart / cycle checks account for it.
    """
    if driving_hours <= 0.01:
        return

    mph = distance_miles / driving_hours if driving_hours else 65.0
    hours_per_fuel_interval = FUEL_EVERY_MILES / mph

    driving_left = driving_hours
    distance_left = distance_miles

    while driving_left > 0.01:
        # Between driving days: check 34-hr restart first (it subsumes the 10-hr rest)
        if state.need_rest:
            on_duty_remaining = _estimate_on_duty_remaining(driving_left, distance_left, extra_stops_hours)
            if state.cycle_used + on_duty_remaining > CYCLE_LIMIT:
                # 34-hr restart satisfies the 10-hr rest requirement — skip the rest
                state.take_rest(RESTART_OFF_DUTY, "34-hr restart", reset_cycle=True)
            else:
                state.take_rest(OFF_DUTY_BETWEEN_DAYS, "10-hr rest")

        # 34-hr restart check at the start of a fresh day (need_rest is already False here)
        elif state.day_driving == 0 and state.day_on_duty == 0:
            on_duty_remaining = _estimate_on_duty_remaining(driving_left, distance_left, extra_stops_hours)
            if state.cycle_used + on_duty_remaining > CYCLE_LIMIT:
                state.take_rest(RESTART_OFF_DUTY, "34-hr restart", reset_cycle=True)

        # Drive loop for the current day, continuing from wherever this day's
        # counters (day_driving/day_on_duty/break_taken) already stand.
        while driving_left > 0.01:
            if state.day_driving >= DAY_DRIVING_LIMIT:
                break
            if state.day_on_duty + BREAK_LENGTH >= DAY_ON_DUTY_LIMIT:
                break

            # Fuel stop: check BEFORE driving segment so we can insert it. Uses the
            # same time-based tolerance as `drive_for` below (0.01h) rather than a
            # separate mile-based one — a mismatched tolerance here previously let
            # `until_fuel` round down to a 0-hour `drive_for` just *before*
            # `miles_since_fuel` crossed the old mile threshold, which stalled the
            # trip forever (no fuel stop fired, no driving happened, so every day
            # looked "used up" and it just kept resting without ever progressing).
            until_fuel = hours_per_fuel_interval - state.miles_since_fuel / mph
            if until_fuel <= 0.01:
                state.segments.append(Segment(state.day, "on_duty_not_driving", state.time, state.time + FUEL_STOP_LENGTH, "Fuel stop"))
                state.time += FUEL_STOP_LENGTH
                state.day_on_duty += FUEL_STOP_LENGTH
                state.cycle_used += FUEL_STOP_LENGTH
                state.miles_since_fuel = 0.0
                continue

            # How long until the next mandatory event?
            until_11h = DAY_DRIVING_LIMIT - state.day_driving
            until_break = BREAK_AFTER_DRIVING - state.day_driving if not state.break_taken else until_11h
            until_on_duty_limit = DAY_ON_DUTY_LIMIT - state.day_on_duty - BREAK_LENGTH

            drive_for = min(driving_left, until_11h, until_break, until_fuel, until_on_duty_limit)
            drive_for = max(0, round(drive_for, 2))
            if drive_for <= 0.01:
                break

            state.segments.append(Segment(state.day, "driving", state.time, state.time + drive_for, "Driving"))
            state.time += drive_for
            driving_left -= drive_for
            distance_left -= drive_for * mph
            state.miles_since_fuel += drive_for * mph
            state.day_driving += drive_for
            state.day_on_duty += drive_for
            state.cycle_used += drive_for

            if driving_left <= 0.01:
                break

            # 30-min break after 8h cumulative driving
            if not state.break_taken and state.day_driving >= BREAK_AFTER_DRIVING - 0.01:
                state.segments.append(Segment(state.day, "on_duty_not_driving", state.time, state.time + BREAK_LENGTH, "30-min break"))
                state.time += BREAK_LENGTH
                state.day_on_duty += BREAK_LENGTH
                state.cycle_used += BREAK_LENGTH
                state.break_taken = True

        if driving_left > 0.01:
            # Day ended (11h driving or 14h on-duty) with more driving left on this leg — rest and continue
            state.need_rest = True
            continue


def _add_on_duty_stop(state: _HosState, hours: float, label: str):
    """Insert an on-duty-not-driving stop (Pickup/Drop-off).

    On-duty time still counts against the 14-hour on-duty window, so if
    today's window has no room left for it, a 10-hr rest is required first.
    """
    if state.day_on_duty + hours > DAY_ON_DUTY_LIMIT:
        # No room left in the current on-duty window — rest before adding the stop.
        state.take_rest(OFF_DUTY_BETWEEN_DAYS, "10-hr rest")

    state.segments.append(Segment(state.day, "on_duty_not_driving", state.time, state.time + hours, label))
    state.time += hours
    state.cycle_used += hours
    state.day_on_duty += hours


def calculate_hos(
    leg1_driving_hours: float, leg1_distance_miles: float,
    leg2_driving_hours: float, leg2_distance_miles: float,
    current_cycle_used: float,
) -> list[Segment]:
    """Calculate HOS duty-status segments for a trip with a pickup stop.

    The trip is: drive leg 1 (current -> pickup), Pickup (1hr on-duty),
    drive leg 2 (pickup -> dropoff), Drop-off (1hr on-duty). Both legs share
    the same running day/cycle/fuel counters, exactly as if it were one
    continuous drive with a stop in the middle.

    Returns an ordered list of Segments covering the full trip.
    """
    if leg1_driving_hours <= 0 and leg2_driving_hours <= 0:
        return []

    state = _HosState(current_cycle_used)

    _drive_leg(state, leg1_driving_hours, leg1_distance_miles, extra_stops_hours=PICKUP_HOURS + leg2_driving_hours + DROPOFF_HOURS)
    _add_on_duty_stop(state, PICKUP_HOURS, "Pickup")
    _drive_leg(state, leg2_driving_hours, leg2_distance_miles, extra_stops_hours=DROPOFF_HOURS)
    _add_on_duty_stop(state, DROPOFF_HOURS, "Drop-off")

    return state.segments


def print_schedule(segments: list[Segment]):
    if not segments:
        print("  (no segments)")
        return

    current_day = 0
    for s in segments:
        if s.day_number != current_day:
            current_day = s.day_number
            print(f"\n--- Day {current_day} ---")
        sh, sm = divmod(int(s.start * 60), 60)
        eh, em = divmod(int(s.end * 60), 60)
        print(f"  {s.status:<24} {sh:02d}:{sm:02d}-{eh:02d}:{em:02d}  ({s.duration}h)  {s.label}")


if __name__ == "__main__":
    print("=" * 60)
    print("TEST 1: Short trip, single day (2h + 3h drive, 120mi + 180mi)")
    print("=" * 60)
    segs = calculate_hos(2.0, 120.0, 3.0, 180.0, 10.0)
    print_schedule(segs)
    assert len([s for s in segs if s.status == "driving"]) == 2
    assert sum(s.duration for s in segs if s.status == "driving") == 5.0
    assert not any("fuel" in s.label.lower() for s in segs)
    assert len([s for s in segs if s.label == "Pickup"]) == 1
    assert len([s for s in segs if s.label == "Drop-off"]) == 1
    # Order: driving, Pickup, driving, ..., Drop-off
    driving_idx = [i for i, s in enumerate(segs) if s.status == "driving"]
    pickup_idx = next(i for i, s in enumerate(segs) if s.label == "Pickup")
    dropoff_idx = next(i for i, s in enumerate(segs) if s.label == "Drop-off")
    assert driving_idx[0] < pickup_idx < driving_idx[-1] < dropoff_idx
    print("\n  ✓ PASS")

    print("\n\n" + "=" * 60)
    print("TEST 2: Multi-day trip, long leg 1 requiring a break/second day (9h + 6h drive)")
    print("=" * 60)
    segs = calculate_hos(9.0, 540.0, 6.0, 360.0, 20.0)
    print_schedule(segs)
    assert sum(s.duration for s in segs if s.status == "driving") == 15.0
    assert any(s.label == "10-hr rest" for s in segs)
    assert not any("fuel" in s.label.lower() for s in segs)
    assert len([s for s in segs if s.label == "Pickup"]) == 1
    assert len([s for s in segs if s.label == "Drop-off"]) == 1
    print("\n  ✓ PASS")

    print("\n\n" + "=" * 60)
    print("TEST 3: High cycle — 34-hr restart (4h + 5h drive, 62h used)")
    print("=" * 60)
    segs = calculate_hos(4.0, 240.0, 5.0, 300.0, 62.0)
    print_schedule(segs)
    assert any(s.label == "34-hr restart" for s in segs)
    assert sum(s.duration for s in segs if s.status == "driving") == 9.0
    assert len([s for s in segs if s.label == "Pickup"]) == 1
    assert len([s for s in segs if s.label == "Drop-off"]) == 1
    print("\n  ✓ PASS")

    print("\n\n" + "=" * 60)
    print("TEST 4: Long trip with fuel stop across leg boundary (8h + 12h drive, 1200mi total)")
    print("=" * 60)
    segs = calculate_hos(8.0, 480.0, 12.0, 720.0, 15.0)
    print_schedule(segs)
    fuel_stops = [s for s in segs if s.label == "Fuel stop"]
    assert len(fuel_stops) == 1, f"Expected 1 fuel stop, got {len(fuel_stops)}"
    assert sum(s.duration for s in segs if s.status == "driving") == 20.0
    assert len([s for s in segs if s.label == "Pickup"]) == 1
    assert len([s for s in segs if s.label == "Drop-off"]) == 1
    print("\n  ✓ PASS")

    print("\n\n" + "=" * 60)
    print("TEST 5: No rest stacking (10h + 10h drive, 1200mi total, 58h used)")
    print("=" * 60)
    segs = calculate_hos(10.0, 600.0, 10.0, 600.0, 58.0)
    print_schedule(segs)
    # Verify: no two off-duty segments share the same day_number (no stacking)
    off_duty_days = [s.day_number for s in segs if s.status == "off_duty"]
    assert len(off_duty_days) == len(set(off_duty_days)), \
        f"Stacked off-duty on same day: {off_duty_days}"
    assert sum(s.duration for s in segs if s.status == "driving") == 20.0
    assert len([s for s in segs if s.label == "Pickup"]) == 1
    assert len([s for s in segs if s.label == "Drop-off"]) == 1
    print("\n  ✓ PASS")

    print("\n\n" + "=" * 60)
    print("TEST 6 (bug-report repro): leg1 3.5h current->pickup, leg2 1.5h pickup->dropoff")
    print("=" * 60)
    segs = calculate_hos(3.5, 210.0, 1.5, 90.0, 10.0)
    print_schedule(segs)
    print("\nRaw segments:")
    for s in segs:
        print(f"  {s!r}")
    order = [s.label if s.status != "driving" else "Driving" for s in segs]
    assert order == ["Driving", "Pickup", "Driving", "Drop-off"], order
    assert sum(s.duration for s in segs if s.status == "driving") == 5.0
    print("\n  ✓ PASS")
