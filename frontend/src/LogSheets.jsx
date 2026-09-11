export default function LogSheets({ logs }) {
  if (!logs || logs.length === 0) {
    return (
      <div className="log-sheets log-sheets--empty">
        <p>No HOS segments for this trip</p>
      </div>
    )
  }

  return (
    <div className="log-sheets">
      <h3>ELD Daily Logs</h3>
      {logs.map((entry) => (
        <div key={entry.date} className="log-sheet">
          <div dangerouslySetInnerHTML={{ __html: entry.svg }} />
        </div>
      ))}
    </div>
  )
}
