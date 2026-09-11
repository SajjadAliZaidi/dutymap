import { useState } from 'react'
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

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
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
      console.log('Trip response:', data)
      alert('Trip created! Check console for response.')
    } catch (err) {
      console.error('Error creating trip:', err)
      alert('Failed to create trip. Is the backend running?')
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

        <div className="placeholders">
          <div className="placeholder-box">
            <h3>Map</h3>
            <p>Route visualization will go here</p>
          </div>
          <div className="placeholder-box">
            <h3>Log Sheets</h3>
            <p>ELD log sheets will go here</p>
          </div>
        </div>
      </main>
    </div>
  )
}

export default App
