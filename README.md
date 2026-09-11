# DutyMap

**ELD Trip Planner** — enter a current location, pickup, dropoff, and the hours already used in your cycle; DutyMap geocodes the places, computes the driving route, and renders it on an interactive map with distance and driving-time stats.

> Status: work in progress. Routing and mapping work end to end; ELD log-sheet generation is still a placeholder.

## Stack

| Layer    | Tech                                                                    |
| -------- | ----------------------------------------------------------------------- |
| Backend  | Django 4.2–5.0, Django REST Framework, SQLite                            |
| Frontend | React 19, Vite, Leaflet / react-leaflet                                  |
| Services | OpenStreetMap Nominatim (geocoding), OSRM (driving routes) — server-side |

## Project layout

```
backend/    Django project (eldproject) with the `trips` app
frontend/   React + Vite single-page app
```

## Running locally

**Backend** (http://localhost:8000)

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

**Frontend** (http://localhost:5173)

```bash
cd frontend
npm install
npm run dev
```

## API

| Method | Path             | Description                                   |
| ------ | ---------------- | --------------------------------------------- |
| POST   | `/api/trips/`    | Create a trip, geocode it, and calculate route |

`POST /api/trips/` accepts:

```json
{
  "current_location": "Dallas, TX",
  "pickup_location": "Houston, TX",
  "dropoff_location": "Chicago, IL",
  "current_cycle_used": 8.5
}
```

The response includes the trip inputs, a `route` object (GeoJSON geometry, distance in miles, duration in hours, per-stop coordinates), `logs`, and a `meta` block.

## Roadmap

- [ ] ELD log-sheet generation and hours-of-service rules
- [ ] Persist trip history (`GET /api/trips/`)
- [ ] Authentication and per-user trips
- [ ] Move secrets and endpoints into environment variables
- [ ] Tests

## Credit

Built by **[Sajjad Zaidi](https://sajjadalizaidi.github.io/)**.
