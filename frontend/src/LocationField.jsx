import { LATLONG, PLACE } from './tripForm'
import AutocompleteInput from './AutocompleteInput'

const PinIcon = () => (
  <svg viewBox="0 0 24 24" width="12" height="12" fill="currentColor" aria-hidden="true">
    <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5a2.5 2.5 0 1 1 0-5 2.5 2.5 0 0 1 0 5z" />
  </svg>
)

const CrosshairIcon = () => (
  <svg viewBox="0 0 24 24" width="12" height="12" fill="currentColor" aria-hidden="true">
    <path d="M12 8a4 4 0 1 0 0 8 4 4 0 0 0 0-8zm8.94 3A8.994 8.994 0 0 0 13 3.06V1h-2v2.06A8.994 8.994 0 0 0 3.06 11H1v2h2.06A8.994 8.994 0 0 0 11 20.94V23h2v-2.06A8.994 8.994 0 0 0 20.94 13H23v-2h-2.06zM12 19a7 7 0 1 1 0-14 7 7 0 0 1 0 14z" />
  </svg>
)

function ModeSwitch({ label, mode, onChange }) {
  return (
    <div className="mode-switch" data-active={mode}>
      <span className="mode-switch-thumb" aria-hidden="true" />
      <button
        type="button"
        className={`mode-switch-btn ${mode === PLACE ? 'active' : ''}`}
        onClick={() => onChange(PLACE)}
        aria-label={`${label}: enter a place name`}
        aria-pressed={mode === PLACE}
        title="Search by place name"
      >
        <PinIcon />
      </button>
      <button
        type="button"
        className={`mode-switch-btn ${mode === LATLONG ? 'active' : ''}`}
        onClick={() => onChange(LATLONG)}
        aria-label={`${label}: enter latitude and longitude`}
        aria-pressed={mode === LATLONG}
        title="Enter latitude / longitude"
      >
        <CrosshairIcon />
      </button>
    </div>
  )
}

export default function LocationField({
  field,
  mode,
  coords,
  value,
  onModeChange,
  onPlaceChange,
  onCoordChange,
}) {
  const { label, name, placeholder } = field

  return (
    <fieldset className="location-fieldset">
      <div className="location-header">
        <label className="location-label">{label}</label>
        <ModeSwitch label={label} mode={mode} onChange={onModeChange} />
      </div>

      {mode === PLACE ? (
        <AutocompleteInput
          value={value}
          onChange={(next) => onPlaceChange(name, next)}
          placeholder={placeholder}
          required
        />
      ) : (
        <div className="coord-inputs">
          <input
            type="number"
            placeholder="Lat"
            value={coords.lat}
            onChange={(e) => onCoordChange('lat', e.target.value)}
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
            value={coords.lon}
            onChange={(e) => onCoordChange('lon', e.target.value)}
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
  )
}
