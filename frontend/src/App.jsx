import { useState } from 'react'
import TripMap from './TripMap'
import { BUILT_BY } from './branding'
import './App.css'

const API_URL = 'http://localhost:8000/api/trips/'

const formatApiError = (data) => {
  if (!data) return 'Request failed'
  if (typeof data === 'string') return data
  if (data.error) return data.error
  if (data.detail) return data.detail
  return Object.entries(data)
    .map(([field, msgs]) => {
      const text = Array.isArray(msgs) ? msgs.join(' ') : msgs
      return `${field.replace(/_/g, ' ')}: ${text}`
    })
    .join('; ')
}

function App() {
  const [form, setForm] = useState({
    current_location: '',
    pickup_location: '',
    dropoff_location: '',
    current_cycle_used: '',
  })
  const [coordMode, setCoordMode] = useState({
    current: 'place',
    pickup: 'place',
    dropoff: 'place',
  })
  const [coords, setCoords] = useState({
    current: { lat: '', lon: '' },
    pickup: { lat: '', lon: '' },
    dropoff: { lat: '', lon: '' },
  })
  const [loading, setLoading] = useState(false)
  const [tripData, setTripData] = useState(null)
  const [error, setError] = useState(null)

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value })
  }

  const handleCoordChange = (field, axis, value) => {
    setCoords({
      ...coords,
      [field]: { ...coords[field], [axis]: value },
    })
  }

  const validateCoords = () => {
    for (const [field, label] of [['current', 'Current'], ['pickup', 'Pickup'], ['dropoff', 'Dropoff']]) {
      if (coordMode[field] !== 'latlong') continue
      const lat = parseFloat(coords[field].lat)
      const lon = parseFloat(coords[field].lon)
      if (isNaN(lat) || isNaN(lon)) {
        return `${label} coordinates must be valid numbers`
      }
      if (lat < -90 || lat > 90) {
        return `${label} latitude must be between -90 and 90`
      }
      if (lon < -180 || lon > 180) {
        return `${label} longitude must be between -180 and 180`
      }
    }
    return null
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError(null)

    const coordError = validateCoords()
    if (coordError) {
      setError(coordError)
      return
    }

    setLoading(true)
    setTripData(null)
    try {
      const body = {
        ...form,
        current_cycle_used: parseFloat(form.current_cycle_used),
      }
      for (const field of ['current', 'pickup', 'dropoff']) {
        if (coordMode[field] === 'latlong') {
          body[`${field}_location`] = ''
          body[`${field}_lat`] = parseFloat(coords[field].lat)
          body[`${field}_lon`] = parseFloat(coords[field].lon)
        }
      }
      const res = await fetch(API_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      })
      const data = await res.json()
      if (!res.ok) {
        setError(formatApiError(data))
        return
      }
      console.log('Trip response:', data)
      setTripData(data)
      if (data.route?.error) {
        setError(data.route.error)
      }
    } catch (err) {
      console.error('Error creating trip:', err)
      setError('Failed to connect to backend. Is it running on port 8000?')
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

          {[
            { key: 'current', label: 'Current Location', name: 'current_location', placeholder: 'e.g. Dallas, TX' },
            { key: 'pickup', label: 'Pickup Location', name: 'pickup_location', placeholder: 'e.g. Houston, TX' },
            { key: 'dropoff', label: 'Dropoff Location', name: 'dropoff_location', placeholder: 'e.g. Chicago, IL' },
          ].map(({ key, label, name, placeholder }) => (
            <fieldset key={key} className="location-fieldset">
              <div className="location-header">
                <label className="location-label">{label}</label>
                <div className="mode-switch" data-active={coordMode[key]}>
                  <span className="mode-switch-thumb" aria-hidden="true" />
                  <button
                    type="button"
                    className={`mode-switch-btn ${coordMode[key] === 'place' ? 'active' : ''}`}
                    onClick={() => setCoordMode({ ...coordMode, [key]: 'place' })}
                    aria-label={`${label}: enter a place name`}
                    aria-pressed={coordMode[key] === 'place'}
                    title="Search by place name"
                  >
                    <svg viewBox="0 0 24 24" width="12" height="12" fill="currentColor" aria-hidden="true">
                      <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5a2.5 2.5 0 1 1 0-5 2.5 2.5 0 0 1 0 5z" />
                    </svg>
                  </button>
                  <button
                    type="button"
                    className={`mode-switch-btn ${coordMode[key] === 'latlong' ? 'active' : ''}`}
                    onClick={() => setCoordMode({ ...coordMode, [key]: 'latlong' })}
                    aria-label={`${label}: enter latitude and longitude`}
                    aria-pressed={coordMode[key] === 'latlong'}
                    title="Enter latitude / longitude"
                  >
                    <svg viewBox="0 0 24 24" width="12" height="12" fill="currentColor" aria-hidden="true">
                      <path d="M12 8a4 4 0 1 0 0 8 4 4 0 0 0 0-8zm8.94 3A8.994 8.994 0 0 0 13 3.06V1h-2v2.06A8.994 8.994 0 0 0 3.06 11H1v2h2.06A8.994 8.994 0 0 0 11 20.94V23h2v-2.06A8.994 8.994 0 0 0 20.94 13H23v-2h-2.06zM12 19a7 7 0 1 1 0-14 7 7 0 0 1 0 14z" />
                    </svg>
                  </button>
                </div>
              </div>
              {coordMode[key] === 'place' ? (
                <input
                  type="text"
                  name={name}
                  value={form[name]}
                  onChange={handleChange}
                  placeholder={placeholder}
                  required
                />
              ) : (
                <div className="coord-inputs">
                  <input
                    type="number"
                    placeholder="Lat"
                    value={coords[key].lat}
                    onChange={(e) => handleCoordChange(key, 'lat', e.target.value)}
                    min="-90"
                    max="90"
                    step="any"
                    aria-label={`${label} latitude in decimal degrees`}
                    title="Latitude in decimal degrees — positive is North, negative is South (e.g. 32.7767 or -33.8688)"
                    required
                  />
                  <input
                    type="number"
                    placeholder="Lon"
                    value={coords[key].lon}
                    onChange={(e) => handleCoordChange(key, 'lon', e.target.value)}
                    min="-180"
                    max="180"
                    step="any"
                    aria-label={`${label} longitude in decimal degrees`}
                    title="Longitude in decimal degrees — positive is East, negative is West (e.g. -96.7970 or 151.2093)"
                    required
                  />
                </div>
              )}
            </fieldset>
          ))}

          <label>
            Current Cycle Used (hours)
            <input
              type="number"
              name="current_cycle_used"
              value={form.current_cycle_used}
              onChange={handleChange}
              placeholder="e.g. 8.5"
              step="0.5"
              min="0"
              max="70"
              required
            />
          </label>

          <button type="submit" disabled={loading}>
            {loading ? 'Creating...' : 'Create Trip'}
          </button>
        </form>

        <div className="right-panel">
          <TripMap route={tripData?.route} />
          <div className="placeholder-box">
            <h3>Log Sheets</h3>
            <p>ELD log sheets will go here</p>
          </div>
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
