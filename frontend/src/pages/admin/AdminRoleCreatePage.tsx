import type { FormEvent } from 'react'
import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { createRole, listRoles } from '@/api/roles'
import type { RoleList } from '@/api/types'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Textarea } from '@/components/ui/textarea'

export default function AdminRoleCreatePage() {
  const navigate = useNavigate()
  const [roles, setRoles] = useState<RoleList[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [form, setForm] = useState({ name: '', description: '', parent_role_id: '' })

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
      const role = await createRole({
        name: form.name,
        description: form.description || null,
        parent_role_id: form.parent_role_id ? Number(form.parent_role_id) : null,
      })
      navigate(`/admin/roles/${role.id}`)
    } catch (err: unknown) {
      const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail
      setError(typeof detail === 'string' ? detail : 'Failed to create role.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-xl space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">New Role</h1>
        <p className="text-sm text-muted-foreground mt-0.5">Create a new organizational role.</p>
      </div>

      <form onSubmit={(e) => void handleSubmit(e)} className="space-y-5">
        {error && (
          <div className="rounded-md bg-destructive/10 border border-destructive/30 px-4 py-3 text-sm text-destructive">
            {error}
          </div>
        )}

        <div className="space-y-1.5">
          <Label htmlFor="name">Name *</Label>
          <Input
            id="name"
            required
            value={form.name}
            onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
            placeholder="e.g. Sales Manager"
          />
        </div>

        <div className="space-y-1.5">
          <Label htmlFor="description">Description</Label>
          <Textarea
            id="description"
            value={form.description}
            onChange={(e) => setForm((f) => ({ ...f, description: e.target.value }))}
            placeholder="Optional description…"
            rows={3}
          />
        </div>

        <div className="space-y-1.5">
          <Label htmlFor="parent_role_id">Parent Role</Label>
          <Select
            value={form.parent_role_id}
            onValueChange={(v) => setForm((f) => ({ ...f, parent_role_id: v }))}
          >
            <SelectTrigger id="parent_role_id">
              <SelectValue placeholder="No parent (top-level)" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="">No parent</SelectItem>
              {roles.map((r) => (
                <SelectItem key={r.id} value={String(r.id)}>
                  {r.name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <div className="flex gap-3 pt-2">
          <Button type="submit" disabled={loading}>
            {loading ? 'Creating…' : 'Create Role'}
          </Button>
          <Button type="button" variant="outline" onClick={() => navigate('/admin/roles')}>
            Cancel
          </Button>
        </div>
      </form>
    </div>
  )
}
