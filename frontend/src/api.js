/**
 * api.js — typed fetch wrappers for /admin/api/v1/...
 *
 * All functions return a Promise that resolves to the parsed JSON body, or
 * throws an Error with `.message` set to the server's "error" field (or the
 * HTTP status text on non-JSON errors).
 */

const BASE = '/admin/api/v1'

async function request(method, path, body) {
  const opts = {
    method,
    headers: { 'Content-Type': 'application/json' },
  }
  if (body !== undefined) opts.body = JSON.stringify(body)

  const res = await fetch(BASE + path, opts)
  const text = await res.text()
  let json
  try { json = JSON.parse(text) } catch { json = null }

  if (!res.ok) {
    const msg = json?.error ?? `${res.status} ${res.statusText}`
    throw new Error(msg)
  }
  return json
}

// Providers
export const listProviders    = ()           => request('GET',  '/providers')
export const addAPIKey        = (vendor, payload) =>
  request('POST', `/providers/${encodeURIComponent(vendor)}/keys`, payload)
export const listVendorAPIKeys = (vId)       => request('GET',    `/providers/${vId}/keys`)
export const deleteAPIKey     = (id)         => request('DELETE', `/keys/${id}`)

// Virtual models
export const listVirtualModels = () => request('GET', '/virtual-models')

// Routing rules
export const listRoutingRules  = ()         => request('GET',    '/routing-rules')
export const createRoutingRule = (payload)  => request('POST',   '/routing-rules', payload)
export const updateRoutingRule = (id, patch)=> request('PUT',    `/routing-rules/${id}`, patch)
export const deleteRoutingRule = (id)       => request('DELETE', `/routing-rules/${id}`)
export const syncIndividualModels = ()      => request('POST',   '/routing-rules/sync-individual')

// Jails
export const listJails = () => request('GET', '/jails')

// Metrics summary
export const getMetricsSummary = () => request('GET', '/metrics-summary')

// Logs
export const getLogs = () => request('GET', '/logs')

// Virtual keys
export const listVirtualKeys   = ()         => request('GET',    '/virtual-keys')
export const createVirtualKey  = (payload)  => request('POST',   '/virtual-keys', payload)
export const deleteVirtualKey  = (id)       => request('DELETE', `/virtual-keys/${id}`)

// Vendor Models & Groups
export const listVendorModels     = (vId)   => request('GET',    `/providers/${vId}/models`)
export const addVendorModel       = (vId, p)=> request('POST',   `/providers/${vId}/models`, p)
export const deleteVendorModel    = (id)    => request('DELETE', `/models/${id}`)
export const listModelGroups      = (vId)   => request('GET',    `/providers/${vId}/model-groups`)
export const addModelGroup        = (vId, p)=> request('POST',   `/providers/${vId}/model-groups`, p)
export const deleteModelGroup     = (id)    => request('DELETE', `/model-groups/${id}`)
export const getModelGroupMembers = (id)    => request('GET',    `/model-groups/${id}/members`)
export const setModelGroupMembers = (id, p) => request('POST',   `/model-groups/${id}/members`, p)

// Rate Limits
export const getRateLimits    = (type, id)             => request('GET',    `/limits/${type}/${id}`)
export const upsertRateLimit  = (type, id, payload)    => request('PUT',    `/limits/${type}/${id}`, payload)
export const deleteRateLimit  = (type, id, limitT, ws) => request('DELETE', `/limits/${type}/${id}/${limitT}/${ws}`)
