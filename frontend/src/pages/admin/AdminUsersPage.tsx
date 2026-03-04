import { useCallback, useEffect, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { listRoles } from '@/api/roles'
import type { RoleList, UserList } from '@/api/types'
import { listUsers } from '@/api/users'
import DataTable, { type Column } from '@/components/DataTable'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'

const PAGE_SIZE = 20

const COLUMNS: Column<UserList>[] = [
  {
    key: 'name',
    label: 'Name',
    render: (r) => [r.first_name, r.last_name].filter(Boolean).join(' ') || '—',
  },
  { key: 'email', label: 'Email' },
  {
    key: 'role_id',
    label: 'Role',
    render: () => '—', // replaced dynamically below via roleMap
  },
  {
    key: 'is_active',
    label: 'Active',
    render: (r) =>
      r.is_active ? (
        <Badge variant="secondary">Active</Badge>
      ) : (
        <Badge variant="destructive">Inactive</Badge>
      ),
  },
  {
    key: 'is_superuser',
    label: 'Superuser',
    render: (r) => (r.is_superuser ? <Badge>Admin</Badge> : null),
  },
]

export default function AdminUsersPage() {
  const navigate = useNavigate()
  const [users, setUsers] = useState<UserList[]>([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [loading, setLoading] = useState(false)
  const [emailFilter, setEmailFilter] = useState('')
  const [activeFilter, setActiveFilter] = useState<string>('all')
  const [roles, setRoles] = useState<RoleList[]>([])

  const emailInputRef = useRef<HTMLInputElement>(null)

  // Load roles for the role name display
  useEffect(() => {
    listRoles({ limit: 200 })
      .then((r) => setRoles(r.items))
      .catch(() => {})
  }, [])

  const roleMap = Object.fromEntries(roles.map((r) => [r.id, r.name]))

  const load = useCallback(
    async (p: number, email: string, active: string) => {
      setLoading(true)
      try {
        const params: Record<string, unknown> = { offset: (p - 1) * PAGE_SIZE, limit: PAGE_SIZE }
        if (email) params.email = email
        if (active === 'active') params.is_active = true
        if (active === 'inactive') params.is_active = false
        const data = await listUsers(params as Parameters<typeof listUsers>[0])
        setUsers(data.items)
        setTotal(data.total)
      } finally {
        setLoading(false)
      }
    },
    [],
  )

  useEffect(() => {
    void load(page, emailFilter, activeFilter)
  }, [load, page, emailFilter, activeFilter])

  // Enrich columns with role names
  const enrichedColumns = COLUMNS.map((col) =>
    col.key === 'role_id'
      ? {
          ...col,
          render: (r: UserList) => (r.role_id ? (roleMap[r.role_id] ?? `#${r.role_id}`) : '—'),
        }
      : col,
  )

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Users</h1>
          <p className="text-sm text-muted-foreground mt-0.5">Manage user accounts and access.</p>
        </div>
        <Button onClick={() => navigate('/admin/users/new')}>+ New User</Button>
      </div>

      {/* Filters */}
      <div className="flex items-center gap-3">
        <Input
          ref={emailInputRef}
          className="max-w-xs"
          placeholder="Search by email…"
          value={emailFilter}
          onChange={(e) => {
            setEmailFilter(e.target.value)
            setPage(1)
          }}
        />
        <Select
          value={activeFilter}
          onValueChange={(v) => {
            setActiveFilter(v)
            setPage(1)
          }}
        >
          <SelectTrigger className="w-36">
            <SelectValue placeholder="Status" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All statuses</SelectItem>
            <SelectItem value="active">Active</SelectItem>
            <SelectItem value="inactive">Inactive</SelectItem>
          </SelectContent>
        </Select>
        {(emailFilter || activeFilter !== 'all') && (
          <Button
            variant="ghost"
            size="sm"
            onClick={() => {
              setEmailFilter('')
              setActiveFilter('all')
              setPage(1)
            }}
          >
            Clear
          </Button>
        )}
      </div>

      <DataTable
        columns={enrichedColumns}
        data={users}
        loading={loading}
        total={total}
        page={page}
        pageSize={PAGE_SIZE}
        onPageChange={setPage}
        onRowClick={(u) => navigate(`/admin/users/${u.id}`)}
        emptyMessage="No users found."
      />
    </div>
  )
}
