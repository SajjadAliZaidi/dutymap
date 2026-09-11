# DutyMap Deployment Guide

This app is deployed as two separate services:

- **Backend (Django):** [Render](https://render.com/)
- **Frontend (React + Vite):** [Vercel](https://vercel.com/)

---

## 1. Backend — Render

### Settings

| Setting | Value |
|---|---|
| Root Directory | `backend` |
| Build Command | `./build.sh` |
| Start Command | `gunicorn eldproject.wsgi:application --bind 0.0.0.0:$PORT` |

### Environment Variables (Render Dashboard)

| Variable | Required? | Example / Notes |
|---|---|---|
| `SECRET_KEY` | Yes | Generate a strong random string, e.g. `python -c "import secrets; print(secrets.token_urlsafe(50))"` |
| `DEBUG` | Optional | Leave unset or set `False` in production. |
| `DATABASE_URL` | No | Leave unset to use the SQLite fallback (`backend/db.sqlite3`). |
| `ALLOWED_HOSTS` | Optional | Comma-separated, e.g. `your-service.onrender.com,localhost` |
| `RENDER_HOST` | Optional | `your-service.onrender.com` (used as a fallback in `ALLOWED_HOSTS`) |
| `VERCEL_ORIGIN` | Optional | `https://your-project.vercel.app` |

**Note on SQLite in production:** This project uses SQLite. Render's default filesystem is ephemeral, so `db.sqlite3` will be recreated on every deploy and is not shared across instances. That's fine for a demo/take-home, but if you ever want persistence or multiple instances, switch to PostgreSQL.

**After your first deploy:**

1. Copy your actual Render domain (e.g. `https://dutymap-abc.onrender.com`).
2. Set `RENDER_HOST=dutymap-abc.onrender.com` and/or update `ALLOWED_HOSTS` in the Render dashboard.
3. Copy your actual Vercel URL and set `VERCEL_ORIGIN=https://your-project.vercel.app` in Render.
4. Redeploy the backend so CORS/CSRF origins are correct.

---

## 2. Frontend — Vercel

### Settings

| Setting | Value |
|---|---|
| Root Directory | `frontend` |
| Framework Preset | Vite |
| Build Command | `npm run build` (default) |
| Output Directory | `dist` (default for Vite) |

### Environment Variables (Vercel Dashboard)

| Variable | Required? | Example / Notes |
|---|---|---|
| `VITE_API_BASE` | Yes | `https://your-service.onrender.com/api` — points at the deployed Django backend. |

No `vercel.json` is needed; the app does not use React Router for client-side routing.

---

## 3. Local Development

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver

# Frontend (new terminal)
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

The local backend runs at `http://localhost:8000` and the Vite dev server at `http://localhost:5173`.

---

## 4. Important Reminders

- Do **not** commit production `SECRET_KEY` or database credentials.
- Update `VERCEL_ORIGIN` (and `ALLOWED_HOSTS`/`RENDER_HOST`) in Render with the real Vercel URL after first deploy.
- The frontend is built with Vite; environment variables consumed by the frontend must be prefixed with `VITE_`.
