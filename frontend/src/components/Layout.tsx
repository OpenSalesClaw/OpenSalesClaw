import { NavLink, useNavigate } from 'react-router-dom'
import { useAuthStore } from '../stores/authStore'
import { Button } from './ui/button'

const NAV_ITEMS: { label: string; to: string }[] = [
  { label: 'Dashboard', to: '/' },
  { label: 'Accounts', to: '/accounts' },
  { label: 'Contacts', to: '/contacts' },
  { label: 'Leads', to: '/leads' },
  { label: 'Opportunities', to: '/opportunities' },
  { label: 'Cases', to: '/cases' },
]

interface LayoutProps {
  children: React.ReactNode
}

export default function Layout({ children }: LayoutProps) {
  const navigate = useNavigate()
  const { user, logout } = useAuthStore()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  const fullName = [user?.first_name, user?.last_name].filter(Boolean).join(' ') || user?.email || 'User'

  return (
    <div className="flex h-screen overflow-hidden bg-gray-50 font-sans">
      {/* Sidebar */}
      <aside className="w-[220px] shrink-0 flex flex-col bg-slate-800">
        <div className="px-4 py-5 border-b border-slate-700">
          <span className="font-bold text-[0.9375rem] text-slate-100 tracking-tight">OpenSalesClaw</span>
        </div>
        <nav className="flex flex-col py-3 gap-0.5">
          {NAV_ITEMS.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.to === '/'}
              className={({ isActive }) =>
                [
                  'block px-4 py-2 text-sm no-underline transition-colors',
                  isActive ? 'text-slate-100 bg-slate-700' : 'text-slate-400 hover:text-slate-100 hover:bg-slate-700/50',
                ].join(' ')
              }
            >
              {item.label}
            </NavLink>
          ))}
        </nav>
      </aside>

      {/* Main area */}
      <div className="flex flex-1 flex-col overflow-hidden">
        {/* Top bar */}
        <header className="h-14 shrink-0 bg-white border-b border-gray-200 flex items-center justify-between px-6">
          <span />
          <div className="flex items-center gap-3">
            <span className="text-sm font-medium text-gray-700">{fullName}</span>
            <Button variant="outline" size="sm" onClick={handleLogout}>
              Logout
            </Button>
          </div>
        </header>

        {/* Page content */}
        <main className="flex-1 overflow-auto p-6">{children}</main>
      </div>
    </div>
  )
}
