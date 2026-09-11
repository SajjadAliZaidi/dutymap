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


def _estimate_on_duty_remaining(driving_hours: float, distance_miles: float) -> float:
    """Rough estimate of on-duty hours still needed (for cycle restart check)."""
    breaks = (driving_hours / BREAK_AFTER_DRIVING) * BREAK_LENGTH
    fuel_stops = (distance_miles / FUEL_EVERY_MILES) * FUEL_STOP_LENGTH
    return driving_hours + DROPOFF_HOURS + breaks + fuel_stops


def calculate_hos(total_driving_hours: float, total_distance_miles: float,
                  current_cycle_used: float) -> list[Segment]:
    """Calculate HOS duty-status segments for a trip.

    Returns an ordered list of Segments covering the full trip.
    """
    if total_driving_hours <= 0:
        return []

    mph = total_distance_miles / total_driving_hours if total_driving_hours else 65.0
    hours_per_fuel_interval = FUEL_EVERY_MILES / mph

    driving_left = total_driving_hours
    distance_left = total_distance_miles
    cycle_used = current_cycle_used
    time = 0.0
    segments: list[Segment] = []
    day = 1
    need_rest = False
    miles_since_fuel = 0.0

    # Pickup happens once, before any driving begins
    segments.append(Segment(day, "on_duty_not_driving", time, time + PICKUP_HOURS, "Pickup"))
    time += PICKUP_HOURS
    cycle_used += PICKUP_HOURS

    while driving_left > 0.01:
        # Between driving days: check 34-hr restart first (it subsumes the 10-hr rest)
        if need_rest:
            on_duty_remaining = _estimate_on_duty_remaining(driving_left, distance_left)
            if cycle_used + on_duty_remaining > CYCLE_LIMIT:
                # 34-hr restart satisfies the 10-hr rest requirement — skip the rest
                segments.append(Segment(day, "off_duty", time, time + RESTART_OFF_DUTY, "34-hr restart"))
                time += RESTART_OFF_DUTY
                cycle_used = 0
                day += 1
            else:
                day += 1
                segments.append(Segment(day - 1, "off_duty", time, time + OFF_DUTY_BETWEEN_DAYS, "10-hr rest"))
                time += OFF_DUTY_BETWEEN_DAYS

        # 34-hr restart on first day (need_rest is False here)
        if not need_rest:
            on_duty_remaining = _estimate_on_duty_remaining(driving_left, distance_left)
            if cycle_used + on_duty_remaining > CYCLE_LIMIT:
                segments.append(Segment(day, "off_duty", time, time + RESTART_OFF_DUTY, "34-hr restart"))
                time += RESTART_OFF_DUTY
                cycle_used = 0
                day += 1

        on_duty = 0.0
        day_driving = 0.0
        break_taken = False

        # Drive loop for this day
        while driving_left > 0.01:
            if day_driving >= DAY_DRIVING_LIMIT:
                break
            if on_duty + BREAK_LENGTH >= DAY_ON_DUTY_LIMIT:
                break

            # Fuel stop: check BEFORE driving segment so we can insert it
            if miles_since_fuel >= FUEL_EVERY_MILES - 0.1:
                segments.append(Segment(day, "on_duty_not_driving", time, time + FUEL_STOP_LENGTH, "Fuel stop"))
                time += FUEL_STOP_LENGTH
                on_duty += FUEL_STOP_LENGTH
                miles_since_fuel = 0.0
                continue

            # How long until the next mandatory event?
            until_11h = DAY_DRIVING_LIMIT - day_driving
            until_break = BREAK_AFTER_DRIVING - day_driving if not break_taken else until_11h
            until_fuel = hours_per_fuel_interval - miles_since_fuel / mph
            until_on_duty_limit = DAY_ON_DUTY_LIMIT - on_duty - BREAK_LENGTH

            drive_for = min(driving_left, until_11h, until_break, until_fuel, until_on_duty_limit)
            drive_for = max(0, round(drive_for, 2))
            if drive_for <= 0.01:
                break

            segments.append(Segment(day, "driving", time, time + drive_for, "Driving"))
            time += drive_for
            driving_left -= drive_for
            distance_left -= drive_for * mph
            miles_since_fuel += drive_for * mph
            day_driving += drive_for
            on_duty += drive_for

            if driving_left <= 0.01:
                break

            # 30-min break after 8h cumulative driving
            if not break_taken and day_driving >= BREAK_AFTER_DRIVING - 0.01:
                segments.append(Segment(day, "on_duty_not_driving", time, time + BREAK_LENGTH, "30-min break"))
                time += BREAK_LENGTH
                on_duty += BREAK_LENGTH
                break_taken = True

        if driving_left > 0.01:
            # Day ended (11h driving or 14h on-duty), accumulate and rest
            cycle_used += on_duty
            need_rest = True
            continue

        # Trip complete, add drop-off
        segments.append(Segment(day, "on_duty_not_driving", time, time + DROPOFF_HOURS, "Drop-off"))
        time += DROPOFF_HOURS
        cycle_used += on_duty + DROPOFF_HOURS

    return segments


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
    print("TEST 1: Short trip, single day (5h drive, 300mi)")
    print("=" * 60)
    segs = calculate_hos(5.0, 300.0, 10.0)
    print_schedule(segs)
    assert len([s for s in segs if s.status == "driving"]) == 1
    assert sum(s.duration for s in segs if s.status == "driving") == 5.0
    assert not any("fuel" in s.label.lower() for s in segs)
    assert len([s for s in segs if s.label == "Pickup"]) == 1
    assert len([s for s in segs if s.label == "Drop-off"]) == 1
    print("\n  ✓ PASS")

    print("\n\n" + "=" * 60)
    print("TEST 2: Multi-day trip (15h drive, 900mi)")
    print("=" * 60)
    segs = calculate_hos(15.0, 900.0, 20.0)
    print_schedule(segs)
    assert sum(s.duration for s in segs if s.status == "driving") == 15.0
    assert any(s.label == "10-hr rest" for s in segs)
    assert not any("fuel" in s.label.lower() for s in segs)
    assert len([s for s in segs if s.label == "Pickup"]) == 1
    assert len([s for s in segs if s.label == "Drop-off"]) == 1
    print("\n  ✓ PASS")

    print("\n\n" + "=" * 60)
    print("TEST 3: High cycle — 34-hr restart (9h drive, 540mi, 62h used)")
    print("=" * 60)
    segs = calculate_hos(9.0, 540.0, 62.0)
    print_schedule(segs)
    assert any(s.label == "34-hr restart" for s in segs)
    assert sum(s.duration for s in segs if s.status == "driving") == 9.0
    assert len([s for s in segs if s.label == "Pickup"]) == 1
    assert len([s for s in segs if s.label == "Drop-off"]) == 1
    print("\n  ✓ PASS")

    print("\n\n" + "=" * 60)
    print("TEST 4: Long trip with fuel stop (20h drive, 1200mi)")
    print("=" * 60)
    segs = calculate_hos(20.0, 1200.0, 15.0)
    print_schedule(segs)
    fuel_stops = [s for s in segs if s.label == "Fuel stop"]
    assert len(fuel_stops) == 1, f"Expected 1 fuel stop, got {len(fuel_stops)}"
    assert sum(s.duration for s in segs if s.status == "driving") == 20.0
    assert len([s for s in segs if s.label == "Pickup"]) == 1
    assert len([s for s in segs if s.label == "Drop-off"]) == 1
    print("\n  ✓ PASS")

    print("\n\n" + "=" * 60)
    print("TEST 5: No rest stacking (20h drive, 1200mi, 58h used)")
    print("=" * 60)
    segs = calculate_hos(20.0, 1200.0, 58.0)
    print_schedule(segs)
    # Verify: no two off-duty segments share the same day_number (no stacking)
    off_duty_days = [s.day_number for s in segs if s.status == "off_duty"]
    assert len(off_duty_days) == len(set(off_duty_days)), \
        f"Stacked off-duty on same day: {off_duty_days}"
    assert sum(s.duration for s in segs if s.status == "driving") == 20.0
    assert len([s for s in segs if s.label == "Pickup"]) == 1
    assert len([s for s in segs if s.label == "Drop-off"]) == 1
    print("\n  ✓ PASS")
