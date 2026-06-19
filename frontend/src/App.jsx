import { Sidebar } from './components/Sidebar'
import { Dashboard } from './pages/Dashboard'
import { Providers } from './pages/Providers'
import { Routing } from './pages/Routing'
import { Logs } from './pages/Logs'
import { useRoute } from './router'
import { VirtualKeys } from './pages/VirtualKeys'

const PAGES = {
  dashboard: Dashboard,
  providers: Providers,
  routing:   Routing,
  keys:      VirtualKeys,
  logs:      Logs,
}

export function App() {
  const route = useRoute()
  const Page = PAGES[route] ?? Dashboard

  return (
    <div class="flex h-screen bg-gray-50 text-gray-900 antialiased">
      <Sidebar active={route} />

      {/* Main content area */}
      <main class="flex-1 flex flex-col min-w-0 overflow-auto">
        {/* Top bar */}
        <header class="h-14 flex items-center border-b border-gray-200 bg-white px-6 shrink-0">
          <h1 class="text-sm font-semibold text-gray-500 uppercase tracking-widest">
            Love&nbsp;<span class="text-indigo-600">AI</span>&nbsp;Admin
          </h1>
        </header>

        {/* Page content */}
        <div class="flex-1 p-6 overflow-auto">
          <Page />
        </div>
      </main>
    </div>
  )
}
