import { useEffect, useRef, useState } from 'react'
import { searchLocations } from './api'

const SearchIcon = () => (
  <svg viewBox="0 0 24 24" width="14" height="14" fill="currentColor" aria-hidden="true">
    <path d="M15.5 14h-.79l-.28-.27a6.5 6.5 0 0 0 1.48-5.34c-.47-2.78-2.79-5-5.59-5.34a6.505 6.505 0 0 0-7.34 7.34c.34 2.8 2.56 5.12 5.34 5.59a6.5 6.5 0 0 0 5.34-1.48l.27.28v.79l4.25 4.25a1.09 1.09 0 0 0 1.54-1.54L15.5 14zm-6 0a4.5 4.5 0 1 1 0-9 4.5 4.5 0 0 1 0 9z" />
  </svg>
)

export default function AutocompleteInput({
  value,
  onChange,
  placeholder,
  required = false,
}) {
  const [open, setOpen] = useState(false)
  const [suggestions, setSuggestions] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const containerRef = useRef(null)

  useEffect(() => {
    function handleClickOutside(event) {
      if (containerRef.current && !containerRef.current.contains(event.target)) {
        setOpen(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const doSearch = async () => {
    if (!value.trim()) return
    setLoading(true)
    setError(null)
    setOpen(true)
    try {
      const results = await searchLocations(value)
      setSuggestions(results)
    } catch (err) {
      setSuggestions([])
      setError(err.message || 'Search failed')
    } finally {
      setLoading(false)
    }
  }

  const handleSelect = (displayName) => {
    onChange(displayName)
    setOpen(false)
  }

  const handleKeyDown = (event) => {
    if (event.key === 'Enter') {
      event.preventDefault()
      doSearch()
    }
  }

  return (
    <div className="autocomplete" ref={containerRef}>
      <div className="autocomplete-input-wrap">
        <input
          type="text"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          required={required}
        />
        <button
          type="button"
          className="autocomplete-search-btn"
          onClick={doSearch}
          disabled={loading || !value.trim()}
          aria-label="Search addresses"
          title="Search addresses"
        >
          {loading ? (
            <span className="autocomplete-spinner" aria-label="Searching" />
          ) : (
            <SearchIcon />
          )}
        </button>
      </div>

      {open && (
        <ul className="autocomplete-dropdown">
          {error ? (
            <li className="autocomplete-error">{error}</li>
          ) : suggestions.length === 0 ? (
            <li className="autocomplete-empty">No matches found</li>
          ) : (
            suggestions.map((suggestion, index) => (
              <li
                key={index}
                className="autocomplete-item"
                onClick={() => handleSelect(suggestion.display_name)}
              >
                {suggestion.display_name}
              </li>
            ))
          )}
        </ul>
      )}
    </div>
  )
}
