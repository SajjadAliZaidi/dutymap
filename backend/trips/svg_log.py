"""
SVG rendering of FMCSA-style daily log sheets.

Generates a clean, readable 24-hour grid with duty-status rows and a
stepped line showing the driver's status over time.
"""

from datetime import date, timedelta
from .hos import Segment

# FMCSA status order (top to bottom)
STATUSES = [
    ("off_duty", "Off Duty"),
    ("sleeper_berth", "Sleeper Berth"),
    ("driving", "Driving"),
    ("on_duty_not_driving", "On Duty (Not Driving)"),
]
STATUS_INDEX = {code: i for i, (code, _) in enumerate(STATUSES)}

# Layout constants
WIDTH = 800
HEIGHT = 300
MARGIN_LEFT = 130
MARGIN_RIGHT = 20
MARGIN_TOP = 45
MARGIN_BOTTOM = 30
GRID_LEFT = MARGIN_LEFT
GRID_RIGHT = WIDTH - MARGIN_RIGHT
GRID_TOP = MARGIN_TOP
GRID_BOTTOM = HEIGHT - MARGIN_BOTTOM
GRID_W = GRID_RIGHT - GRID_LEFT
GRID_H = GRID_BOTTOM - GRID_TOP
ROW_H = GRID_H / 4
HOUR_W = GRID_W / 24


def _row_y(status: str) -> float:
    """Vertical center of the row for a given status code."""
    idx = STATUS_INDEX.get(status, 0)
    return GRID_TOP + ROW_H * idx + ROW_H / 2


def _hour_x(elapsed_hours: float) -> float:
    """Horizontal pixel position for an elapsed-hour value (0–24)."""
    return GRID_LEFT + (elapsed_hours / 24.0) * GRID_W


def _escape(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def render_log_sheet(day_date: date, segments: list[Segment]) -> str:
    """Return a complete SVG string for one day's FMCSA-style log.

    Parameters
    ----------
    day_date : date
        The calendar day this log covers.
    segments : list[Segment]
        Segments for this day (already split by ``split_by_calendar_day``).
        Each segment's ``start``/``end`` are elapsed hours from trip start.
    """
    parts: list[str] = []
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {HEIGHT}" '
        f'width="{WIDTH}" height="{HEIGHT}" style="font-family:Arial,Helvetica,sans-serif">'
    )

    # --- Background ---
    parts.append(f'<rect width="{WIDTH}" height="{HEIGHT}" fill="#fff"/>')

    # --- Header ---
    parts.append(
        f'<text x="{WIDTH / 2}" y="22" text-anchor="middle" '
        f'font-size="15" font-weight="bold" fill="#222">'
        f'{day_date.strftime("%A, %B %-d, %Y")}</text>'
    )
    parts.append(
        f'<text x="{WIDTH / 2}" y="38" text-anchor="middle" '
        f'font-size="11" fill="#666">'
        f'Driver\'s Daily Log — 24-Hour Period</text>'
    )

    # --- Grid lines ---
    # Horizontal row dividers
    for i in range(5):
        y = GRID_TOP + ROW_H * i
        parts.append(
            f'<line x1="{GRID_LEFT}" y1="{y:.1f}" x2="{GRID_RIGHT}" y2="{y:.1f}" '
            f'stroke="#bbb" stroke-width="0.5"/>'
        )

    # Vertical hour lines + labels
    for h in range(25):
        x = GRID_LEFT + HOUR_W * h
        stroke = "#999" if h % 6 == 0 else "#ddd"
        width = "1" if h % 6 == 0 else "0.5"
        parts.append(
            f'<line x1="{x:.1f}" y1="{GRID_TOP}" x2="{x:.1f}" y2="{GRID_BOTTOM}" '
            f'stroke="{stroke}" stroke-width="{width}"/>'
        )
        if h < 24:
            lx = x + HOUR_W / 2
            parts.append(
                f'<text x="{lx:.1f}" y="{GRID_BOTTOM + 14}" text-anchor="middle" '
                f'font-size="9" fill="#555">{h}</text>'
            )

    # --- Row labels (left side) ---
    for code, label in STATUSES:
        y = _row_y(code)
        parts.append(
            f'<text x="{GRID_LEFT - 8}" y="{y + 4:.1f}" text-anchor="end" '
            f'font-size="10" fill="#333">{_escape(label)}</text>'
        )

    # --- Duty-status line ---
    if segments:
        # Determine starting point. If the first segment doesn't start at
        # midnight, draw an off-duty lead-in from the left edge.
        first_seg = segments[0]
        first_y = _row_y(first_seg.status)
        lead_in = first_seg.start > 0
        start_y = _row_y("off_duty") if lead_in else first_y

        path_d = [f"M {GRID_LEFT:.1f} {start_y:.1f}"]
        prev_x = GRID_LEFT
        prev_y = start_y

        for seg in segments:
            sy = _row_y(seg.status)
            sx = _hour_x(seg.start)
            ex = _hour_x(seg.end)

            # Horizontal to segment start at current row
            if prev_x != sx:
                path_d.append(f"L {sx:.1f} {prev_y:.1f}")
            # Vertical step into this segment's status row
            if prev_y != sy:
                path_d.append(f"L {sx:.1f} {sy:.1f}")
            # Horizontal through the segment
            path_d.append(f"L {ex:.1f} {sy:.1f}")

            prev_x = ex
            prev_y = sy

        # Extend to right edge at off-duty if the last segment ends before midnight
        if prev_x < GRID_RIGHT:
            off_y = _row_y("off_duty")
            if prev_y != off_y:
                path_d.append(f"L {prev_x:.1f} {off_y:.1f}")
            path_d.append(f"L {GRID_RIGHT:.1f} {off_y:.1f}")

        parts.append(
            f'<path d="{" ".join(path_d)}" fill="none" '
            f'stroke="#d32f2f" stroke-width="2.5" stroke-linejoin="miter"/>'
        )

        # --- Segment labels ---
        for seg in segments:
            sx = _hour_x(seg.start)
            ex = _hour_x(seg.end)
            mid_x = (sx + ex) / 2
            sy = _row_y(seg.status)
            seg_w = ex - sx

            # Choose label placement: above if possible, inside if wide enough
            if seg_w > 50:
                # Label inside the segment
                ty = sy + 4
                anchor = "middle"
                font_size = "9"
            else:
                # Label above the segment line
                ty = sy - 6
                anchor = "middle"
                font_size = "8"

            label = seg.label
            # Abbreviate long labels in tight spaces
            if seg_w < 35:
                abbrevs = {
                    "Off Duty": "Off",
                    "Sleeper Berth": "SB",
                    "Driving": "Drv",
                    "On Duty (Not Driving)": "OnD",
                    "30-min break": "Brk",
                    "Fuel stop": "Fuel",
                    "34-hr restart": "Rst",
                    "10-hr rest": "Rest",
                }
                label = abbrevs.get(label, label[:4])

            parts.append(
                f'<text x="{mid_x:.1f}" y="{ty:.1f}" text-anchor="{anchor}" '
                f'font-size="{font_size}" fill="#222" font-weight="bold">'
                f'{_escape(label)}</text>'
            )
    else:
        # No segments — flat off-duty line for full 24 hours
        y = _row_y("off_duty")
        parts.append(
            f'<line x1="{GRID_LEFT}" y1="{y:.1f}" x2="{GRID_RIGHT}" y2="{y:.1f}" '
            f'stroke="#d32f2f" stroke-width="2.5"/>'
        )
        parts.append(
            f'<text x="{WIDTH / 2}" y="{y + 4:.1f}" text-anchor="middle" '
            f'font-size="10" fill="#999">No duty activity</text>'
        )

    parts.append("</svg>")
    return "\n".join(parts)


