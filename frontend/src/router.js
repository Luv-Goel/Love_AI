/**
 * Minimal hash-based router.
 *
 * Routes are keyed on the fragment after "#", e.g. "#/providers" → "providers".
 * Default route is "dashboard".
 */
import { useState, useEffect } from 'preact/hooks'

function getRoute() {
  const hash = window.location.hash.replace(/^#\/?/, '')
  return hash || 'dashboard'
}

export function useRoute() {
  const [route, setRoute] = useState(getRoute)

  useEffect(() => {
    const handler = () => setRoute(getRoute())
    window.addEventListener('hashchange', handler)
    return () => window.removeEventListener('hashchange', handler)
  }, [])

  return route
}

export function navigate(to) {
  window.location.hash = '/' + to
}
