// v2 - providers expand + virtual key limits
const _BUILD_V = 'providers-v2'
import { useState, useEffect } from 'preact/hooks'
import { Fragment } from 'preact'
import { 
  listProviders, 
  addAPIKey, 
  listVendorAPIKeys,
  deleteAPIKey,
  listVendorModels, 
  addVendorModel, 
  deleteVendorModel, 
  listModelGroups,
  addModelGroup,
  deleteModelGroup,
  getModelGroupMembers,
  setModelGroupMembers,
  getRateLimits,
  upsertRateLimit,
  deleteRateLimit 
} from '../api'
import { useAsync } from '../hooks/useAsync'
import { Spinner, Banner } from './Dashboard'

const STATUS_BADGE = {
  healthy: 'bg-emerald-100 text-emerald-700',
  jailed:  'bg-rose-100    text-rose-700',
  unknown: 'bg-gray-100    text-gray-500',
}

export function Providers() {
  const { data: providers, loading, error, refetch } = useAsync(listProviders)
  const [selectedProvider, setSelectedProvider] = useState(null)

  return (
    <div class="space-y-6">
      <div class="flex items-center justify-between">
        <h2 class="text-xl font-semibold">Providers</h2>
      </div>

      {error ? <Banner type="error">{error}</Banner>
        : loading ? <Spinner />
        : (
          <div class="rounded-xl border border-gray-200 bg-white overflow-hidden">
            <table class="w-full text-sm">
              <thead>
                <tr class="border-b border-gray-100 bg-gray-50">
                  <th class="text-left px-4 py-3 font-medium text-gray-500">Name</th>
                  <th class="text-left px-4 py-3 font-medium text-gray-500">Base URL</th>
                  <th class="text-left px-4 py-3 font-medium text-gray-500">API Keys</th>
                  <th class="text-left px-4 py-3 font-medium text-gray-500">Status</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-100">
                {(providers ?? []).length === 0 ? (
                  <tr><td colspan="4" class="px-4 py-8 text-center text-gray-400">No providers configured.</td></tr>
                ) : (providers ?? []).map(p => (
                  <Fragment key={p.id}>
                    <tr 
                      class={`hover:bg-gray-50 transition-colors cursor-pointer ${selectedProvider?.id === p.id ? 'bg-indigo-50' : ''}`}
                      onClick={() => setSelectedProvider(selectedProvider?.id === p.id ? null : p)}
                    >
                      <td class="px-4 py-3 font-medium text-indigo-600">{p.name} {selectedProvider?.id === p.id ? '▼' : '▶'}</td>
                      <td class="px-4 py-3 text-gray-500 font-mono text-xs">{p.base_url}</td>
                      <td class="px-4 py-3 text-gray-500">{p.api_key_count}</td>
                      <td class="px-4 py-3">
                        <span class={`inline-block text-xs font-semibold px-2 py-0.5 rounded-full ${p.enabled ? STATUS_BADGE.healthy : STATUS_BADGE.unknown}`}>
                          {p.enabled ? 'enabled' : 'disabled'}
                        </span>
                      </td>
                    </tr>
                    {selectedProvider?.id === p.id && (
                      <tr>
                        <td colspan="4" class="p-0 border-b border-gray-200">
                           <ProviderDetails provider={p} />
                        </td>
                      </tr>
                    )}
                  </Fragment>
                ))}
              </tbody>
            </table>
          </div>
        )}
    </div>
  )
}

