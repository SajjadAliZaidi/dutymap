# DutyMap

ELD trip planner for property-carrying truck drivers. Enter a current location, pickup, dropoff, cycle hours used, and trip start time — DutyMap geocodes the stops, computes the driving route, calculates an FMCSA-compliant Hours of Service schedule, and renders driver daily log sheets as SVG.

**Live demo:** https://dutymap.vercel.app <!-- TODO: update with real URL -->

<!-- TODO: insert screenshot or GIF here -->

## Tech stack

| Layer    | Tech                                                           |
| -------- | -------------------------------------------------------------- |
| Backend  | Python 3.11, Django 4.x, Django REST Framework, SQLite         |
| Frontend | React 19, Vite, Leaflet / react-leaflet                        |
| Routing  | OSRM (free, no API key)                                        |
| Geocoding| Nominatim / OpenStreetMap (free, no API key)                   |

## Local development

No API keys are required. Both Nominatim (geocoding) and OSRM (routing) are free, open services.

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver      # runs on http://localhost:8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev                     # runs on http://localhost:5173
```

The frontend talks to the backend at `http://localhost:8000/api` by default. To override, set `VITE_API_BASE` in a `.env` file:

```
VITE_API_BASE=http://localhost:8000/api
```

## Environment variables

Backend (`backend/eldproject/settings.py` reads these from the environment):

```
SECRET_KEY=your-secret-key-here
DEBUG=true
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

| Variable               | Required | Default                                         |
| ---------------------- | -------- | ----------------------------------------------- |
| `SECRET_KEY`           | Yes (prod) | Auto-generated if unset (dev only)            |
| `DEBUG`                | No       | `False`                                         |
| `ALLOWED_HOSTS`        | No       | `localhost,127.0.0.1`                          |
| `CORS_ALLOWED_ORIGINS` | No       | Includes `localhost:3000`, `localhost:5173`     |

## HOS rules implemented

70-hour / 8-day cycle for property-carrying drivers:

- 11-hour driving limit per day
- 14-hour on-duty window per day
- 30-minute break required after 8 cumulative hours of driving
- 10-hour off-duty rest period between driving days
- 70-hour / 8-day rolling cycle limit with 34-hour restart option
- 1 hour on-duty for pickup, 1 hour on-duty for dropoff
- Mandatory fuel stop every 1,000 miles (30 minutes, on-duty not driving)
- No adverse driving conditions

## Key assumptions

These constraints were given by the assignment:

- Property-carrying driver only (no passenger-carrying rules)
- 70-hour / 8-day cycle (not 60-hour / 7-day)
- No adverse driving conditions
- Fuel stop every 1,000 miles
- 1 hour each for pickup and dropoff

## Known limitations / out of scope

- No sleeper berth split-rule support
- No 60-hour / 7-day cycle option
- No adverse driving condition adjustments
- No team driving support
- No authentication or per-user trip history
- Log sheets are SVG only (no PDF export yet)

## Project structure

```
dutymap/
├── backend/
│   ├── trips/
│   │   ├── hos.py          # HOS calculation (segments, rules)
│   │   ├── log_sheets.py   # Calendar-day slicing
│   │   ├── svg_log.py      # SVG daily log rendering
│   │   ├── services.py     # Trip processing pipeline
│   │   ├── models.py       # Trip model
│   │   ├── serializers.py  # DRF serializer
│   │   └── views.py        # API views
│   ├── eldproject/         # Django project settings
│   ├── manage.py
│   └── requirements.txt
└── frontend/
    ├── src/
    │   ├── App.jsx         # Main layout and form
    │   ├── TripMap.jsx     # Leaflet map with route
    │   ├── LogSheets.jsx   # Tabbed SVG log viewer
    │   ├── LocationField.jsx  # Place/lat-long input toggle
    │   └── api.js          # API client
    └── package.json
```

## Credit

Built by **[Sajjad Zaidi](https://sajjadalizaidi.github.io/)** · [LinkedIn](https://www.linkedin.com/in/syedmuhammadsajjad/)
