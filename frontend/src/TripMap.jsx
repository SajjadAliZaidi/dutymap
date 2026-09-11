import { useEffect, useMemo } from 'react'
import { MapContainer, TileLayer, Marker, Popup, Polyline, useMap } from 'react-leaflet'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

const marker = (color) =>
  new L.DivIcon({
    className: 'marker-icon',
    html: `<div style="background:${color};width:12px;height:12px;border-radius:50%;border:2px solid #fff;box-shadow:0 1px 3px rgba(0,0,0,.3)"></div>`,
    iconSize: [12, 12],
    iconAnchor: [6, 6],
  })

const markerIcons = {
  current: marker('#22c55e'),
  pickup: marker('#3b82f6'),
  dropoff: marker('#ef4444'),
}

function FitBounds({ coords }) {
  const map = useMap()

  useEffect(() => {
    if (coords.length > 0) {
      map.fitBounds(L.latLngBounds(coords), { padding: [40, 40] })
    }
  }, [map, coords])

  return null
}

export default function TripMap({ route }) {
  const positions = useMemo(() => {
    const stops = route?.coordinates
    if (!stops) return []
    const ordered = [stops.current, stops.pickup, stops.dropoff]
    if (ordered.some((c) => c == null || c.lat == null || c.lon == null)) return []
    return ordered.map((c) => [c.lat, c.lon])
  }, [route])

  const polylineCoords = useMemo(
    () => route?.geometry?.coordinates?.map(([lon, lat]) => [lat, lon]) ?? [],
    [route],
  )

  if (positions.length === 0) {
    return (
      <div className="map-placeholder">
        <p>Submit a trip to see the route on the map</p>
      </div>
    )
  }

  return (
    <div className="map-container">
      {route.distance_miles != null && (
        <div className="route-stats">
          <span>{route.distance_miles} miles</span>
          <span>{route.duration_hours} hrs driving</span>
        </div>
      )}
      <MapContainer center={positions[0]} zoom={6} style={{ height: '100%', width: '100%' }}>
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        <FitBounds coords={positions} />
        <Marker position={positions[0]} icon={markerIcons.current}>
          <Popup>Current Location</Popup>
        </Marker>
        <Marker position={positions[1]} icon={markerIcons.pickup}>
          <Popup>Pickup</Popup>
        </Marker>
        <Marker position={positions[2]} icon={markerIcons.dropoff}>
          <Popup>Dropoff</Popup>
        </Marker>
        {polylineCoords.length > 0 && (
          <Polyline
            positions={polylineCoords}
            pathOptions={{ color: '#3b82f6', weight: 4, opacity: 0.8 }}
          />
        )}
      </MapContainer>
    </div>
  )
}
