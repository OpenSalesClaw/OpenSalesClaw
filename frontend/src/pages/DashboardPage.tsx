import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { accountsApi } from '@/api/accounts'
import { casesApi } from '@/api/cases'
import { contactsApi } from '@/api/contacts'
import { leadsApi } from '@/api/leads'
import { opportunitiesApi } from '@/api/opportunities'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { useAuthStore } from '../stores/authStore'

interface Stat {
  label: string
  value: string
  to: string
}

export default function DashboardPage() {
  const navigate = useNavigate()
  const user = useAuthStore((s) => s.user)
  const [stats, setStats] = useState<Stat[]>([
    { label: 'Accounts', value: '—', to: '/accounts' },
    { label: 'Contacts', value: '—', to: '/contacts' },
    { label: 'Leads', value: '—', to: '/leads' },
    { label: 'Opportunities', value: '—', to: '/opportunities' },
    { label: 'Cases', value: '—', to: '/cases' },
  ])

  const fullName = [user?.first_name, user?.last_name].filter(Boolean).join(' ') || user?.email || 'User'

  useEffect(() => {
    void (async () => {
      try {
        const [accounts, contacts, leads, opportunities, cases] = await Promise.allSettled([
          accountsApi.list({ offset: 0, limit: 1 }),
          contactsApi.list({ offset: 0, limit: 1 }),
          leadsApi.list({ offset: 0, limit: 1 }),
          opportunitiesApi.list({ offset: 0, limit: 1 }),
          casesApi.list({ offset: 0, limit: 1 }),
        ])
        setStats([
          { label: 'Accounts', value: accounts.status === 'fulfilled' ? String(accounts.value.total) : '—', to: '/accounts' },
          { label: 'Contacts', value: contacts.status === 'fulfilled' ? String(contacts.value.total) : '—', to: '/contacts' },
          { label: 'Leads', value: leads.status === 'fulfilled' ? String(leads.value.total) : '—', to: '/leads' },
          { label: 'Opportunities', value: opportunities.status === 'fulfilled' ? String(opportunities.value.total) : '—', to: '/opportunities' },
          { label: 'Cases', value: cases.status === 'fulfilled' ? String(cases.value.total) : '—', to: '/cases' },
        ])
      } catch {
        // leave defaults
      }
    })()
  }, [])

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-semibold tracking-tight">Dashboard</h2>
        <p className="text-muted-foreground mt-1">Welcome back, {fullName}.</p>
      </div>

      <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-5">
        {stats.map((s) => (
          <Card
            key={s.label}
            className="cursor-pointer hover:shadow-md transition-shadow"
            onClick={() => navigate(s.to)}
          >
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">{s.label}</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-3xl font-bold">{s.value}</p>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}

