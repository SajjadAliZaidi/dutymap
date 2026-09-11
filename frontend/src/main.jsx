import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'
import { BUILT_BY, PROJECT } from './branding'

console.log(
  `%c${PROJECT.name}%c ${PROJECT.tagline}\n%cBuilt by ${BUILT_BY.name} — ${BUILT_BY.portfolio}`,
  'font-size:1.4rem;font-weight:700;color:#16213e;',
  'font-size:0.8rem;color:#6b7280;',
  'font-size:0.75rem;color:#3b82f6;',
)

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
