import { NavLink, useNavigate } from 'react-router-dom'
import { useAuthStore } from '../stores/authStore'
import { Button } from './ui/button'
import { Separator } from './ui/separator'

const ADMIN_NAV: { label: string; to: string }[] = [
  { label: 'Users', to: '/admin/users' },
  { label: 'Roles', to: '/admin/roles' },
  // Future: Custom Fields, Custom Objects, Picklists, Settings…
]

interface AdminLayoutProps {
  children: React.ReactNode
}

export default function AdminLayout({ children }: AdminLayoutProps) {
  const navigate = useNavigate()
  const { user, logout } = useAuthStore()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  const fullName = [user?.first_name, user?.last_name].filter(Boolean).join(' ') || user?.email || 'User'

  return (
    <div className="flex h-screen overflow-hidden bg-gray-50 font-sans">
      {/* Admin Sidebar */}
      <aside className="w-[220px] shrink-0 flex flex-col bg-slate-900">
        {/* Header */}
        <div className="px-4 py-5 border-b border-slate-700">
          <span className="block font-bold text-[0.9375rem] text-slate-100 tracking-tight">OpenSalesClaw</span>
          <span className="block text-xs text-slate-400 mt-0.5">Admin</span>
        </div>

        {/* Back to CRM */}
        <div className="px-4 py-3">
          <NavLink
            to="/"
            className="flex items-center gap-1.5 text-xs text-slate-400 hover:text-slate-200 transition-colors"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="12"
              height="12"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <polyline points="15 18 9 12 15 6" />
            </svg>
            Back to CRM
          </NavLink>
        </div>

        <Separator className="bg-slate-700" />

        {/* Nav items */}
        <nav className="flex flex-col py-3 gap-0.5">
          {ADMIN_NAV.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
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
          <span className="text-sm font-semibold text-gray-500 uppercase tracking-wide">Administration</span>
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
