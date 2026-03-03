import { NavLink, useNavigate } from 'react-router-dom'
import { useAuthStore } from '../stores/authStore'

const NAV_ITEMS: { label: string; to: string }[] = [
  { label: 'Dashboard', to: '/' },
  { label: 'Accounts', to: '/accounts' },
  { label: 'Contacts', to: '/contacts' },
  { label: 'Leads', to: '/leads' },
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
    <div style={styles.root}>
      {/* Sidebar */}
      <aside style={styles.sidebar}>
        <div style={styles.sidebarHeader}>
          <span style={styles.logo}>OpenSalesClaw</span>
        </div>
        <nav style={styles.nav}>
          {NAV_ITEMS.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.to === '/'}
              style={({ isActive }) => ({
                ...styles.navLink,
                ...(isActive ? styles.navLinkActive : {}),
              })}
            >
              {item.label}
            </NavLink>
          ))}
        </nav>
      </aside>

      {/* Main area */}
      <div style={styles.main}>
        {/* Top bar */}
        <header style={styles.topbar}>
          <span />
          <div style={styles.userArea}>
            <span style={styles.userName}>{fullName}</span>
            <button onClick={handleLogout} style={styles.logoutButton}>
              Logout
            </button>
          </div>
        </header>

        {/* Page content */}
        <main style={styles.content}>{children}</main>
      </div>
    </div>
  )
}

const styles: Record<string, React.CSSProperties> = {
  root: {
    display: 'flex',
    height: '100vh',
    overflow: 'hidden',
    fontFamily: 'system-ui, -apple-system, sans-serif',
    backgroundColor: '#f9fafb',
  },
  sidebar: {
    width: 220,
    flexShrink: 0,
    backgroundColor: '#1e293b',
    display: 'flex',
    flexDirection: 'column',
  },
  sidebarHeader: {
    padding: '1.25rem 1rem',
    borderBottom: '1px solid #334155',
  },
  logo: {
    fontWeight: 700,
    fontSize: '0.9375rem',
    color: '#f1f5f9',
    letterSpacing: '-0.01em',
  },
  nav: {
    display: 'flex',
    flexDirection: 'column',
    padding: '0.75rem 0',
    gap: 2,
  },
  navLink: {
    display: 'block',
    padding: '0.5rem 1rem',
    fontSize: '0.875rem',
    color: '#94a3b8',
    textDecoration: 'none',
    borderRadius: 0,
    transition: 'background 0.1s, color 0.1s',
  },
  navLinkActive: {
    color: '#f1f5f9',
    backgroundColor: '#334155',
  },
  main: {
    flex: 1,
    display: 'flex',
    flexDirection: 'column',
    overflow: 'hidden',
  },
  topbar: {
    height: 56,
    flexShrink: 0,
    backgroundColor: '#fff',
    borderBottom: '1px solid #e5e7eb',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: '0 1.5rem',
  },
  userArea: {
    display: 'flex',
    alignItems: 'center',
    gap: '0.75rem',
  },
  userName: {
    fontSize: '0.875rem',
    color: '#374151',
    fontWeight: 500,
  },
  logoutButton: {
    padding: '0.375rem 0.75rem',
    fontSize: '0.8125rem',
    border: '1px solid #d1d5db',
    borderRadius: 6,
    backgroundColor: '#fff',
    color: '#374151',
    cursor: 'pointer',
  },
  content: {
    flex: 1,
    overflowY: 'auto',
    padding: '2rem',
  },
}
