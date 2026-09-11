import { MapContainer, TileLayer, Marker, Popup, Polyline, useMap } from 'react-leaflet'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

const markerIcons = {
  current: new L.DivIcon({
    className: 'marker-icon',
    html: '<div style="background:#22c55e;width:12px;height:12px;border-radius:50%;border:2px solid #fff;box-shadow:0 1px 3px rgba(0,0,0,.3)"></div>',
    iconSize: [12, 12],
    iconAnchor: [6, 6],
  }),
  pickup: new L.DivIcon({
    className: 'marker-icon',
    html: '<div style="background:#3b82f6;width:12px;height:12px;border-radius:50%;border:2px solid #fff;box-shadow:0 1px 3px rgba(0,0,0,.3)"></div>',
    iconSize: [12, 12],
    iconAnchor: [6, 6],
  }),
  dropoff: new L.DivIcon({
    className: 'marker-icon',
    html: '<div style="background:#ef4444;width:12px;height:12px;border-radius:50%;border:2px solid #fff;box-shadow:0 1px 3px rgba(0,0,0,.3)"></div>',
    iconSize: [12, 12],
    iconAnchor: [6, 6],
  }),
}

function FitBounds({ coords }) {
  const map = useMap()
  if (coords.length > 0) {
    const bounds = L.latLngBounds(coords)
    map.fitBounds(bounds, { padding: [40, 40] })
  }
  return null
}

export default function TripMap({ route }) {
  if (!route || !route.coordinates) {
    return (
      <div className="map-placeholder">
        <p>Submit a trip to see the route on the map</p>
      </div>
    )
  }

  const coords = route.coordinates
  const positions = [
    [coords.current.lat, coords.current.lon],
    [coords.pickup.lat, coords.pickup.lon],
    [coords.dropoff.lat, coords.dropoff.lon],
  ]

  const polylineCoords = route.geometry?.coordinates?.map(c => [c[1], c[0]]) || []

  const center = positions[0]

  return (
    <div className="map-container">
      {route.distance_miles && (
        <div className="route-stats">
          <span>{route.distance_miles} miles</span>
          <span>{route.duration_hours} hrs driving</span>
        </div>
      )}
      <MapContainer center={center} zoom={6} style={{ height: '100%', width: '100%' }}>
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
