import { useAuthStore } from '../stores/authStore'

export default function DashboardPage() {
  const user = useAuthStore((s) => s.user)

  const fullName = [user?.first_name, user?.last_name].filter(Boolean).join(' ') || user?.email || 'User'

  return (
    <div>
      <h2 style={{ marginTop: 0, color: '#111827' }}>Dashboard</h2>
      <p style={{ color: '#6b7280' }}>Welcome back, {fullName}.</p>

      <div style={styles.cardGrid}>
        <StatCard label="Accounts" value="—" />
        <StatCard label="Contacts" value="—" />
        <StatCard label="Leads" value="—" />
      </div>

      <p style={{ marginTop: '2rem', color: '#9ca3af', fontSize: '0.875rem' }}>
        More widgets coming in a future phase.
      </p>
    </div>
  )
}

function StatCard({ label, value }: { label: string; value: string }) {
  return (
    <div style={styles.card}>
      <p style={styles.cardValue}>{value}</p>
      <p style={styles.cardLabel}>{label}</p>
    </div>
  )
}

const styles: Record<string, React.CSSProperties> = {
  cardGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fill, minmax(160px, 1fr))',
    gap: '1rem',
    marginTop: '1.5rem',
  },
  card: {
    backgroundColor: '#fff',
    border: '1px solid #e5e7eb',
    borderRadius: 8,
    padding: '1.25rem 1rem',
    textAlign: 'center',
  },
  cardValue: {
    fontSize: '2rem',
    fontWeight: 700,
    color: '#111827',
    margin: '0 0 0.25rem',
  },
  cardLabel: {
    fontSize: '0.875rem',
    color: '#6b7280',
    margin: 0,
  },
}
