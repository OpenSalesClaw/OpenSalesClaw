import type { FormEvent } from 'react'
import { useCallback, useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { deleteRole, getRole, listRoles, updateRole } from '@/api/roles'
import { listUsers } from '@/api/users'
import type { Role, RoleList, UserList } from '@/api/types'
import DeleteConfirmDialog from '@/components/DeleteConfirmDialog'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Separator } from '@/components/ui/separator'
import { Textarea } from '@/components/ui/textarea'

export default function AdminRoleDetailPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()

  const [role, setRole] = useState<Role | null>(null)
  const [allRoles, setAllRoles] = useState<RoleList[]>([])
  const [assignedUsers, setAssignedUsers] = useState<UserList[]>([])
  const [loading, setLoading] = useState(true)
  const [saveLoading, setSaveLoading] = useState(false)
  const [saveError, setSaveError] = useState<string | null>(null)
  const [showDelete, setShowDelete] = useState(false)
  const [deleteLoading, setDeleteLoading] = useState(false)

  const [form, setForm] = useState({ name: '', description: '', parent_role_id: '' })

  const load = useCallback(async () => {
    const [r, allR, users] = await Promise.all([
      getRole(Number(id)),
      listRoles({ limit: 200 }),
      listUsers({ role_id: Number(id), limit: 200 }),
    ])
    setRole(r)
    setAllRoles(allR.items)
    setAssignedUsers(users.items)
    setForm({
      name: r.name,
      description: r.description ?? '',
      parent_role_id: r.parent_role_id ? String(r.parent_role_id) : '',
    })
  }, [id])

  useEffect(() => {
    load().catch(() => navigate('/admin/roles')).finally(() => setLoading(false))
  }, [load, navigate])

  const roleMap = Object.fromEntries(allRoles.map((r) => [r.id, r.name]))

  // Exclude current role from parent options to avoid self-reference
  const parentOptions = allRoles.filter((r) => r.id !== Number(id))

  const childRoles = allRoles.filter((r) => r.parent_role_id === Number(id))

  const handleSave = async (e: FormEvent) => {
    e.preventDefault()
    setSaveError(null)
    setSaveLoading(true)
    try {
      const updated = await updateRole(Number(id), {
        name: form.name,
        description: form.description || null,
        parent_role_id: form.parent_role_id ? Number(form.parent_role_id) : null,
      })
      setRole(updated)
    } catch (err: unknown) {
      const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail
      setSaveError(typeof detail === 'string' ? detail : 'Failed to save changes.')
    } finally {
      setSaveLoading(false)
    }
  }

  const handleDelete = async () => {
    setDeleteLoading(true)
    try {
      await deleteRole(Number(id))
      navigate('/admin/roles')
    } catch (err: unknown) {
      const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail
      setSaveError(typeof detail === 'string' ? detail : 'Failed to delete role.')
      setShowDelete(false)
    } finally {
      setDeleteLoading(false)
    }
  }

  if (loading) return <div className="text-sm text-muted-foreground">Loading…</div>
  if (!role) return null

  return (
    <div className="max-w-2xl space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">{role.name}</h1>
          {role.parent_role_id && (
            <p className="text-sm text-muted-foreground mt-0.5">
              Parent: {roleMap[role.parent_role_id] ?? `Role #${role.parent_role_id}`}
            </p>
          )}
        </div>
        <Button
          variant="destructive"
          size="sm"
          onClick={() => setShowDelete(true)}
        >
          Delete
        </Button>
      </div>

      <Separator />

      {/* Edit form */}
      <form onSubmit={(e) => void handleSave(e)} className="space-y-5">
        {saveError && (
          <div className="rounded-md bg-destructive/10 border border-destructive/30 px-4 py-3 text-sm text-destructive">
            {saveError}
          </div>
        )}

        <div className="space-y-1.5">
          <Label htmlFor="name">Name *</Label>
          <Input
            id="name"
            required
            value={form.name}
            onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
          />
        </div>

        <div className="space-y-1.5">
          <Label htmlFor="description">Description</Label>
          <Textarea
            id="description"
            value={form.description}
            onChange={(e) => setForm((f) => ({ ...f, description: e.target.value }))}
            rows={3}
          />
        </div>

        <div className="space-y-1.5">
          <Label htmlFor="parent_role_id">Parent Role</Label>
          <Select
            value={form.parent_role_id || '__none__'}
            onValueChange={(v) => setForm((f) => ({ ...f, parent_role_id: v === '__none__' ? '' : v }))}
          >
            <SelectTrigger id="parent_role_id">
              <SelectValue placeholder="No parent (top-level)" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="__none__">No parent</SelectItem>
              {parentOptions.map((r) => (
                <SelectItem key={r.id} value={String(r.id)}>
                  {r.name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {/* Audit metadata */}
        <div className="rounded-lg border p-4 text-sm text-muted-foreground space-y-1">
          <p>
            <span className="font-medium text-foreground">Created:</span>{' '}
            {new Date(role.created_at).toLocaleString()}
          </p>
          <p>
            <span className="font-medium text-foreground">Updated:</span>{' '}
            {new Date(role.updated_at).toLocaleString()}
          </p>
        </div>

        <div className="flex gap-3 pt-2">
          <Button type="submit" disabled={saveLoading}>
            {saveLoading ? 'Saving…' : 'Save Changes'}
          </Button>
          <Button type="button" variant="outline" onClick={() => navigate('/admin/roles')}>
            Back to Roles
          </Button>
        </div>
      </form>

      {/* Child roles */}
      {childRoles.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Child Roles ({childRoles.length})</CardTitle>
          </CardHeader>
          <CardContent className="space-y-1">
            {childRoles.map((r) => (
              <button
                key={r.id}
                type="button"
                className="block w-full text-left text-sm px-2 py-1.5 rounded hover:bg-muted/50 hover:underline"
                onClick={() => navigate(`/admin/roles/${r.id}`)}
              >
                {r.name}
              </button>
            ))}
          </CardContent>
        </Card>
      )}

      {/* Assigned users */}
      {assignedUsers.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Assigned Users ({assignedUsers.length})</CardTitle>
          </CardHeader>
          <CardContent className="space-y-1">
            {assignedUsers.map((u) => (
              <button
                key={u.id}
                type="button"
                className="flex items-center gap-2 w-full text-left text-sm px-2 py-1.5 rounded hover:bg-muted/50"
                onClick={() => navigate(`/admin/users/${u.id}`)}
              >
                <span className="flex-1">
                  {[u.first_name, u.last_name].filter(Boolean).join(' ') || u.email}
                </span>
                <span className="text-muted-foreground">{u.email}</span>
              </button>
            ))}
          </CardContent>
        </Card>
      )}

      <DeleteConfirmDialog
        open={showDelete}
        onOpenChange={setShowDelete}
        onConfirm={() => void handleDelete()}
        loading={deleteLoading}
        title="Delete Role"
        description={`Delete role "${role.name}"? Users assigned to this role will lose their role assignment.`}
      />
    </div>
  )
}
