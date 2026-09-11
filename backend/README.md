# DutyMap Backend

Django REST Framework API for the DutyMap ELD trip planner.

## Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

The server runs on `http://localhost:8000`.

## API endpoints

### `GET /api/geocode/?q=<query>`

Search Nominatim for address suggestions.

**Response:**

```json
{
  "suggestions": [
    {
      "display_name": "Dallas, Dallas County, Texas, United States",
      "lat": 32.7767,
      "lon": -96.7970
    }
  ]
}
```

### `POST /api/trips/`

Create a trip, geocode stops, fetch the driving route, calculate HOS segments, and generate log sheets.

**Request:**

```json
{
  "current_location": "Dallas, TX",
  "pickup_location": "Houston, TX",
  "dropoff_location": "Chicago, IL",
  "current_cycle_used": 8.5,
  "start_datetime": "2026-09-12T08:00:00"
}
```

You can also supply lat/lon directly instead of place names:

```json
{
  "current_location": "",
  "current_lat": 32.7767,
  "current_lon": -96.7970,
  "pickup_location": "",
  "pickup_lat": 29.7604,
  "pickup_lon": -95.3698,
  "dropoff_location": "",
  "dropoff_lat": 41.8781,
  "dropoff_lon": -87.6298,
  "current_cycle_used": 8.5,
  "start_datetime": "2026-09-12T08:00:00"
}
```

**Response (201):**

```json
{
  "id": 1,
  "current_location": "Dallas, TX",
  "pickup_location": "Houston, TX",
  "dropoff_location": "Chicago, IL",
  "current_cycle_used": 8.5,
  "start_datetime": "2026-09-12T08:00:00",
  "created_at": "2026-09-12T07:30:00Z",
  "route": {
    "geometry": { "coordinates": [[-96.797, 32.777], ...], "type": "LineString" },
    "distance_miles": 907.5,
    "duration_hours": 13.9,
    "coordinates": {
      "current": { "lat": 32.777, "lon": -96.797 },
      "pickup": { "lat": 29.76, "lon": -95.37 },
      "dropoff": { "lat": 41.878, "lon": -87.63 }
    },
    "error": null
  },
  "logs": [
    {
      "date": "2026-09-12",
      "svg": "<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 800 520\">...</svg>"
    },
    {
      "date": "2026-09-13",
      "svg": "<svg>...</svg>"
    }
  ],
  "meta": {
    "built_by": { "name": "Sajjad Zaidi", "portfolio": "...", "linkedin": "..." }
  }
}
```

**Error responses:**

- `400` — validation error (missing fields, invalid coordinates)
- `502` — OSRM routing failed

### `GET /api/trips/<id>/`

Retrieve a previously created trip by ID. Returns the same shape as the POST response.

**Response (404):**

```json
{ "error": "Trip not found" }
```

## HOS pipeline

When a trip is created, `services.py` runs this pipeline:

1. **Geocode** (`routing.py`) — resolve each stop to lat/lon via Nominatim (or use supplied coordinates)
2. **Route** (`routing.py`) — fetch driving route from OSRM, get distance and duration
3. **HOS segments** (`hos.py`) — `calculate_hos()` simulates the trip day-by-day, emitting segments for pickup, driving, breaks, fuel stops, rest periods, 34-hr restarts, and drop-off
4. **Calendar-day slicing** (`log_sheets.py`) — `split_by_calendar_day()` converts elapsed-hour segments to wall-clock datetimes and groups them by calendar date, splitting any segment that crosses midnight
5. **SVG rendering** (`svg_log.py`) — `render_log_sheet()` renders each day's segments as an FMCSA-style 24-hour grid with 4 duty-status rows

## Running tests

```bash
# HOS calculation tests (5 test cases)
python -m trips.hos

# Calendar-day slicing tests
python -m trips.log_sheets

# SVG rendering tests
python -m trips.svg_log
```

## Migrations

```bash
python manage.py makemigrations trips
python manage.py migrate
```

Current migration history:

| Migration       | Description                          |
| --------------- | ------------------------------------ |
| `0001_initial`  | Trip model with location fields      |
| `0002`          | Route fields (geometry, distance, etc.) |
| `0003`          | Alter location field defaults        |
| `0004`          | Add `start_datetime` field           |
| `0005`          | Add `logs` JSONField                 |
