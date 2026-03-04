import { NavLink, useNavigate } from 'react-router-dom'
import { useAuthStore } from '../stores/authStore'
import { Button } from './ui/button'
import { Separator } from './ui/separator'

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
        <nav className="flex flex-col py-3 gap-0.5 flex-1">
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

        {/* Admin link — visible only to superusers */}
        {user?.is_superuser && (
          <>
            <Separator className="bg-slate-700" />
            <div className="pb-3 pt-2">
              <NavLink
                to="/admin"
                className={({ isActive }) =>
                  [
                    'flex items-center gap-2 px-4 py-2 text-sm no-underline transition-colors',
                    isActive ? 'text-slate-100 bg-slate-700' : 'text-slate-400 hover:text-slate-100 hover:bg-slate-700/50',
                  ].join(' ')
                }
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="14"
                  height="14"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                >
                  <path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z" />
                  <circle cx="12" cy="12" r="3" />
                </svg>
                Admin
              </NavLink>
            </div>
          </>
        )}
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
