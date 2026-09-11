import { useState } from 'react'
import TripMap from './TripMap'
import { BUILT_BY } from './branding'
import './App.css'

const API_URL = 'http://localhost:8000/api/trips/'

function App() {
  const [form, setForm] = useState({
    current_location: '',
    pickup_location: '',
    dropoff_location: '',
    current_cycle_used: '',
  })
  const [loading, setLoading] = useState(false)
  const [tripData, setTripData] = useState(null)
  const [error, setError] = useState(null)

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    setTripData(null)
    try {
      const res = await fetch(API_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...form,
          current_cycle_used: parseFloat(form.current_cycle_used),
        }),
      })
      const data = await res.json()
      if (!res.ok) {
        setError(data.error || data.detail || JSON.stringify(data))
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

          <label>
            Current Location
            <input
              type="text"
              name="current_location"
              value={form.current_location}
              onChange={handleChange}
              placeholder="e.g. Dallas, TX"
              required
            />
          </label>

          <label>
            Pickup Location
            <input
              type="text"
              name="pickup_location"
              value={form.pickup_location}
              onChange={handleChange}
              placeholder="e.g. Houston, TX"
              required
            />
          </label>

          <label>
            Dropoff Location
            <input
              type="text"
              name="dropoff_location"
              value={form.dropoff_location}
              onChange={handleChange}
              placeholder="e.g. Chicago, IL"
              required
            />
          </label>

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
