import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Bar, BarChart, CartesianGrid, Cell, Legend, Pie, PieChart, XAxis, YAxis } from 'recharts'
import { accountsApi } from '@/api/accounts'
import { casesApi } from '@/api/cases'
import { contactsApi } from '@/api/contacts'
import { leadsApi } from '@/api/leads'
import { opportunitiesApi } from '@/api/opportunities'
import type { PipelineStage } from '@/api/types'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { ChartContainer, ChartTooltip, ChartTooltipContent, type ChartConfig } from '@/components/ui/chart'
import { useAuthStore } from '../stores/authStore'

// ── Constants ────────────────────────────────────────────────────────────────

const LEAD_STATUSES = ['New', 'Contacted', 'Qualified', 'Unqualified', 'Converted'] as const
const CASE_PRIORITIES = ['Low', 'Medium', 'High', 'Critical'] as const
const CASE_STATUSES = ['New', 'Working', 'Escalated', 'Closed'] as const

const STAGE_SHORT: Record<string, string> = {
  Prospecting: 'Prospecting',
  Qualification: 'Qualification',
  'Needs Analysis': 'Needs Analysis',
  'Value Proposition': 'Value Prop.',
  'Id. Decision Makers': 'Decision Makers',
  'Perception Analysis': 'Perception',
  'Proposal/Price Quote': 'Proposal',
  'Negotiation/Review': 'Negotiation',
  'Closed Won': 'Closed Won',
  'Closed Lost': 'Closed Lost',
}

const LEAD_COLORS = [
  'var(--chart-1)',
  'var(--chart-2)',
  'var(--chart-3)',
  'var(--chart-4)',
  'var(--chart-5)',
]

const PRIORITY_COLOR: Record<string, string> = {
  Low: 'var(--chart-2)',
  Medium: 'var(--chart-1)',
  High: 'var(--chart-4)',
  Critical: 'var(--chart-5)',
}

// ── Chart configs ─────────────────────────────────────────────────────────────

const pipelineConfig = {
  count: { label: 'Deals', color: 'var(--chart-1)' },
  total_amount: { label: 'Amount ($)', color: 'var(--chart-2)' },
} satisfies ChartConfig

const leadConfig = Object.fromEntries(
  LEAD_STATUSES.map((s, i) => [s, { label: s, color: LEAD_COLORS[i] }]),
) satisfies ChartConfig

const priorityConfig = Object.fromEntries(
  CASE_PRIORITIES.map((p) => [p, { label: p, color: PRIORITY_COLOR[p] }]),
) satisfies ChartConfig

const caseStatusConfig = {
  count: { label: 'Cases', color: 'var(--chart-3)' },
} satisfies ChartConfig

// ── Types ─────────────────────────────────────────────────────────────────────

interface Stat {
  label: string
  value: string
  to: string
}

interface CountEntry {
  key: string
  count: number
}

