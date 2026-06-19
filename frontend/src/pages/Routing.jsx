/**
 * Routing — live waterfall rules with inline priority/weight/enabled editing
 * and a create-rule form.  Changes are saved via PUT /admin/api/v1/routing-rules/{id}
 * which triggers the Go hot-reload so live requests pick up the new order immediately.
 */
import { useState } from 'preact/hooks'
import {
  listRoutingRules,
  createRoutingRule,
  updateRoutingRule,
  deleteRoutingRule,
  listVirtualModels,
  listProviders,
  syncIndividualModels,
} from '../api'
import { useAsync } from '../hooks/useAsync'
import { Spinner, Banner } from './Dashboard'

export function Routing() {
  const { data: rules,  loading: rLoad, error: rErr,  refetch: refetchRules  } = useAsync(listRoutingRules)
  const { data: vms,    loading: vmLoad }                                       = useAsync(listVirtualModels)
  const { data: vendors,loading: vLoad  }                                       = useAsync(listProviders)

  const [editID,    setEditID]    = useState(null)
  const [editVals,  setEditVals]  = useState({})
  const [saving,    setSaving]    = useState(false)
  const [saveErr,   setSaveErr]   = useState(null)

  const [searchQuery, setSearchQuery] = useState('')
  const [syncing, setSyncing] = useState(false)

  const [expandedGroups, setExpandedGroups] = useState({})

  const [showCreate, setShowCreate] = useState(false)
  const [newRule, setNewRule] = useState({ virtual_model:'', vendor:'', model_name:'', priority:1, weight:100 })
  const [creating, setCreating] = useState(false)
  const [createErr, setCreateErr] = useState(null)

  function toggleGroup(vm) {
    setExpandedGroups(prev => ({ ...prev, [vm]: !prev[vm] }))
  }

  function startEdit(rule) {
    setEditID(rule.id)
    setEditVals({ priority: rule.priority, weight: rule.weight, enabled: rule.enabled })
    setSaveErr(null)
  }

  function cancelEdit() { setEditID(null); setEditVals({}) }

  async function saveEdit(id) {
    setSaving(true); setSaveErr(null)
    try {
      await updateRoutingRule(id, {
        priority: Number(editVals.priority),
        weight:   Number(editVals.weight),
        enabled:  editVals.enabled,
      })
      cancelEdit()
      refetchRules()
    } catch (err) {
      setSaveErr(err.message)
    } finally {
      setSaving(false)
    }
  }

  async function handleDelete(id) {
    if (!confirm('Delete this routing rule?')) return
    try {
      await deleteRoutingRule(id)
      refetchRules()
    } catch (err) {
      alert('Delete failed: ' + err.message)
    }
  }

  async function handleCreate(e) {
    e.preventDefault()
    setCreating(true); setCreateErr(null)
    try {
      await createRoutingRule({
        ...newRule,
        priority: Number(newRule.priority),
        weight:   Number(newRule.weight),
      })
      setNewRule({ virtual_model:'', vendor:'', model_name:'', priority:1, weight:100 })
      setShowCreate(false)
      refetchRules()
    } catch (err) {
      setCreateErr(err.message)
    } finally {
      setCreating(false)
    }
  }

  async function handleSync() {
    setSyncing(true)
    try {
      await syncIndividualModels()
      refetchRules()
    } catch (err) {
      alert('Sync failed: ' + err.message)
    } finally {
      setSyncing(false)
    }
  }

  return (
    <div class="space-y-6">
      <div class="flex items-center justify-between">
        <h2 class="text-xl font-semibold">Routing Rules</h2>
        <div class="flex space-x-3 items-center">
          <input 
            type="text" 
            placeholder="Search rules..." 
            value={searchQuery}
            onInput={e => setSearchQuery(e.currentTarget.value)}
            class="text-sm border border-gray-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-300 w-64"
          />
          <button
            onClick={handleSync}
            disabled={syncing}
            class="text-sm bg-gray-100 hover:bg-gray-200 text-gray-700 font-medium px-4 py-2 rounded-lg transition-colors disabled:opacity-50"
          >
            {syncing ? 'Refreshing...' : 'Refresh Individual Models'}
          </button>
          <button
            onClick={() => { setShowCreate(c => !c); setCreateErr(null) }}
            class="text-sm bg-indigo-600 hover:bg-indigo-700 text-white font-medium px-4 py-2 rounded-lg transition-colors"
          >
            {showCreate ? 'Cancel' : '+ Add Rule'}
          </button>
        </div>
      </div>

      {/* Create form */}
      {showCreate && (
        <form onSubmit={handleCreate} class="rounded-xl border border-gray-200 bg-white p-5 space-y-4">
          <h3 class="font-semibold text-gray-800">New Routing Rule</h3>
          {createErr && <Banner type="error">{createErr}</Banner>}
          <div class="grid grid-cols-2 sm:grid-cols-3 gap-4">
            <Field label="Virtual model">
              <select value={newRule.virtual_model}
                onChange={e => setNewRule(r => ({...r, virtual_model: e.currentTarget.value}))}
                required class={inputCls}>
                <option value="">Select…</option>
                {!vmLoad && (vms ?? []).map(v => <option key={v.name} value={v.name}>{v.name}</option>)}
              </select>
            </Field>
            <Field label="Vendor">
              <select value={newRule.vendor}
                onChange={e => setNewRule(r => ({...r, vendor: e.currentTarget.value}))}
                required class={inputCls}>
                <option value="">Select…</option>
                {!vLoad && (vendors ?? []).map(v => <option key={v.name} value={v.name}>{v.name}</option>)}
              </select>
            </Field>
            <Field label="Model name">
              <input type="text" value={newRule.model_name} required placeholder="gpt-4o"
                onInput={e => setNewRule(r => ({...r, model_name: e.currentTarget.value}))}
                class={inputCls} />
            </Field>
            <Field label="Priority">
              <input type="number" min="0" value={newRule.priority}
                onInput={e => setNewRule(r => ({...r, priority: e.currentTarget.value}))}
                class={inputCls} />
            </Field>
            <Field label="Weight">
              <input type="number" min="1" max="1000" value={newRule.weight}
                onInput={e => setNewRule(r => ({...r, weight: e.currentTarget.value}))}
                class={inputCls} />
            </Field>
          </div>
          <button type="submit" disabled={creating}
            class="bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white text-sm font-medium px-5 py-2 rounded-lg transition-colors">
            {creating ? 'Creating…' : 'Create Rule'}
          </button>
        </form>
      )}

      {/* Info banner */}
      <div class="rounded-xl border border-indigo-100 bg-indigo-50 px-4 py-3 text-sm text-indigo-700">
        Rules are tried in <strong>priority order</strong> (lowest first). Edit inline and
        save — changes take effect on <strong>live requests immediately</strong> (no restart needed).
      </div>

      {saveErr && <Banner type="error">{saveErr}</Banner>}

      {/* Table */}
      {rErr ? <Banner type="error">{rErr}</Banner>
        : rLoad ? <Spinner />
        : (
          <div class="rounded-xl border border-gray-200 bg-white overflow-hidden">
            <table class="w-full text-sm">
              <thead>
                <tr class="border-b border-gray-100 bg-gray-50">
                  <th class="text-left px-4 py-3 font-medium text-gray-500">Virtual Model</th>
                  <th class="text-left px-4 py-3 font-medium text-gray-500">Vendor</th>
                  <th class="text-left px-4 py-3 font-medium text-gray-500">Model</th>
                  <th class="text-left px-4 py-3 font-medium text-gray-500 w-24">Priority</th>
                  <th class="text-left px-4 py-3 font-medium text-gray-500 w-24">Weight</th>
                  <th class="text-left px-4 py-3 font-medium text-gray-500 w-20">Enabled</th>
                  <th class="text-right px-4 py-3 font-medium text-gray-500">Actions</th>
                </tr>
              </thead>
              {(() => {
                const query = searchQuery.toLowerCase()
                const filteredRules = (rules ?? []).filter(r => 
                  !query || 
                  r.virtual_model.toLowerCase().includes(query) ||
                  r.vendor.toLowerCase().includes(query) ||
                  r.model_name.toLowerCase().includes(query)
                )

                const groupedRules = filteredRules.reduce((acc, r) => {
                  if (!acc[r.virtual_model]) acc[r.virtual_model] = []
                  acc[r.virtual_model].push(r)
                  return acc
                }, {})

                if (Object.keys(groupedRules).length === 0) {
                  return (
                    <tbody>
                      <tr><td colspan="7" class="px-4 py-8 text-center text-gray-400">No routing rules.</td></tr>
                    </tbody>
                  )
                }

                return Object.entries(groupedRules).map(([vmName, vmRules]) => {
                  const isExpanded = expandedGroups[vmName]
                  const vmDesc = (vms ?? []).find(v => v.name === vmName)?.description || ''
                  return (
                    <tbody key={vmName} class="divide-y divide-gray-100">
                      <tr class="bg-indigo-50/50 cursor-pointer hover:bg-indigo-50 border-t border-gray-200" onClick={() => toggleGroup(vmName)}>
                        <td colspan="7" class="px-4 py-3 font-semibold text-indigo-800">
                          <span class="inline-block w-4 mr-2 text-center">{isExpanded ? '▼' : '▶'}</span>
                          Virtual Model: <span title={vmDesc || undefined} class={`font-mono text-xs ml-1 bg-white px-2 py-0.5 rounded border border-indigo-200 ${vmDesc ? 'cursor-help' : ''}`}>{vmName}</span>
                          <span class="ml-3 text-xs text-indigo-500 font-normal">({vmRules.length} rules)</span>
                        </td>
                      </tr>
                      {isExpanded && vmRules.map(r => {
                        const isEditing = editID === r.id
                        return (
                          <tr key={r.id} class={`transition-colors ${isEditing ? 'bg-indigo-50' : 'hover:bg-gray-50'}`}>
                            <td class="px-4 py-3 text-gray-400 font-mono text-xs text-center pl-8">↳</td>
                            <td class="px-4 py-3 font-medium">{r.vendor}</td>
                            <td class="px-4 py-3 text-gray-500 font-mono text-xs">{r.model_name}</td>
                            <td class="px-4 py-3">
                              {isEditing
                                ? <input type="number" min="0" value={editVals.priority}
                                    onInput={e => setEditVals(v => ({...v, priority: e.currentTarget.value}))}
                                    class="w-20 text-sm border border-indigo-300 rounded px-2 py-1 focus:outline-none focus:ring-1 focus:ring-indigo-400" />
                                : r.priority}
                            </td>
                            <td class="px-4 py-3">
                              {isEditing
                                ? <input type="number" min="1" max="1000" value={editVals.weight}
                                    onInput={e => setEditVals(v => ({...v, weight: e.currentTarget.value}))}
                                    class="w-20 text-sm border border-indigo-300 rounded px-2 py-1 focus:outline-none focus:ring-1 focus:ring-indigo-400" />
                                : r.weight}
                            </td>
                            <td class="px-4 py-3">
                              {isEditing
                                ? <input type="checkbox" checked={editVals.enabled}
                                    onChange={e => setEditVals(v => ({...v, enabled: e.currentTarget.checked}))}
                                    class="h-4 w-4 rounded accent-indigo-600" />
                                : <span class={`inline-block text-xs font-semibold px-2 py-0.5 rounded-full
                                    ${r.enabled ? 'bg-emerald-100 text-emerald-700' : 'bg-gray-100 text-gray-400'}`}>
                                    {r.enabled ? 'yes' : 'no'}
                                  </span>
                              }
                            </td>
                            <td class="px-4 py-3 text-right space-x-3">
                              {isEditing ? (
                                <>
                                  <button onClick={() => saveEdit(r.id)} disabled={saving}
                                    class="text-indigo-600 hover:text-indigo-800 font-medium text-xs disabled:opacity-50">
                                    {saving ? 'Saving…' : 'Save'}
                                  </button>
                                  <button onClick={cancelEdit}
                                    class="text-gray-400 hover:text-gray-600 font-medium text-xs">
                                    Cancel
                                  </button>
                                </>
                              ) : (
                                <>
                                  <button onClick={() => startEdit(r)}
                                    class="text-indigo-600 hover:text-indigo-800 font-medium text-xs">
                                    Edit
                                  </button>
                                  <button onClick={() => handleDelete(r.id)}
                                    class="text-rose-500 hover:text-rose-700 font-medium text-xs">
                                    Delete
                                  </button>
                                </>
                              )}
                            </td>
                          </tr>
                        )
                      })}
                    </tbody>
                  )
                })
              })()}
            </table>
          </div>
        )}
    </div>
  )
}

const inputCls = 'w-full text-sm border border-gray-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-300'

function Field({ label, children }) {
  return (
    <label class="flex flex-col gap-1">
      <span class="text-xs font-medium text-gray-500">{label}</span>
      {children}
    </label>
  )
}