if __name__ == "__main__":
    from datetime import datetime

    print("=" * 60)
    print("TEST: Render a sample day with mixed segments")
    print("=" * 60)

    # A realistic day: Driving, fuel stop, more driving, off duty
    day = date(2026, 9, 11)
    segs = [
        Segment(1, "on_duty_not_driving", 0.0, 1.0, "Pickup"),
        Segment(1, "driving", 1.0, 5.0, "Driving"),
        Segment(1, "on_duty_not_driving", 5.0, 5.5, "Fuel stop"),
        Segment(1, "driving", 5.5, 9.5, "Driving"),
        Segment(1, "on_duty_not_driving", 9.5, 10.0, "30-min break"),
        Segment(1, "off_duty", 10.0, 24.0, "Off Duty"),
    ]
    svg = render_log_sheet(day, segs)
    print(f"\nSVG length: {len(svg)} chars")
    print(f"Contains <svg: {svg.startswith('<svg')}")
    print(f"Contains date: {day.strftime('%B')} in output: {day.strftime('%B') in svg}")
    print(f"Segments rendered: Driving={sum(1 for s in segs if s.status == 'driving')}")

    # Write to file for visual inspection
    out_path = "test_log.svg"
    with open(out_path, "w") as f:
        f.write(svg)
    print(f"\nWrote sample SVG to {out_path}")

    # Verify basic structure
    assert svg.startswith('<svg xmlns="http://www.w3.org/2000/svg"')
    assert "Off Duty" in svg
    assert "Sleeper Berth" in svg
    assert "Driving" in svg
    assert "On Duty (Not Driving)" in svg
    assert day.strftime("%B") in svg

    print("\n  ✓ PASS")

    print("\n\n" + "=" * 60)
    print("TEST: Empty segments (all off duty)")
    print("=" * 60)
    svg2 = render_log_sheet(date(2026, 9, 12), [])
    assert "No duty activity" in svg2
    assert svg2.count("Off Duty") >= 1
    print("  ✓ PASS")
