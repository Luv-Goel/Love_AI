/**
 * Dashboard — live system overview fetched from /admin/api/v1/metrics-summary
 * and /admin/api/v1/jails.
 */
import { getMetricsSummary, listJails } from '../api'
import { useAsync } from '../hooks/useAsync'
import { useEffect } from 'preact/hooks'

const ACCENT = {
  indigo:  'bg-indigo-50  text-indigo-700  border-indigo-200',
  emerald: 'bg-emerald-50 text-emerald-700 border-emerald-200',
  rose:    'bg-rose-50    text-rose-700    border-rose-200',
  amber:   'bg-amber-50   text-amber-700   border-amber-200',
}

function StatCard({ label, value, accent }) {
  return (
    <div class={`rounded-xl border p-5 flex flex-col gap-1 ${ACCENT[accent]}`}>
      <span class="text-3xl font-bold">{value}</span>
      <span class="text-sm font-medium opacity-70">{label}</span>
    </div>
  )
}

function sum(obj) {
  return obj ? Object.values(obj).reduce((a, b) => a + b, 0) : 0
}

export function Dashboard() {
  const { data: metrics, loading: mLoad, error: mErr, refetch: mRefetch } = useAsync(getMetricsSummary)
  const { data: jails,   loading: jLoad, error: jErr, refetch: jRefetch } = useAsync(listJails)

  useEffect(() => {
    const timer = setInterval(() => {
      mRefetch()
      jRefetch()
    }, 2000)
    return () => clearInterval(timer)
  }, [mRefetch, jRefetch])

  // Only sum the ':received' state to avoid double-counting requests that are both received and completed
  const totalRequests = metrics ? 
    Object.entries(metrics.requests_total || {})
      .filter(([key]) => key.endsWith(':received'))
      .reduce((acc, [_, val]) => acc + val, 0) 
    : '–'
  const activeStreams  = metrics ? metrics.active_streams      : '–'
  const jailedCount   = metrics ? metrics.jailed_backends     : '–'
  const totalTokens   = metrics ? sum(metrics.tokens_total)   : '–'

  return (
    <div class="space-y-8">
      <section>
        <h2 class="text-xl font-semibold mb-4">System Overview</h2>
        {mErr && <Banner type="error">{mErr}</Banner>}
        <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard label="Requests total"  value={mLoad ? '…' : totalRequests} accent="indigo"  />
          <StatCard label="Active streams"  value={mLoad ? '…' : activeStreams}  accent="emerald" />
          <StatCard label="Jailed backends" value={mLoad ? '…' : jailedCount}   accent="rose"    />
          <StatCard label="Total tokens"    value={mLoad ? '…' : totalTokens}   accent="amber"   />
        </div>
      </section>

      <section>
        <h2 class="text-xl font-semibold mb-3">Token Breakdown</h2>
        {mErr ? (
          <Banner type="error">{mErr}</Banner>
        ) : mLoad ? (
          <Spinner />
        ) : (
          <div class="rounded-xl border border-gray-200 bg-white overflow-hidden">
            <table class="w-full text-sm">
              <thead>
                <tr class="border-b border-gray-100 bg-gray-50">
                  <th class="text-left px-4 py-3 font-medium text-gray-500">Virtual Model · Kind</th>
                  <th class="text-right px-4 py-3 font-medium text-gray-500">Tokens</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-100">
                {Object.keys(metrics?.tokens_total ?? {}).length === 0 ? (
                  <tr><td colspan="2" class="px-4 py-8 text-center text-gray-400">No token data yet.</td></tr>
                ) : (
                  Object.entries(metrics.tokens_total).map(([key, val]) => (
                    <tr key={key} class="hover:bg-gray-50">
                      <td class="px-4 py-3 font-mono text-xs text-gray-700">{key}</td>
                      <td class="px-4 py-3 text-right tabular-nums">{val.toLocaleString()}</td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        )}
      </section>

      <section>
        <h2 class="text-xl font-semibold mb-3">Jailed Backends</h2>
        {jErr ? (
          <Banner type="error">{jErr}</Banner>
        ) : jLoad ? (
          <Spinner />
        ) : (jails ?? []).length === 0 ? (
          <p class="text-gray-400 text-sm">No backends in jail — all systems healthy.</p>
        ) : (
          <div class="rounded-xl border border-gray-200 bg-white overflow-hidden">
            <table class="w-full text-sm">
              <thead>
                <tr class="border-b border-gray-100 bg-gray-50">
                  <th class="text-left px-4 py-3 font-medium text-gray-500">Vendor</th>
                  <th class="text-left px-4 py-3 font-medium text-gray-500">Model</th>
                  <th class="text-left px-4 py-3 font-medium text-gray-500">Tier</th>
                  <th class="text-left px-4 py-3 font-medium text-gray-500">Jailed Until</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-100">
                {jails.map((j, i) => (
                  <tr key={i} class="hover:bg-gray-50">
                    <td class="px-4 py-3 font-medium">{j.vendor}</td>
                    <td class="px-4 py-3 font-mono text-xs">{j.model}</td>
                    <td class="px-4 py-3">{j.jail_tier}</td>
                    <td class="px-4 py-3 text-gray-500 text-xs">{j.jail_until}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </div>
  )
}

export function Spinner() {
  return <div class="py-8 text-center text-gray-400 text-sm animate-pulse">Loading…</div>
}

export function Banner({ type, children }) {
  const cls = type === 'error'
    ? 'bg-rose-50 text-rose-700 border-rose-200'
    : 'bg-emerald-50 text-emerald-700 border-emerald-200'
  return <div class={`rounded-lg border px-4 py-3 text-sm mb-4 ${cls}`}>{children}</div>
}
