import { navigate } from '../router'

const NAV_ITEMS = [
  {
    id:    'dashboard',
    label: 'Dashboard',
    icon:  IconDashboard,
  },
  {
    id:    'providers',
    label: 'Providers',
    icon:  IconProviders,
  },
  {
    id:    'routing',
    label: 'Routing',
    icon:  IconRouting,
  },
  {
    id:    'keys',
    label: 'Virtual Keys',
    icon:  IconKeys,
  },
  {
    id:    'logs',
    label: 'Logs',
    icon:  IconLogs,
  },
]

export function Sidebar({ active }) {
  return (
    <aside class="w-56 shrink-0 bg-white border-r border-gray-200 flex flex-col">
      {/* Brand */}
      <div class="h-14 flex items-center gap-2 px-5 border-b border-gray-200">
        <span class="text-indigo-600 font-bold text-lg tracking-tight">❤ Love AI</span>
      </div>

      {/* Nav */}
      <nav class="flex-1 py-4 px-3 space-y-0.5">
        {NAV_ITEMS.map(({ id, label, icon: Icon }) => {
          const isActive = active === id
          return (
            <button
              key={id}
              onClick={() => navigate(id)}
              class={[
                'w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors',
                isActive
                  ? 'bg-indigo-50 text-indigo-700'
                  : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900',
              ].join(' ')}
            >
              <Icon class="w-4 h-4 shrink-0" />
              {label}
            </button>
          )
        })}
      </nav>

      {/* Footer */}
      <div class="px-5 py-4 border-t border-gray-200">
        <p class="text-xs text-gray-400">v0.1.0</p>
      </div>
    </aside>
  )
}

/* ── Inline SVG icons (no external dep) ─────────────────────────────────── */

function IconDashboard(props) {
  return (
    <svg viewBox="0 0 20 20" fill="currentColor" {...props}>
      <path d="M2 10a8 8 0 1 1 16 0A8 8 0 0 1 2 10Zm8-3a1 1 0 0 0-1 1v2H7a1 1 0 1 0 0 2h2v2a1 1 0 1 0 2 0v-2h2a1 1 0 1 0 0-2h-2V8a1 1 0 0 0-1-1Z" />
    </svg>
  )
}

function IconProviders(props) {
  return (
    <svg viewBox="0 0 20 20" fill="currentColor" {...props}>
      <path
        fillRule="evenodd"
        d="M2 5a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v2a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5Zm14 1a1 1 0 1 1-2 0 1 1 0 0 1 2 0ZM2 13a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v2a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2v-2Zm14 1a1 1 0 1 1-2 0 1 1 0 0 1 2 0Z"
        clipRule="evenodd"
      />
    </svg>
  )
}

function IconRouting(props) {
  return (
    <svg viewBox="0 0 20 20" fill="currentColor" {...props}>
      <path
        fillRule="evenodd"
        d="M12.293 2.293a1 1 0 0 1 1.414 0l4 4a1 1 0 0 1 0 1.414l-4 4a1 1 0 0 1-1.414-1.414L14.586 9H3a1 1 0 1 1 0-2h11.586l-2.293-2.293a1 1 0 0 1 0-1.414Zm-4.586 8a1 1 0 0 1 0 1.414L5.414 14H17a1 1 0 1 1 0 2H5.414l2.293 2.293a1 1 0 1 1-1.414 1.414l-4-4a1 1 0 0 1 0-1.414l4-4a1 1 0 0 1 1.414 0Z"
        clipRule="evenodd"
      />
    </svg>
  )
}

function IconLogs(props) {
  return (
    <svg viewBox="0 0 20 20" fill="currentColor" {...props}>
      <path
        fillRule="evenodd"
        d="M2 5a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v10a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5Zm3 1a1 1 0 0 0 0 2h6a1 1 0 1 0 0-2H5Zm0 4a1 1 0 0 0 0 2h8a1 1 0 1 0 0-2H5Zm0 4a1 1 0 0 0 0 2h4a1 1 0 1 0 0-2H5Z"
        clipRule="evenodd"
      />
    </svg>
  )
}

function IconKeys(props) {
  return (
    <svg viewBox="0 0 20 20" fill="currentColor" {...props}>
      <path fillRule="evenodd" d="M10 2a4 4 0 00-3.446 6.032l-5.26 5.26a1 1 0 00-.294.708v2a1 1 0 001 1h2a1 1 0 001-1v-1h1a1 1 0 001-1v-1h1a1 1 0 00.707-.293l1.83-1.83A4 4 0 1010 2zm1 3a1 1 0 100 2 1 1 0 000-2z" clipRule="evenodd" />
    </svg>
  )
}
