import { useState } from 'react'
import LocationField from './LocationField'
import LogSheets from './LogSheets'
import TripMap from './TripMap'
import { createTrip } from './api'
import { BUILT_BY } from './branding'
import { LOCATIONS, buildTripPayload, emptyCoords, emptyModes, validateCoords } from './tripForm'
import './App.css'

function defaultStartDatetime() {
  const now = new Date()
  const offset = now.getTimezoneOffset()
  const local = new Date(now.getTime() - offset * 60_000)
  return local.toISOString().slice(0, 16)
}

const EMPTY_FORM = {
  current_location: '',
  pickup_location: '',
  dropoff_location: '',
  current_cycle_used: '',
  start_datetime: defaultStartDatetime(),
}

function App() {
  const [form, setForm] = useState(EMPTY_FORM)
  const [modes, setModes] = useState(emptyModes)
  const [coords, setCoords] = useState(emptyCoords)
  const [loading, setLoading] = useState(false)
  const [tripData, setTripData] = useState(null)
  const [error, setError] = useState(null)

  const handlePlaceChange = (name, value) => {
    setForm((prev) => ({ ...prev, [name]: value }))
  }

  const handleCycleChange = (value) => {
    setForm((prev) => ({ ...prev, current_cycle_used: value }))
  }

  const handleModeChange = (key, mode) => {
    setModes((prev) => ({ ...prev, [key]: mode }))
  }

  const handleCoordChange = (key, axis, value) => {
    setCoords((prev) => ({ ...prev, [key]: { ...prev[key], [axis]: value } }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()

    if (!form.start_datetime) {
      setError('Trip start date & time is required')
      return
    }

    const coordError = validateCoords(modes, coords)
    if (coordError) {
      setError(coordError)
      return
    }

    setError(null)
    setLoading(true)
    setTripData(null)
    try {
      const data = await createTrip(buildTripPayload(form, modes, coords))
      console.log('Trip response:', data)
      setTripData(data)
      if (data.route?.error) {
        setError(data.route.error)
      }
    } catch (err) {
      console.error('Error creating trip:', err)
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app">
      <header>
        <h1>DutyMap</h1>
        <p>ELD Trip Planner</p>
      </header>

      {error && (
        <div className="error-banner">
          <span>{error}</span>
          <button onClick={() => setError(null)}>&times;</button>
        </div>
      )}

      <main>
        <form onSubmit={handleSubmit} className="trip-form">
          <h2>New Trip</h2>

          {LOCATIONS.map((field) => (
            <LocationField
              key={field.key}
              field={field}
              mode={modes[field.key]}
              coords={coords[field.key]}
              value={form[field.name]}
              onModeChange={(mode) => handleModeChange(field.key, mode)}
              onPlaceChange={handlePlaceChange}
              onCoordChange={(axis, value) => handleCoordChange(field.key, axis, value)}
            />
          ))}

          <label>
            Current Cycle Used (hours)
            <input
              type="number"
              name="current_cycle_used"
              value={form.current_cycle_used}
              onChange={(e) => handleCycleChange(e.target.value)}
              placeholder="e.g. 8.5"
              step="0.5"
              min="0"
              max="70"
              required
            />
          </label>

          <label>
            Trip Start Date &amp; Time
            <input
              type="datetime-local"
              name="start_datetime"
              value={form.start_datetime}
              onChange={(e) => handlePlaceChange('start_datetime', e.target.value)}
              required
            />
          </label>

          <button type="submit" disabled={loading}>
            {loading ? 'Creating...' : 'Create Trip'}
          </button>
        </form>

        <div className="right-panel">
          <TripMap route={tripData?.route} />
          <LogSheets logs={tripData?.logs} />
        </div>
      </main>

      <footer className="site-footer">
        <span>DutyMap · ELD Trip Planner</span>
        <span className="footer-credit">
          Built by{' '}
          <a href={BUILT_BY.portfolio} target="_blank" rel="noreferrer">
            {BUILT_BY.name}
          </a>
          <a
            className="footer-social"
            href={BUILT_BY.linkedin}
            target="_blank"
            rel="noreferrer"
            aria-label="LinkedIn"
            title="LinkedIn"
          >
            <svg viewBox="0 0 24 24" width="14" height="14" fill="currentColor" aria-hidden="true">
              <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.063 2.063 0 1 1 0-4.126 2.063 2.063 0 0 1 0 4.126zM7.119 20.452H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.225 0z" />
            </svg>
          </a>
        </span>
      </footer>
    </div>
  )
}

export default App
