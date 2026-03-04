import type { FormEvent } from 'react'
import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { listRoles } from '@/api/roles'
import type { AdminUserCreate, RoleList } from '@/api/types'
import { createUser } from '@/api/users'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Switch } from '@/components/ui/switch'

export default function AdminUserCreatePage() {
  const navigate = useNavigate()
  const [roles, setRoles] = useState<RoleList[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const [form, setForm] = useState<{
    email: string
    password: string
    first_name: string
    last_name: string
    role_id: string
    is_active: boolean
    is_superuser: boolean
  }>({
    email: '',
    password: '',
    first_name: '',
    last_name: '',
    role_id: '',
    is_active: true,
    is_superuser: false,
  })

  useEffect(() => {
    listRoles({ limit: 200 })
      .then((r) => setRoles(r.items))
      .catch(() => {})
  }, [])

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setError(null)
    setLoading(true)
    try {
      const payload: AdminUserCreate = {
        email: form.email,
        password: form.password,
        first_name: form.first_name || null,
        last_name: form.last_name || null,
        is_active: form.is_active,
        is_superuser: form.is_superuser,
        role_id: form.role_id ? Number(form.role_id) : null,
      }
      const user = await createUser(payload)
      navigate(`/admin/users/${user.id}`)
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail
      setError(typeof msg === 'string' ? msg : 'Failed to create user.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-xl space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">New User</h1>
        <p className="text-sm text-muted-foreground mt-0.5">Create a new user account.</p>
      </div>

      <form onSubmit={(e) => void handleSubmit(e)} className="space-y-5">
        {error && (
          <div className="rounded-md bg-destructive/10 border border-destructive/30 px-4 py-3 text-sm text-destructive">
            {error}
          </div>
        )}

        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-1.5">
            <Label htmlFor="first_name">First Name</Label>
            <Input
              id="first_name"
              value={form.first_name}
              onChange={(e) => setForm((f) => ({ ...f, first_name: e.target.value }))}
              placeholder="Jane"
            />
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="last_name">Last Name</Label>
            <Input
              id="last_name"
              value={form.last_name}
              onChange={(e) => setForm((f) => ({ ...f, last_name: e.target.value }))}
              placeholder="Smith"
            />
          </div>
        </div>

        <div className="space-y-1.5">
          <Label htmlFor="email">Email *</Label>
          <Input
            id="email"
            type="email"
            required
            value={form.email}
            onChange={(e) => setForm((f) => ({ ...f, email: e.target.value }))}
            placeholder="jane@example.com"
          />
        </div>

        <div className="space-y-1.5">
          <Label htmlFor="password">Password *</Label>
          <Input
            id="password"
            type="password"
            required
            value={form.password}
            onChange={(e) => setForm((f) => ({ ...f, password: e.target.value }))}
            placeholder="Min. 8 characters"
          />
        </div>

        <div className="space-y-1.5">
          <Label htmlFor="role_id">Role</Label>
          <Select value={form.role_id} onValueChange={(v) => setForm((f) => ({ ...f, role_id: v }))}>
            <SelectTrigger id="role_id">
              <SelectValue placeholder="No role assigned" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="">No role</SelectItem>
              {roles.map((r) => (
                <SelectItem key={r.id} value={String(r.id)}>
                  {r.name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <div className="space-y-3">
          <div className="flex items-center justify-between rounded-lg border p-4">
            <div>
              <p className="text-sm font-medium">Active</p>
              <p className="text-xs text-muted-foreground">User can log in.</p>
            </div>
            <Switch
              checked={form.is_active}
              onCheckedChange={(v) => setForm((f) => ({ ...f, is_active: v }))}
            />
          </div>
          <div className="flex items-center justify-between rounded-lg border p-4">
            <div>
              <p className="text-sm font-medium">Superuser / Admin</p>
              <p className="text-xs text-muted-foreground">Full access to admin features.</p>
            </div>
            <Switch
              checked={form.is_superuser}
              onCheckedChange={(v) => setForm((f) => ({ ...f, is_superuser: v }))}
            />
          </div>
        </div>

        <div className="flex gap-3 pt-2">
          <Button type="submit" disabled={loading}>
            {loading ? 'Creating…' : 'Create User'}
          </Button>
          <Button type="button" variant="outline" onClick={() => navigate('/admin/users')}>
            Cancel
          </Button>
        </div>
      </form>
    </div>
  )
}
