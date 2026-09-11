# DutyMap Frontend

React + Vite single-page app for the DutyMap ELD trip planner.

## Setup

```bash
cd frontend
npm install
npm run dev
```

The dev server runs on `http://localhost:5173`.

## Environment variables

| Variable      | Required | Default                        | Description                    |
| ------------- | -------- | ------------------------------ | ------------------------------ |
| `VITE_API_BASE` | No     | `http://localhost:8000/api`    | Backend API base URL           |

Create a `.env` file in `frontend/` to override:

```
VITE_API_BASE=http://localhost:8000/api
```

## Scripts

| Command           | Description                  |
| ----------------- | ---------------------------- |
| `npm run dev`     | Start Vite dev server        |
| `npm run build`   | Production build to `dist/`  |
| `npm run lint`    | Run oxlint                   |
| `npm run preview` | Preview production build     |

## Component overview

| Component         | File               | Purpose                                                         |
| ----------------- | ------------------ | --------------------------------------------------------------- |
| `App`             | `App.jsx`          | Main layout: form row on top, map + log sheets below            |
| `TripMap`         | `TripMap.jsx`      | Leaflet map showing the route, markers, and distance stats      |
| `LogSheets`       | `LogSheets.jsx`    | Tabbed viewer for the SVG daily log sheets from the API         |
| `LocationField`   | `LocationField.jsx`| Location input with toggle between place name and lat/lon entry |
| `AutocompleteInput` | `AutocompleteInput.jsx` | Address search with Nominatim autocomplete dropdown     |

## Layout

The app uses a viewport-height layout (`100vh`):

- **Top row** — compact form with three location inputs on the left (60%) and cycle hours, start datetime, and submit button on the right (40%)
- **Bottom row** — map panel (5/12 width) and log sheet panel (7/12 width) sharing the remaining height
- On viewports narrower than 768px, everything stacks vertically

## API calls

All backend communication goes through `src/api.js`:

- `createTrip(payload)` — `POST /api/trips/`
- `searchLocations(query)` — `GET /api/geocode/?q=<query>`

Both return parsed JSON or throw `ApiError` with a human-readable message.
