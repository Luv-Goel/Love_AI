/**
 * Logs — filterable request log viewer.
 * Fetches live jail state from /admin/api/v1/jails as a proxy for recent
 * system events; a proper streaming log endpoint can be added later.
 */
import { useState } from 'preact/hooks'
import { getLogs } from '../api'
import { useAsync } from '../hooks/useAsync'
import { Spinner, Banner } from './Dashboard'

const LEVEL_BADGE = {
  INFO:  'bg-blue-100  text-blue-700',
  WARN:  'bg-amber-100 text-amber-700',
  ERROR: 'bg-rose-100  text-rose-700',
}

export function Logs() {
  const { data: logs, loading, error, refetch } = useAsync(getLogs)
  const [filter, setFilter] = useState('')

  // Build combined log list
  const liveLogs = (logs ?? []).map(l => {
    // Collect all fields other than time, level, msg for the detail string
    const details = Object.entries(l)
      .filter(([k]) => k !== 'time' && k !== 'level' && k !== 'msg')
      .map(([k, v]) => `${k}=${v}`)
      .join(' ')
    return {
      ts:     l.time,
      level:  (l.level || 'INFO').toUpperCase(),
      msg:    l.msg,
      detail: details,
    }
  })

  const visible = liveLogs.filter(l =>
    !filter ||
    l.msg?.toLowerCase().includes(filter.toLowerCase()) ||
    l.detail?.toLowerCase().includes(filter.toLowerCase()),
  )

  return (
    <div class="space-y-4">
      <div class="flex items-center justify-between gap-4 flex-wrap">
        <h2 class="text-xl font-semibold shrink-0">System Logs</h2>
        <input
          type="text"
          placeholder="Filter logs…"
          value={filter}
          onInput={e => setFilter(e.currentTarget.value)}
          class="flex-1 max-w-sm text-sm border border-gray-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-300"
        />
        <div class="flex items-center gap-2 shrink-0">
          <span class="text-sm text-gray-400">{visible.length} entries</span>
          <button onClick={refetch}
            class="text-xs text-indigo-600 hover:text-indigo-800 font-medium border border-indigo-200 rounded px-2 py-1">
            Refresh
          </button>
        </div>
      </div>

      {error && <Banner type="error">{error}</Banner>}

      {loading ? <Spinner /> : (
        <div class="rounded-xl border border-gray-200 bg-white overflow-hidden font-mono text-xs">
          {visible.length === 0 ? (
            <p class="px-4 py-8 text-center text-gray-400">No log entries match your filter.</p>
          ) : (
            <table class="w-full">
              <thead>
                <tr class="border-b border-gray-100 bg-gray-50">
                  <th class="text-left px-4 py-2 font-medium text-gray-500 w-44">Time</th>
                  <th class="text-left px-4 py-2 font-medium text-gray-500 w-16">Level</th>
                  <th class="text-left px-4 py-2 font-medium text-gray-500">Message</th>
                  <th class="text-left px-4 py-2 font-medium text-gray-500">Detail</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-50">
                {visible.map((l, i) => (
                  <tr key={i} class="hover:bg-gray-50 transition-colors">
                    <td class="px-4 py-2 text-gray-400 truncate max-w-[11rem]">{l.ts}</td>
                    <td class="px-4 py-2">
                      <span class={`inline-block font-semibold px-1.5 py-0.5 rounded ${LEVEL_BADGE[l.level] ?? ''}`}>
                        {l.level}
                      </span>
                    </td>
                    <td class="px-4 py-2 text-gray-800">{l.msg}</td>
                    <td class="px-4 py-2 text-gray-500">{l.detail}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      )}
    </div>
  )
}
