import { useState, useEffect } from 'preact/hooks'
import { listVirtualKeys, createVirtualKey, deleteVirtualKey, listVirtualModels, upsertRateLimit, getRateLimits, deleteRateLimit } from '../api'

export function VirtualKeys() {
  const [keys, setKeys] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  // Form state
  const [projectName, setProjectName] = useState('')
  const [allowedModels, setAllowedModels] = useState('*')
  const [creating, setCreating] = useState(false)
  
  // Rate limit fields in create form
  const [rpmLimit, setRpmLimit] = useState('')
  const [tpmLimit, setTpmLimit] = useState('')
  const [budget, setBudget] = useState('')
  const [enableWebSearch, setEnableWebSearch] = useState(false)

  // Modal for new key
  const [newKeyData, setNewKeyData] = useState(null)
  const [visibleKeys, setVisibleKeys] = useState(new Set())

  // Limits modal for existing keys
  const [limitsKey, setLimitsKey] = useState(null)

  // Virtual models dropdown
  const [vms, setVms] = useState([])
  const [showDropdown, setShowDropdown] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')

  useEffect(() => {
    loadKeys()
  }, [])

  async function loadKeys() {
    try {
      setLoading(true)
      const [keysData, vmsData] = await Promise.all([
        listVirtualKeys(),
        listVirtualModels()
      ])
      setKeys(keysData || [])
      setVms(vmsData || [])
      setError(null)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  async function handleCreate(e) {
    e.preventDefault()
    if (!projectName.trim()) return

    try {
      setCreating(true)
      const res = await createVirtualKey({
        project_name: projectName,
        allowed_models: allowedModels || '*',
        budget: budget ? parseFloat(budget) : null,
        rpm_limit: rpmLimit ? parseInt(rpmLimit, 10) : null,
        enable_web_search: enableWebSearch
      })
      // Apply rate limits if provided
      const keyId = res.id?.toString()
      if (keyId) {
        if (rpmLimit) await upsertRateLimit('virtual_key', keyId, { limit_type: 'requests', window_size: 'minute', max_value: Number(rpmLimit) })
        if (tpmLimit) await upsertRateLimit('virtual_key', keyId, { limit_type: 'tokens', window_size: 'minute', max_value: Number(tpmLimit) })
      }
      setNewKeyData(res)
      setProjectName('')
      setAllowedModels('*')
      setRpmLimit('')
      setTpmLimit('')
      setBudget('')
      setEnableWebSearch(false)
      await loadKeys()
    } catch (err) {
      alert('Failed to create key: ' + err.message)
    } finally {
      setCreating(false)
    }
  }

  async function handleDelete(id) {
    if (!confirm('Are you sure you want to delete this virtual key?')) return
    try {
      await deleteVirtualKey(id)
      await loadKeys()
    } catch (err) {
      alert('Failed to delete key: ' + err.message)
    }
  }

  if (loading) {
    return <div class="text-gray-500 animate-pulse">Loading virtual keys...</div>
  }

  return (
    <div class="space-y-6">
      <div class="flex items-center justify-between">
        <h2 class="text-lg font-medium text-gray-900">Virtual Keys</h2>
      </div>

      {error && (
        <div class="p-4 bg-red-50 text-red-700 rounded-md text-sm border border-red-200">
          {error}
        </div>
      )}

      {newKeyData && (
        <div class="bg-green-50 border border-green-200 p-6 rounded-lg relative">
          <button 
            onClick={() => setNewKeyData(null)}
            class="absolute top-4 right-4 text-green-700 hover:text-green-900"
          >
            &times;
          </button>
          <h3 class="text-green-900 font-medium mb-2">Key Created Successfully!</h3>
          <p class="text-green-800 text-sm mb-4">
            Please copy this key now. You will not be able to see it again.
          </p>
          <div class="bg-white p-3 rounded border border-green-300 font-mono text-sm text-gray-800 break-all">
            {newKeyData.api_key}
          </div>
        </div>
      )}

      <div class="bg-white rounded-xl shadow-sm border border-gray-200">
        <div class="p-5 border-b border-gray-200 bg-gray-50 rounded-t-xl">
          <h3 class="text-sm font-medium text-gray-900 mb-4">Create New Virtual Key</h3>
          <form onSubmit={handleCreate} class="space-y-4">
            <div class="flex gap-4 items-end">
              <div class="flex-1">
                <label class="block text-xs font-medium text-gray-700 mb-1">Project Name</label>
                <input
                  type="text"
                  class="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm px-3 py-2 border"
                  placeholder="e.g. My Awesome App"
                  value={projectName}
                  onInput={(e) => setProjectName(e.target.value)}
                  required
                />
              </div>
              <div class="flex-1 relative z-20">
                <label class="block text-xs font-medium text-gray-700 mb-1">Allowed Models (comma separated, or * for all)</label>
                <div class="flex">
                  <input
                    type="text"
                    class="block w-full rounded-l-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm px-3 py-2 border"
                    placeholder="*"
                    value={allowedModels}
                    onInput={(e) => setAllowedModels(e.target.value)}
                  />
                  <button
                    type="button"
                    onClick={() => setShowDropdown(!showDropdown)}
                    class="inline-flex items-center px-3 py-2 border border-l-0 border-gray-300 rounded-r-md bg-gray-50 text-gray-500 hover:bg-gray-100 text-sm"
                  >
                    Add Model ▼
                  </button>
                </div>

                {showDropdown && (
                  <div class="absolute z-10 mt-1 w-full bg-white shadow-lg max-h-60 rounded-md py-1 text-base ring-1 ring-black ring-opacity-5 overflow-auto focus:outline-none sm:text-sm">
                    <div class="px-2 pb-2 pt-1 sticky top-0 bg-white border-b border-gray-100">
                      <input
                        type="text"
                        class="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm px-2 py-1.5 border"
                        placeholder="Search models..."
                        value={searchQuery}
                        onInput={(e) => setSearchQuery(e.target.value)}
                      />
                    </div>
                    {vms.filter(vm => vm.name.toLowerCase().includes(searchQuery.toLowerCase())).map((vm) => (
                      <div
                        key={vm.name}
                        class="cursor-pointer select-none relative py-2 pl-3 pr-9 hover:bg-indigo-50 text-gray-900"
                        onClick={() => {
                          if (allowedModels === '*') {
                            setAllowedModels(vm.name)
                          } else {
                            const current = allowedModels.split(',').map(s => s.trim()).filter(Boolean)
                            if (!current.includes(vm.name)) {
                              setAllowedModels([...current, vm.name].join(', '))
                            }
                          }
                          setShowDropdown(false)
                          setSearchQuery('')
                        }}
                      >
                        <span class="block truncate font-mono text-xs">{vm.name}</span>
                      </div>
                    ))}
                    {vms.filter(vm => vm.name.toLowerCase().includes(searchQuery.toLowerCase())).length === 0 && (
                      <div class="py-2 px-3 text-gray-500 text-sm text-center">No models found.</div>
                    )}
                  </div>
                )}
              </div>
            </div>

            {/* Rate limits */}
            <div class="flex gap-4 items-end">
              <div class="w-40">
                <label class="block text-xs font-medium text-gray-700 mb-1">RPM Limit <span class="text-gray-400">(optional)</span></label>
                <input
                  type="number"
                  min="0"
                  class="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm px-3 py-2 border"
                  placeholder="e.g. 100"
                  value={rpmLimit}
                  onInput={(e) => setRpmLimit(e.target.value)}
                />
              </div>
              <div class="w-40">
                <label class="block text-xs font-medium text-gray-700 mb-1">TPM Limit <span class="text-gray-400">(optional)</span></label>
                <input
                  type="number"
                  min="0"
                  class="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm px-3 py-2 border"
                  placeholder="e.g. 50000"
                  value={tpmLimit}
                  onInput={(e) => setTpmLimit(e.target.value)}
                />
              </div>
              <div class="w-40">
                <label class="block text-xs font-medium text-gray-700 mb-1">Budget ($) <span class="text-gray-400">(optional)</span></label>
                <input
                  type="number"
                  step="0.01"
                  min="0"
                  class="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm px-3 py-2 border"
                  placeholder="e.g. 50.00"
                  value={budget}
                  onInput={(e) => setBudget(e.target.value)}
                />
              </div>
              <div class="flex items-center mb-2 px-2">
                <input
                  id="enable-web-search"
                  type="checkbox"
                  class="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
                  checked={enableWebSearch}
                  onChange={(e) => setEnableWebSearch(e.target.checked)}
                />
                <label for="enable-web-search" class="ml-2 block text-sm text-gray-900">
                  Enable Web Search
                </label>
              </div>
              <button
                type="submit"
                disabled={creating || !projectName.trim()}
                class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
              >
                {creating ? 'Creating...' : 'Create Key'}
              </button>
            </div>
          </form>
        </div>

        <div class="overflow-x-auto overflow-y-hidden rounded-b-xl">
          {keys.length === 0 ? (
            <div class="p-6 text-center text-sm text-gray-500">
              No virtual keys found. Create one above to get started.
            </div>
          ) : (
            <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Project</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Key</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Allowed Models</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Budget</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Spend</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Web Search</th>
                <th class="relative px-6 py-3"><span class="sr-only">Actions</span></th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              {keys.map((k) => (
                <tr key={k.id}>
                  <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {k.project_name}
                  </td>
                  <td class="px-6 py-4 text-sm font-mono text-gray-500">
                    <div class="flex items-center gap-2">
                      <span class="truncate max-w-xs">
                        {visibleKeys.has(k.id) && k.encrypted_key ? k.encrypted_key : k.key_hint}
                      </span>
                      {k.encrypted_key && (
                        <button
                          onClick={() => {
                            if (visibleKeys.has(k.id)) {
                              navigator.clipboard.writeText(k.encrypted_key)
                              alert('Copied to clipboard!')
                            } else {
                              const newSet = new Set(visibleKeys)
                              newSet.add(k.id)
                              setVisibleKeys(newSet)
                            }
                          }}
                          class="text-xs bg-gray-100 hover:bg-gray-200 text-gray-700 px-2 py-1 rounded border border-gray-300 flex-shrink-0"
                        >
                          {visibleKeys.has(k.id) ? 'Copy' : 'Show'}
                        </button>
                      )}
                    </div>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                      {k.allowed_models}
                    </span>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {k.budget !== null && k.budget !== undefined ? `$${k.budget}` : 'Unlimited'}
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    ${k.spend || 0}
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {k.enable_web_search ? <span class="text-green-600 font-medium">Enabled</span> : <span class="text-gray-400">Disabled</span>}
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium space-x-3">
                    <button
                      onClick={() => setLimitsKey(k)}
                      class="text-indigo-600 hover:text-indigo-900"
                    >
                      Limits
                    </button>
                    <button
                      onClick={() => handleDelete(k.id)}
                      class="text-red-600 hover:text-red-900"
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
        </div>
      </div>

      {/* Key-level limits modal */}
      {limitsKey && (
        <KeyLimitsModal keyData={limitsKey} onClose={() => setLimitsKey(null)} />
      )}
    </div>
  )
}

function KeyLimitsModal({ keyData, onClose }) {
  const [limits, setLimits] = useState([])
  const [loading, setLoading] = useState(true)
  const [windowSize, setWindowSize] = useState('minute')
  
  const [reqUnlimited, setReqUnlimited] = useState(true)
  const [reqValue, setReqValue] = useState(100)
  
  const [tokUnlimited, setTokUnlimited] = useState(true)
  const [tokValue, setTokValue] = useState(1000)
  const [saving, setSaving] = useState(false)

  const entityId = keyData.id.toString()

  useEffect(() => { loadLimits() }, [keyData])

  useEffect(() => {
    if (!limits || limits.length === 0) return
    const reqLim = limits.find(l => l.limit_type === 'requests')
    if (reqLim) {
      setReqUnlimited(false)
      setReqValue(reqLim.max_value)
      setWindowSize(reqLim.window_size)
    }
    const tokLim = limits.find(l => l.limit_type === 'tokens')
    if (tokLim) {
      setTokUnlimited(false)
      setTokValue(tokLim.max_value)
      setWindowSize(tokLim.window_size)
    }
  }, [limits])

  async function loadLimits() {
    setLoading(true)
    try {
      const data = await getRateLimits('virtual_key', entityId)
      setLimits(data || [])
    } finally {
      setLoading(false)
    }
  }

  async function handleSet(e) {
    e.preventDefault()
    setSaving(true)
    try {
      if (reqUnlimited) {
        await deleteRateLimit('virtual_key', entityId, 'requests', windowSize).catch(() => {})
      } else {
        await upsertRateLimit('virtual_key', entityId, { limit_type: 'requests', window_size: windowSize, max_value: Number(reqValue) })
      }
      
      if (tokUnlimited) {
        await deleteRateLimit('virtual_key', entityId, 'tokens', windowSize).catch(() => {})
      } else {
        await upsertRateLimit('virtual_key', entityId, { limit_type: 'tokens', window_size: windowSize, max_value: Number(tokValue) })
      }
      await loadLimits()
    } catch(err) { alert(err.message) }
    finally { setSaving(false) }
  }

  async function handleDelete(limit) {
    if (!confirm('Remove this limit?')) return
    await deleteRateLimit('virtual_key', entityId, limit.limit_type, limit.window_size)
    await loadLimits()
  }

  return (
    <div class="fixed inset-0 bg-gray-600 bg-opacity-50 z-50 flex items-center justify-center">
      <div class="relative bg-white rounded-xl shadow-xl w-full max-w-lg p-6">
        <button onClick={onClose} class="absolute top-4 right-4 text-gray-400 hover:text-gray-600 text-lg">✕</button>
        <h3 class="font-semibold text-gray-800 mb-1">Rate Limits</h3>
        <p class="text-xs text-gray-500 mb-4">Key: {keyData.project_name} — {keyData.key_hint}</p>

        <form onSubmit={handleSet} class="flex flex-col gap-4 bg-gray-50 p-4 rounded border border-gray-200 mb-4">
          <div class="flex items-center gap-4">
            <label class="flex flex-col gap-1 text-xs font-medium text-gray-500 w-48">
              Window
              <select value={windowSize} onChange={e => setWindowSize(e.currentTarget.value)} class="text-sm border border-gray-200 rounded-md px-2 py-1.5 focus:outline-none">
                <option value="second">Per Second</option>
                <option value="minute">Per Minute</option>
                <option value="hour">Per Hour</option>
                <option value="day">Per Day</option>
                <option value="week">Per Week</option>
                <option value="month">Per Month</option>
              </select>
            </label>
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-2 gap-6 p-4 bg-white border border-gray-200 rounded">
            <div class="space-y-2">
              <div class="flex items-center justify-between">
                <span class="text-sm font-medium">Requests Limit</span>
                <label class="flex items-center gap-1 text-xs text-gray-600">
                  <input type="checkbox" checked={reqUnlimited} onChange={e => setReqUnlimited(e.currentTarget.checked)} />
                  Unlimited
                </label>
              </div>
              {!reqUnlimited && (
                <input type="number" min="1" value={reqValue} onInput={e => setReqValue(e.currentTarget.value)} class="w-full text-sm border border-gray-200 rounded-md px-3 py-2 focus:outline-none" required />
              )}
            </div>
            
            <div class="space-y-2">
              <div class="flex items-center justify-between">
                <span class="text-sm font-medium">Tokens Limit</span>
                <label class="flex items-center gap-1 text-xs text-gray-600">
                  <input type="checkbox" checked={tokUnlimited} onChange={e => setTokUnlimited(e.currentTarget.checked)} />
                  Unlimited
                </label>
              </div>
              {!tokUnlimited && (
                <input type="number" min="1" value={tokValue} onInput={e => setTokValue(e.currentTarget.value)} class="w-full text-sm border border-gray-200 rounded-md px-3 py-2 focus:outline-none" required />
              )}
            </div>
          </div>

          <div class="flex justify-end mt-2">
            <button type="submit" disabled={saving} class="bg-indigo-600 text-white text-sm px-6 py-2 rounded">
              {saving ? 'Saving...' : 'Apply Limits'}
            </button>
          </div>
        </form>

        {loading ? <div class="text-center text-gray-400 py-4">Loading...</div> : (
          <table class="w-full text-sm border border-gray-200 rounded overflow-hidden">
            <thead><tr class="bg-gray-50"><th class="text-left px-3 py-2 text-xs text-gray-500">Type</th><th class="text-left px-3 py-2 text-xs text-gray-500">Window</th><th class="text-left px-3 py-2 text-xs text-gray-500">Max</th><th></th></tr></thead>
            <tbody>
              {limits.map(l => (
                <tr key={l.id} class="border-t border-gray-100">
                  <td class="px-3 py-2 capitalize">{l.limit_type}</td>
                  <td class="px-3 py-2 capitalize">/{l.window_size}</td>
                  <td class="px-3 py-2 font-mono">{l.max_value?.toLocaleString()}</td>
                  <td class="px-3 py-2 text-right"><button onClick={() => handleDelete(l)} class="text-red-500 text-xs hover:underline">Remove</button></td>
                </tr>
              ))}
              {limits.length === 0 && <tr><td colspan="4" class="text-center p-3 text-gray-400">No limits set.</td></tr>}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}

