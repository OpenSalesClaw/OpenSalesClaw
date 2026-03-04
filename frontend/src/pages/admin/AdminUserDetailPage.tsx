import type { FormEvent } from 'react'
import { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { listRoles } from '@/api/roles'
import type { RoleList, User } from '@/api/types'
import { deleteUser, getUser, resetUserPassword, updateUser } from '@/api/users'
import DeleteConfirmDialog from '@/components/DeleteConfirmDialog'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Separator } from '@/components/ui/separator'
import { Switch } from '@/components/ui/switch'
import { useAuthStore } from '@/stores/authStore'

export default function AdminUserDetailPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const currentUser = useAuthStore((s) => s.user)

  const [user, setUser] = useState<User | null>(null)
  const [roles, setRoles] = useState<RoleList[]>([])
  const [loading, setLoading] = useState(true)
  const [editLoading, setEditLoading] = useState(false)
  const [editError, setEditError] = useState<string | null>(null)
  const [showDelete, setShowDelete] = useState(false)
  const [deleteLoading, setDeleteLoading] = useState(false)

  // Reset-password state
  const [showResetPw, setShowResetPw] = useState(false)
  const [newPassword, setNewPassword] = useState('')
  const [resetLoading, setResetLoading] = useState(false)
  const [resetError, setResetError] = useState<string | null>(null)
  const [resetSuccess, setResetSuccess] = useState(false)

  // Edit form
  const [form, setForm] = useState({
    first_name: '',
    last_name: '',
    email: '',
    role_id: '',
    is_active: true,
    is_superuser: false,
  })

  const isSelf = currentUser?.id === Number(id)

  useEffect(() => {
    Promise.all([getUser(Number(id)), listRoles({ limit: 200 })])
      .then(([u, r]) => {
        setUser(u)
        setRoles(r.items)
        setForm({
          first_name: u.first_name ?? '',
          last_name: u.last_name ?? '',
          email: u.email,
          role_id: u.role_id ? String(u.role_id) : '',
          is_active: u.is_active,
          is_superuser: u.is_superuser,
        })
      })
      .catch(() => navigate('/admin/users'))
      .finally(() => setLoading(false))
  }, [id, navigate])

  const roleMap = Object.fromEntries(roles.map((r) => [r.id, r.name]))

  const handleSave = async (e: FormEvent) => {
    e.preventDefault()
    setEditError(null)
    setEditLoading(true)
    try {
      const updated = await updateUser(Number(id), {
        first_name: form.first_name || null,
        last_name: form.last_name || null,
        email: form.email,
        role_id: form.role_id ? Number(form.role_id) : null,
        is_active: form.is_active,
        is_superuser: form.is_superuser,
      })
      setUser(updated)
    } catch (err: unknown) {
      const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail
      setEditError(typeof detail === 'string' ? detail : 'Failed to save changes.')
    } finally {
      setEditLoading(false)
    }
  }

  const handleDelete = async () => {
    setDeleteLoading(true)
    try {
      await deleteUser(Number(id))
      navigate('/admin/users')
    } catch (err: unknown) {
      const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail
      setEditError(typeof detail === 'string' ? detail : 'Failed to delete user.')
      setShowDelete(false)
    } finally {
      setDeleteLoading(false)
    }
  }

  const handleResetPassword = async (e: FormEvent) => {
    e.preventDefault()
    setResetError(null)
    setResetLoading(true)
    setResetSuccess(false)
    try {
      await resetUserPassword(Number(id), { new_password: newPassword })
      setNewPassword('')
      setShowResetPw(false)
      setResetSuccess(true)
    } catch (err: unknown) {
      const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail
      setResetError(typeof detail === 'string' ? detail : 'Failed to reset password.')
    } finally {
      setResetLoading(false)
    }
  }

  if (loading) {
    return <div className="text-sm text-muted-foreground">Loading…</div>
  }

  if (!user) return null

  return (
    <div className="max-w-2xl space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">
            {[user.first_name, user.last_name].filter(Boolean).join(' ') || user.email}
          </h1>
          <p className="text-sm text-muted-foreground mt-0.5">{user.email}</p>
          <div className="flex gap-1.5 mt-2">
            {user.is_active ? (
              <Badge variant="secondary">Active</Badge>
            ) : (
              <Badge variant="destructive">Inactive</Badge>
            )}
            {user.is_superuser && <Badge>Admin</Badge>}
            {user.role_id && (
              <Badge variant="outline">{roleMap[user.role_id] ?? `Role #${user.role_id}`}</Badge>
            )}
          </div>
        </div>
        <div className="flex gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setShowResetPw((v) => !v)}
          >
            Reset Password
          </Button>
          <Button
            variant="destructive"
            size="sm"
            disabled={isSelf}
            title={isSelf ? 'You cannot delete your own account.' : undefined}
            onClick={() => setShowDelete(true)}
          >
            Delete
          </Button>
        </div>
      </div>

      {resetSuccess && (
        <div className="rounded-md bg-green-50 border border-green-200 px-4 py-3 text-sm text-green-800">
          Password reset successfully.
        </div>
      )}

      {/* Reset password inline form */}
      {showResetPw && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Reset Password</CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={(e) => void handleResetPassword(e)} className="flex items-end gap-3">
              <div className="space-y-1.5 flex-1">
                <Label htmlFor="new_password">New Password (min. 8 chars)</Label>
                <Input
                  id="new_password"
                  type="password"
                  required
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  placeholder="Enter new password…"
                />
              </div>
              <Button type="submit" disabled={resetLoading}>
                {resetLoading ? 'Saving…' : 'Set Password'}
              </Button>
              <Button type="button" variant="ghost" onClick={() => setShowResetPw(false)}>
                Cancel
              </Button>
            </form>
            {resetError && (
              <p className="mt-2 text-sm text-destructive">{resetError}</p>
            )}
          </CardContent>
        </Card>
      )}

      <Separator />

      {/* Edit form */}
      <form onSubmit={(e) => void handleSave(e)} className="space-y-5">
        {editError && (
          <div className="rounded-md bg-destructive/10 border border-destructive/30 px-4 py-3 text-sm text-destructive">
            {editError}
          </div>
        )}

        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-1.5">
            <Label htmlFor="first_name">First Name</Label>
            <Input
              id="first_name"
              value={form.first_name}
              onChange={(e) => setForm((f) => ({ ...f, first_name: e.target.value }))}
            />
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="last_name">Last Name</Label>
            <Input
              id="last_name"
              value={form.last_name}
              onChange={(e) => setForm((f) => ({ ...f, last_name: e.target.value }))}
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
          />
        </div>

        <div className="space-y-1.5">
          <Label htmlFor="role_id">Role</Label>
          <Select
            value={form.role_id || '__none__'}
            onValueChange={(v) => setForm((f) => ({ ...f, role_id: v === '__none__' ? '' : v }))}
          >
            <SelectTrigger id="role_id">
              <SelectValue placeholder="No role assigned" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="__none__">No role</SelectItem>
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
              disabled={isSelf}
              title={isSelf ? 'You cannot deactivate your own account.' : undefined}
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
              disabled={isSelf}
              title={isSelf ? 'You cannot remove superuser from your own account.' : undefined}
              onCheckedChange={(v) => setForm((f) => ({ ...f, is_superuser: v }))}
            />
          </div>
        </div>

        {/* Audit metadata */}
        <div className="rounded-lg border p-4 text-sm text-muted-foreground space-y-1">
          <p>
            <span className="font-medium text-foreground">Created:</span>{' '}
            {new Date(user.created_at).toLocaleString()}
          </p>
          <p>
            <span className="font-medium text-foreground">Updated:</span>{' '}
            {new Date(user.updated_at).toLocaleString()}
          </p>
        </div>

        <div className="flex gap-3 pt-2">
          <Button type="submit" disabled={editLoading}>
            {editLoading ? 'Saving…' : 'Save Changes'}
          </Button>
          <Button type="button" variant="outline" onClick={() => navigate('/admin/users')}>
            Back to Users
          </Button>
        </div>
      </form>

      <DeleteConfirmDialog
        open={showDelete}
        onOpenChange={setShowDelete}
        onConfirm={() => void handleDelete()}
        loading={deleteLoading}
        title="Delete User"
        description={`Permanently delete user "${user.email}"? This action soft-deletes the record and cannot be undone easily.`}
      />
    </div>
  )
}