function ProviderDetails({ provider }) {
  const [tab, setTab] = useState('keys')

  const tabs = [
    { id: 'keys', name: 'API Keys' },
    { id: 'models', name: 'Models' },
    { id: 'groups', name: 'Model Groups' },
    { id: 'limits', name: 'Global Limits' },
  ]

  const getLimitRuleInfo = (name) => {
    switch (name.toLowerCase()) {
      case 'nim': return 'Limits are typically set per API Key (shared across all models).'
      case 'mistral': return 'Limits are typically set per Model Group.'
      default: return 'Configure limits globally, per model, per group, or per API key.'
    }
  }

  return (
    <div class="bg-gray-50 p-6 shadow-inner border-y border-gray-200">
      <div class="mb-4 flex items-center justify-between">
        <div class="text-sm text-gray-600 bg-blue-50 border border-blue-200 px-3 py-1.5 rounded-md">
          <span class="font-medium text-blue-800">Note:</span> {getLimitRuleInfo(provider.name)}
        </div>
      </div>
      <div class="flex space-x-4 border-b border-gray-300 mb-6">
        {tabs.map(t => (
          <button
            key={t.id}
            class={`py-2 px-1 border-b-2 font-medium text-sm ${
              tab === t.id ? 'border-indigo-500 text-indigo-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
            onClick={() => setTab(t.id)}
          >
            {t.name}
          </button>
        ))}
      </div>

      <div class="bg-white rounded-lg p-5 border border-gray-200 shadow-sm">
        {tab === 'keys' && <TabKeys provider={provider} />}
        {tab === 'models' && <TabModels provider={provider} />}
        {tab === 'groups' && <TabGroups provider={provider} />}
        {tab === 'limits' && <TabLimits entityType="vendor" entityId={provider.id.toString()} title={`Global Limits for ${provider.name}`} />}
      </div>
    </div>
  )
}

// ---------------------------------------------------------------------------
// Tabs
// ---------------------------------------------------------------------------

function TabKeys({ provider }) {
  const { data: keys, loading, refetch } = useAsync(() => listVendorAPIKeys(provider.id))
  const [showForm, setShowForm] = useState(false)
  const [formLabel, setFormLabel] = useState('')
  const [formKey, setFormKey] = useState('')
  const [formHint, setFormHint] = useState('')
  const [saving, setSaving] = useState(false)
  const [saveErr, setSaveErr] = useState(null)
  const [limitsKey, setLimitsKey] = useState(null)
  const [limitsVersion, setLimitsVersion] = useState(0)
  
  async function handleAddKey(e) {
    e.preventDefault()
    setSaving(true)
    setSaveErr(null)
    try {
      await addAPIKey(provider.name, {
        label: formLabel,
        encrypted_key: formKey,
        key_hint: formHint,
      })
      setFormLabel('')
      setFormKey('')
      setFormHint('')
      setShowForm(false)
      refetch()
    } catch (err) {
      setSaveErr(err.message)
    } finally {
      setSaving(false)
    }
  }

  return (
    <div>
      <div class="flex justify-between mb-4">
        <h3 class="font-medium">API Keys</h3>
        <button onClick={() => setShowForm(!showForm)} class="text-xs bg-indigo-600 text-white px-3 py-1.5 rounded hover:bg-indigo-700">
          + Add Key
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleAddKey} class="bg-gray-50 p-4 rounded-md border border-gray-200 mb-4 space-y-4">
           {saveErr && <Banner type="error">{saveErr}</Banner>}
           <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
             <Field label="Label">
               <input type="text" value={formLabel} onInput={e => setFormLabel(e.currentTarget.value)} required class={inputCls} />
             </Field>
             <Field label="Ciphertext">
               <input type="text" value={formKey} onInput={e => setFormKey(e.currentTarget.value)} required class={inputCls} />
             </Field>
             <Field label="Hint (4 chars)">
               <input type="text" value={formHint} onInput={e => setFormHint(e.currentTarget.value)} maxLength={4} class={inputCls} />
             </Field>
           </div>
           <button type="submit" disabled={saving} class="bg-indigo-600 text-white text-xs px-4 py-2 rounded">
             {saving ? 'Saving...' : 'Save Key'}
           </button>
        </form>
      )}

      {loading ? <Spinner /> : (
        <table class="w-full text-sm">
          <thead><tr class="bg-gray-50"><th class="text-left px-2 py-2">Label</th><th class="text-left px-2 py-2">Hint</th><th class="text-left px-2 py-2">Limits</th><th class="px-2 py-2"></th></tr></thead>
          <tbody>
            {(keys || []).map(k => (
              <tr key={k.id} class="border-t border-gray-100">
                <td class="px-2 py-2 font-medium text-gray-700">{k.label}</td>
                <td class="px-2 py-2 font-mono text-gray-500 text-xs">...{k.key_hint}</td>
                <td class="px-2 py-2">
                  <InlineLimits entityType="api_key" entityId={k.id.toString()} version={limitsVersion} />
                </td>
                <td class="px-2 py-2 text-right">
                  <button onClick={() => setLimitsKey(k)} class="text-indigo-600 text-xs hover:underline mr-4">Limits</button>
                  <button onClick={async () => {
                    if (confirm('Delete API key?')) {
                      await deleteAPIKey(k.id)
                      refetch()
                    }
                  }} class="text-red-500 text-xs hover:underline">Delete</button>
                </td>
              </tr>
            ))}
            {(!keys || keys.length === 0) && <tr><td colspan="4" class="text-center p-4 text-gray-500">No API keys added yet.</td></tr>}
          </tbody>
        </table>
      )}

      {limitsKey && (
        <Modal onClose={() => setLimitsKey(null)}>
          <TabLimits entityType="api_key" entityId={limitsKey.id.toString()} title={`Limits for Key ${limitsKey.label}`} onClose={() => { setLimitsKey(null); setLimitsVersion(v => v + 1) }} />
        </Modal>
      )}
    </div>
  )
}

function TabModels({ provider }) {
  const { data: models, loading, refetch } = useAsync(() => listVendorModels(provider.id))
  const [name, setName] = useState('')
  const [search, setSearch] = useState('')
  const [saving, setSaving] = useState(false)
  const [limitsModel, setLimitsModel] = useState(null)
  const [limitsVersion, setLimitsVersion] = useState(0)

  async function handleAdd(e) {
    e.preventDefault()
    if (!name.trim()) return
    setSaving(true)
    try {
      await addVendorModel(provider.id, { name })
      setName('')
      refetch()
    } catch(err) {
      alert(err.message)
    } finally {
      setSaving(false)
    }
  }

  const filtered = (models || []).filter(m =>
    !search || m.name.toLowerCase().includes(search.toLowerCase())
  )

  return (
    <div>
      <div class="flex items-center justify-between mb-4">
        <h3 class="font-medium">Vendor Models <span class="text-xs text-gray-400 font-normal">({(models||[]).length} total)</span></h3>
      </div>
      
      <form onSubmit={handleAdd} class="flex gap-2 mb-3">
        <input type="text" value={name} onInput={e => setName(e.currentTarget.value)} placeholder="Model Name (e.g. meta/llama-3.1-8b-instruct)" class={inputCls} required />
        <button type="submit" disabled={saving} class="bg-indigo-600 text-white text-sm px-4 py-2 rounded whitespace-nowrap">Add Model</button>
      </form>

      <input
        type="text"
        value={search}
        onInput={e => setSearch(e.currentTarget.value)}
        placeholder="🔍 Search models..."
        class={inputCls + " mb-4"}
      />

      {loading ? <Spinner /> : (
        <table class="w-full text-sm">
          <thead><tr class="bg-gray-50"><th class="text-left px-2 py-2">Name</th><th class="text-left px-2 py-2">Limits</th><th class="px-2 py-2"></th></tr></thead>
          <tbody>
            {filtered.map(m => (
              <tr key={m.id} class="border-t border-gray-100">
                <td class="px-2 py-2 font-mono text-gray-700 text-xs">{m.name}</td>
                <td class="px-2 py-2">
                  <InlineLimits entityType="api_key_model" entityId={m.id.toString()} version={limitsVersion} />
                </td>
                <td class="px-2 py-2 text-right">
                  <button onClick={() => setLimitsModel(m)} class="text-indigo-600 text-xs hover:underline mr-4">Limits</button>
                  <button onClick={async () => {
                    if (confirm('Delete model?')) {
                      await deleteVendorModel(m.id)
                      refetch()
                    }
                  }} class="text-red-500 text-xs hover:underline">Delete</button>
                </td>
              </tr>
            ))}
            {filtered.length === 0 && search && <tr><td colspan="3" class="text-center p-4 text-gray-500">No models match "{search}".</td></tr>}
            {(!models || models.length === 0) && !search && <tr><td colspan="3" class="text-center p-4 text-gray-500">No models added yet.</td></tr>}
          </tbody>
        </table>
      )}

      {limitsModel && (
        <Modal onClose={() => setLimitsModel(null)}>
          <TabLimits entityType="api_key_model" entityId={limitsModel.id.toString()} title={`Limits for ${limitsModel.name}`} onClose={() => { setLimitsModel(null); setLimitsVersion(v => v + 1) }} />
        </Modal>
      )}
    </div>
  )
}

function TabGroups({ provider }) {
  const { data: groups, loading, refetch } = useAsync(() => listModelGroups(provider.id))
  const [name, setName] = useState('')
  const [saving, setSaving] = useState(false)
  const [limitsGroup, setLimitsGroup] = useState(null)

  async function handleAdd(e) {
    e.preventDefault()
    if (!name.trim()) return
    setSaving(true)
    try {
      await addModelGroup(provider.id, { name })
      setName('')
      refetch()
    } catch(err) {
      alert(err.message)
    } finally {
      setSaving(false)
    }
  }

  return (
    <div>
      <h3 class="font-medium mb-4">Model Groups</h3>
      
      <form onSubmit={handleAdd} class="flex gap-2 mb-6">
        <input type="text" value={name} onInput={e => setName(e.currentTarget.value)} placeholder="Group Name (e.g. mistral-shared)" class={inputCls} required />
        <button type="submit" disabled={saving} class="bg-indigo-600 text-white text-sm px-4 py-2 rounded whitespace-nowrap">Add Group</button>
      </form>

      {loading ? <Spinner /> : (
        <table class="w-full text-sm">
          <thead><tr class="bg-gray-50"><th class="text-left px-2 py-2">Group Name</th><th class="text-left px-2 py-2">Limits</th><th class="px-2 py-2"></th></tr></thead>
          <tbody>
            {(groups || []).map(g => (
              <tr key={g.id} class="border-t border-gray-100">
                <td class="px-2 py-2 font-medium">{g.name}</td>
                <td class="px-2 py-2">
                  <InlineLimits entityType="api_key_model_group" entityId={g.id.toString()} />
                </td>
                <td class="px-2 py-2 text-right">
                  <button onClick={() => setLimitsGroup(g)} class="text-indigo-600 text-xs hover:underline mr-4">Limits</button>
                  <button onClick={async () => {
                    if (confirm('Delete group?')) {
                      await deleteModelGroup(g.id)
                      refetch()
                    }
                  }} class="text-red-500 text-xs hover:underline">Delete</button>
                </td>
              </tr>
            ))}
            {(!groups || groups.length === 0) && <tr><td colspan="3" class="text-center p-4 text-gray-500">No groups added yet.</td></tr>}
          </tbody>
        </table>
      )}

      {limitsGroup && (
        <Modal onClose={() => setLimitsGroup(null)}>
          <TabLimits entityType="api_key_model_group" entityId={limitsGroup.id.toString()} title={`Limits for Group ${limitsGroup.name}`} onClose={() => { setLimitsGroup(null); refetch() }} />
        </Modal>
      )}
    </div>
  )
}

function Modal({ children, onClose }) {
  return (
    <div class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50 flex items-center justify-center">
      <div class="relative p-8 border w-full max-w-2xl shadow-lg rounded-md bg-white">
        <button onClick={onClose} class="absolute top-4 right-4 text-gray-400 hover:text-gray-600">✕</button>
        {children}
      </div>
    </div>
  )
}


function InlineLimits({ entityType, entityId, version = 0 }) {
  const { data: limits, loading } = useAsync(
    () => getRateLimits(entityType, entityId),
    [entityType, entityId, version]
  )
  
  if (loading) return <span class="text-xs text-gray-400">Loading...</span>
  if (!limits || limits.length === 0) return <span class="text-xs text-gray-400 italic">No limits</span>

  return (
    <div class="flex flex-wrap gap-1">
      {limits.map(l => (
        <span key={l.id} class="text-xs bg-indigo-50 border border-indigo-200 px-2 py-0.5 rounded text-indigo-700 font-medium">
          {l.limit_type === 'requests' ? 'RPM' : 'TPM'}: {l.max_value.toLocaleString()}/{l.window_size}
        </span>
      ))}
    </div>
  )
}

function TabLimits({ entityType, entityId, title, onClose }) {
  const { data: limits, loading, refetch } = useAsync(() => getRateLimits(entityType, entityId))
  const [windowSize, setWindowSize] = useState('minute')
  
  const [reqUnlimited, setReqUnlimited] = useState(true)
  const [reqValue, setReqValue] = useState(100)
  
  const [tokUnlimited, setTokUnlimited] = useState(true)
  const [tokValue, setTokValue] = useState(1000)
  
  const [saving, setSaving] = useState(false)

  // Initialize form from data
  useEffect(() => {
    if (!limits) return
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

  async function handleUpsert(e) {
    e.preventDefault()
    setSaving(true)
    try {
      if (reqUnlimited) {
        await deleteRateLimit(entityType, entityId, 'requests', windowSize).catch(() => {})
      } else {
        await upsertRateLimit(entityType, entityId, {
          limit_type: 'requests',
          window_size: windowSize,
          max_value: Number(reqValue)
        })
      }
      
      if (tokUnlimited) {
        await deleteRateLimit(entityType, entityId, 'tokens', windowSize).catch(() => {})
      } else {
        await upsertRateLimit(entityType, entityId, {
          limit_type: 'tokens',
          window_size: windowSize,
          max_value: Number(tokValue)
        })
      }
      
      refetch()
    } catch(err) {
      alert(err.message)
    } finally {
      setSaving(false)
    }
  }

  return (
    <div>
      <div class="flex justify-between items-center mb-4">
        <h3 class="font-medium">{title}</h3>
        {onClose && <button onClick={onClose} class="text-gray-400 hover:text-gray-600 text-lg">✕</button>}
      </div>
      <form onSubmit={handleUpsert} class="flex flex-col gap-4 bg-gray-50 p-4 rounded border border-gray-200 mb-6">
        <div class="flex items-center gap-4">
          <Field label="Window">
            <select value={windowSize} onChange={e => setWindowSize(e.currentTarget.value)} class={inputCls + " w-48"}>
              <option value="second">Per Second</option>
              <option value="minute">Per Minute</option>
              <option value="hour">Per Hour</option>
              <option value="day">Per Day</option>
            </select>
          </Field>
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
              <input type="number" min="1" value={reqValue} onInput={e => setReqValue(e.currentTarget.value)} class={inputCls} required />
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
              <input type="number" min="1" value={tokValue} onInput={e => setTokValue(e.currentTarget.value)} class={inputCls} required />
            )}
          </div>
        </div>

        <div class="flex justify-end mt-2">
          <button type="submit" disabled={saving} class="bg-indigo-600 text-white text-sm px-6 py-2 rounded">
            {saving ? 'Saving...' : 'Apply Limits'}
          </button>
        </div>
      </form>

      <h4 class="text-sm font-medium text-gray-600 mb-2">Current Limits</h4>
      {loading ? <Spinner /> : (
        <table class="w-full text-sm border border-gray-200 rounded overflow-hidden">
          <thead><tr class="bg-gray-100"><th class="text-left px-3 py-2">Type</th><th class="text-left px-3 py-2">Window</th><th class="text-left px-3 py-2">Max Value</th><th></th></tr></thead>
          <tbody>
            {(limits || []).map(l => (
              <tr key={l.id} class="border-t border-gray-100">
                <td class="px-3 py-2 capitalize">{l.limit_type}</td>
                <td class="px-3 py-2 capitalize">Per {l.window_size}</td>
                <td class="px-3 py-2 font-mono">{l.max_value.toLocaleString()}</td>
                <td class="px-3 py-2 text-right">
                  <button onClick={async () => {
                    if (confirm('Delete limit?')) {
                      await deleteRateLimit(entityType, entityId, l.limit_type, l.window_size)
                      refetch()
                    }
                  }} class="text-red-500 text-xs hover:underline">Remove</button>
                </td>
              </tr>
            ))}
            {(!limits || limits.length === 0) && <tr><td colspan="4" class="text-center p-4 text-gray-500">No limits configured.</td></tr>}
          </tbody>
        </table>
      )}
    </div>
  )
}

const inputCls = 'w-full text-sm border border-gray-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-300'

function Field({ label, children }) {
  return (
    <label class="flex flex-col gap-1 w-full">
      <span class="text-xs font-medium text-gray-500">{label}</span>
      {children}
    </label>
  )
}
