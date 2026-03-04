import { useCallback, useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { deleteRole, getRoleHierarchy, type RoleHierarchyItem } from '@/api/roles'
import RoleTree from '@/components/admin/RoleTree'
import DeleteConfirmDialog from '@/components/DeleteConfirmDialog'
import { Button } from '@/components/ui/button'

export default function AdminRolesPage() {
  const navigate = useNavigate()
  const [roles, setRoles] = useState<RoleHierarchyItem[]>([])
  const [loading, setLoading] = useState(true)
  const [deleteTarget, setDeleteTarget] = useState<{ id: number; name: string } | null>(null)
  const [deleteLoading, setDeleteLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const load = useCallback(async () => {
    setLoading(true)
    try {
      const data = await getRoleHierarchy()
      setRoles(data)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    void load()
  }, [load])

  const handleDelete = async () => {
    if (!deleteTarget) return
    setDeleteLoading(true)
    try {
      await deleteRole(deleteTarget.id)
      setDeleteTarget(null)
      await load()
    } catch (err: unknown) {
      const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail
      setError(typeof detail === 'string' ? detail : 'Failed to delete role.')
      setDeleteTarget(null)
    } finally {
      setDeleteLoading(false)
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Roles</h1>
          <p className="text-sm text-muted-foreground mt-0.5">
            Manage organizational roles and hierarchy.
          </p>
        </div>
        <Button onClick={() => navigate('/admin/roles/new')}>+ New Role</Button>
      </div>

      {error && (
        <div className="rounded-md bg-destructive/10 border border-destructive/30 px-4 py-3 text-sm text-destructive">
          {error}
        </div>
      )}

      {loading ? (
        <div className="py-8 text-center text-sm text-muted-foreground">Loading…</div>
      ) : (
        <RoleTree
          nodes={roles}
          onDelete={(id, name) => setDeleteTarget({ id, name })}
        />
      )}

      <DeleteConfirmDialog
        open={deleteTarget !== null}
        onOpenChange={(open) => { if (!open) setDeleteTarget(null) }}
        onConfirm={() => void handleDelete()}
        loading={deleteLoading}
        title="Delete Role"
        description={`Delete role "${deleteTarget?.name ?? ''}"? Users assigned to this role will lose their role assignment.`}
      />
    </div>
  )
}
