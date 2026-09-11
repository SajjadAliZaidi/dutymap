import { useState } from 'react'

function formatTabDate(iso) {
  const [, month, day] = iso.split('-')
  const d = new Date(Number(iso.slice(0, 4)), Number(month) - 1, Number(day))
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
}

export default function LogSheets({ logs }) {
  const [active, setActive] = useState(0)

  if (!logs || logs.length === 0) {
    return (
      <div className="log-sheets log-sheets--empty">
        <p>No HOS segments for this trip</p>
      </div>
    )
  }

  return (
    <div className="log-sheets">
      {logs.length > 1 && (
        <div className="log-tabs">
          {logs.map((entry, i) => (
            <button
              key={entry.date}
              type="button"
              className={`log-tab ${i === active ? 'log-tab--active' : ''}`}
              onClick={() => setActive(i)}
            >
              {formatTabDate(entry.date)}
            </button>
          ))}
        </div>
      )}
      <div className="log-sheet">
        <div dangerouslySetInnerHTML={{ __html: logs[active].svg }} />
      </div>
    </div>
  )
}
