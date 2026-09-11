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

  const { outboundLeg, inboundLeg } = useMemo(() => {
    const coords = route?.geometry?.coordinates
    const pickup = route?.coordinates?.pickup
    if (!coords?.length || !pickup) return { outboundLeg: [], inboundLeg: [] }

    const latlngs = coords.map(([lon, lat]) => [lat, lon])

    let bestIdx = 0
    let bestDist = Infinity
    for (let i = 0; i < latlngs.length; i++) {
      const [lat, lon] = latlngs[i]
      const d = (lat - pickup.lat) ** 2 + (lon - pickup.lon) ** 2
      if (d < bestDist) {
        bestDist = d
        bestIdx = i
      }
    }

    const outbound = latlngs.slice(0, bestIdx + 1)
    const inbound = latlngs.slice(bestIdx)

    if (outbound.length < 2 || inbound.length < 2) {
      return { outboundLeg: [], inboundLeg: [] }
    }
    return { outboundLeg: outbound, inboundLeg: inbound }
  }, [route])

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
        {outboundLeg.length > 0 && (
          <Polyline
            positions={outboundLeg}
            pathOptions={{ color: '#1976D2', weight: 4, opacity: 0.9 }}
          />
        )}
        {inboundLeg.length > 0 && (
          <Polyline
            positions={inboundLeg}
            pathOptions={{ color: '#E65100', weight: 4, opacity: 0.9, dashArray: '8, 6' }}
          />
        )}
        {outboundLeg.length === 0 && inboundLeg.length === 0 && polylineCoords.length > 0 && (
          <Polyline
            positions={polylineCoords}
            pathOptions={{ color: '#1976D2', weight: 4, opacity: 0.8 }}
          />
        )}
      </MapContainer>
      {(outboundLeg.length > 0 || inboundLeg.length > 0) && (
        <div className="route-legend">
          <div className="route-legend-item">
            <svg width="24" height="6" viewBox="0 0 24 6"><line x1="0" y1="3" x2="24" y2="3" stroke="#1976D2" strokeWidth="3" /></svg>
            <span>Current → Pickup</span>
          </div>
          <div className="route-legend-item">
            <svg width="24" height="6" viewBox="0 0 24 6"><line x1="0" y1="3" x2="24" y2="3" stroke="#E65100" strokeWidth="3" strokeDasharray="4,3" /></svg>
            <span>Pickup → Dropoff</span>
          </div>
        </div>
      )}
    </div>
  )
}
