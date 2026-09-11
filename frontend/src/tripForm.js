export const LOCATIONS = [
  {
    key: 'current',
    label: 'Current Location',
    name: 'current_location',
    placeholder: 'e.g. Dallas, TX',
  },
  {
    key: 'pickup',
    label: 'Pickup Location',
    name: 'pickup_location',
    placeholder: 'e.g. Houston, TX',
  },
  {
    key: 'dropoff',
    label: 'Dropoff Location',
    name: 'dropoff_location',
    placeholder: 'e.g. Chicago, IL',
  },
]

export const PLACE = 'place'
export const LATLONG = 'latlong'

export const emptyModes = () =>
  Object.fromEntries(LOCATIONS.map(({ key }) => [key, PLACE]))

export const emptyCoords = () =>
  Object.fromEntries(LOCATIONS.map(({ key }) => [key, { lat: '', lon: '' }]))

export function validateCoords(modes, coords) {
  for (const { key, label } of LOCATIONS) {
    if (modes[key] !== LATLONG) continue

    const lat = Number.parseFloat(coords[key].lat)
    const lon = Number.parseFloat(coords[key].lon)

    if (Number.isNaN(lat) || Number.isNaN(lon)) {
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

export function buildTripPayload(form, modes, coords) {
  const payload = {
    ...form,
    current_cycle_used: Number.parseFloat(form.current_cycle_used),
    start_datetime: form.start_datetime || '',
  }

  for (const { key } of LOCATIONS) {
    if (modes[key] !== LATLONG) continue

    // Clear any place name left over from the other mode so the backend does
    // not treat it as the source of truth.
    payload[`${key}_location`] = ''
    payload[`${key}_lat`] = Number.parseFloat(coords[key].lat)
    payload[`${key}_lon`] = Number.parseFloat(coords[key].lon)
  }

  return payload
}