// ── Component ─────────────────────────────────────────────────────────────────

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
  const [pipeline, setPipeline] = useState<PipelineStage[]>([])
  const [leadsByStatus, setLeadsByStatus] = useState<CountEntry[]>([])
  const [casesByStatus, setCasesByStatus] = useState<CountEntry[]>([])
  const [casesByPriority, setCasesByPriority] = useState<CountEntry[]>([])

  const fullName = [user?.first_name, user?.last_name].filter(Boolean).join(' ') || user?.email || 'User'

  useEffect(() => {
    void (async () => {
      // ── Summary counts ────────────────────────────────────────────────────
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
        {
          label: 'Opportunities',
          value: opportunities.status === 'fulfilled' ? String(opportunities.value.total) : '—',
          to: '/opportunities',
        },
        { label: 'Cases', value: cases.status === 'fulfilled' ? String(cases.value.total) : '—', to: '/cases' },
      ])

      // ── Pipeline ──────────────────────────────────────────────────────────
      try {
        setPipeline(await opportunitiesApi.pipeline())
      } catch {
        /* ignore */
      }

      // ── Leads by status ───────────────────────────────────────────────────
      try {
        const { items } = await leadsApi.list({ offset: 0, limit: 200 })
        const counts: Record<string, number> = {}
        for (const l of items) counts[l.status] = (counts[l.status] ?? 0) + 1
        setLeadsByStatus(
          LEAD_STATUSES.map((s) => ({ key: s, count: counts[s] ?? 0 })).filter((d) => d.count > 0),
        )
      } catch {
        /* ignore */
      }

      // ── Cases by status & priority ────────────────────────────────────────
      try {
        const { items } = await casesApi.list({ offset: 0, limit: 200 })
        const byStatus: Record<string, number> = {}
        const byPriority: Record<string, number> = {}
        for (const c of items) {
          byStatus[c.status] = (byStatus[c.status] ?? 0) + 1
          byPriority[c.priority] = (byPriority[c.priority] ?? 0) + 1
        }
        setCasesByStatus(CASE_STATUSES.map((s) => ({ key: s, count: byStatus[s] ?? 0 })).filter((d) => d.count > 0))
        setCasesByPriority(
          CASE_PRIORITIES.map((p) => ({ key: p, count: byPriority[p] ?? 0 })).filter((d) => d.count > 0),
        )
      } catch {
        /* ignore */
      }
    })()
  }, [])

  const pipelineData = pipeline.map((p) => ({
    stage: STAGE_SHORT[p.stage] ?? p.stage,
    count: p.count,
    total_amount: p.total_amount ?? 0,
  }))

  return (
    <div className="space-y-6">
      {/* ── Header ── */}
      <div>
        <h2 className="text-2xl font-semibold tracking-tight">Dashboard</h2>
        <p className="text-muted-foreground mt-1">Welcome back, {fullName}.</p>
      </div>

      {/* ── Stat cards ── */}
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-5">
        {stats.map((s) => (
          <Card key={s.label} className="cursor-pointer hover:shadow-md transition-shadow" onClick={() => navigate(s.to)}>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">{s.label}</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-3xl font-bold">{s.value}</p>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* ── Opportunity Pipeline ── */}
      <Card>
        <CardHeader>
          <CardTitle>Opportunity Pipeline</CardTitle>
          <CardDescription>Deal count and total value by sales stage</CardDescription>
        </CardHeader>
        <CardContent>
          {pipelineData.length === 0 ? (
            <p className="text-muted-foreground text-sm py-8 text-center">No opportunities yet.</p>
          ) : (
            <ChartContainer config={pipelineConfig} className="h-72 w-full">
              <BarChart data={pipelineData} margin={{ top: 4, right: 16, bottom: 52, left: 0 }}>
                <CartesianGrid vertical={false} strokeDasharray="3 3" />
                <XAxis dataKey="stage" tick={{ fontSize: 11 }} angle={-35} textAnchor="end" interval={0} />
                <YAxis yAxisId="left" allowDecimals={false} width={36} tick={{ fontSize: 11 }} />
                <YAxis
                  yAxisId="right"
                  orientation="right"
                  tickFormatter={(v: number) => `$${(v / 1000).toFixed(0)}k`}
                  width={52}
                  tick={{ fontSize: 11 }}
                />
                <ChartTooltip content={<ChartTooltipContent />} />
                <Bar yAxisId="left" dataKey="count" fill="var(--color-count)" radius={[4, 4, 0, 0]} />
                <Bar yAxisId="right" dataKey="total_amount" fill="var(--color-total_amount)" radius={[4, 4, 0, 0]} name="Amount ($)" />
              </BarChart>
            </ChartContainer>
          )}
        </CardContent>
      </Card>

      {/* ── Leads by Status  +  Cases by Status ── */}
      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        {/* Leads donut */}
        <Card>
          <CardHeader>
            <CardTitle>Leads by Status</CardTitle>
            <CardDescription>Distribution of leads across pipeline stages</CardDescription>
          </CardHeader>
          <CardContent className="flex items-center justify-center">
            {leadsByStatus.length === 0 ? (
              <p className="text-muted-foreground text-sm py-8 text-center">No leads yet.</p>
            ) : (
              <ChartContainer config={leadConfig} className="h-64 w-full max-w-xs">
                <PieChart>
                  <Pie data={leadsByStatus} dataKey="count" nameKey="key" cx="50%" cy="50%" innerRadius="38%" outerRadius="65%" paddingAngle={3}>
                    {leadsByStatus.map((entry, i) => (
                      <Cell key={entry.key} fill={LEAD_COLORS[i % LEAD_COLORS.length]} />
                    ))}
                  </Pie>
                  <ChartTooltip content={<ChartTooltipContent nameKey="key" />} />
                  <Legend iconType="circle" iconSize={10} formatter={(v) => v} />
                </PieChart>
              </ChartContainer>
            )}
          </CardContent>
        </Card>

        {/* Cases by status horizontal bar */}
        <Card>
          <CardHeader>
            <CardTitle>Cases by Status</CardTitle>
            <CardDescription>Open vs. closed support cases</CardDescription>
          </CardHeader>
          <CardContent>
            {casesByStatus.length === 0 ? (
              <p className="text-muted-foreground text-sm py-8 text-center">No cases yet.</p>
            ) : (
              <ChartContainer config={caseStatusConfig} className="h-64 w-full">
                <BarChart data={casesByStatus} layout="vertical" margin={{ left: 8, right: 24, top: 4, bottom: 4 }}>
                  <CartesianGrid horizontal={false} strokeDasharray="3 3" />
                  <XAxis type="number" allowDecimals={false} tick={{ fontSize: 11 }} />
                  <YAxis type="category" dataKey="key" width={72} tick={{ fontSize: 12 }} />
                  <ChartTooltip content={<ChartTooltipContent />} />
                  <Bar dataKey="count" fill="var(--color-count)" radius={[0, 4, 4, 0]} />
                </BarChart>
              </ChartContainer>
            )}
          </CardContent>
        </Card>
      </div>

      {/* ── Cases by Priority ── */}
      <Card>
        <CardHeader>
          <CardTitle>Cases by Priority</CardTitle>
          <CardDescription>Volume of support cases at each severity level</CardDescription>
        </CardHeader>
        <CardContent>
          {casesByPriority.length === 0 ? (
            <p className="text-muted-foreground text-sm py-8 text-center">No cases yet.</p>
          ) : (
            <ChartContainer config={priorityConfig} className="h-52 w-full">
              <BarChart data={casesByPriority} margin={{ top: 4, right: 16, bottom: 4, left: 0 }}>
                <CartesianGrid vertical={false} strokeDasharray="3 3" />
                <XAxis dataKey="key" tick={{ fontSize: 12 }} />
                <YAxis allowDecimals={false} width={36} tick={{ fontSize: 11 }} />
                <ChartTooltip content={<ChartTooltipContent />} />
                <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                  {casesByPriority.map((entry) => (
                    <Cell key={entry.key} fill={PRIORITY_COLOR[entry.key] ?? 'hsl(var(--chart-1))'} />
                  ))}
                </Bar>
              </BarChart>
            </ChartContainer>
          )}
        </CardContent>
      </Card>
    </div>
  )
}

