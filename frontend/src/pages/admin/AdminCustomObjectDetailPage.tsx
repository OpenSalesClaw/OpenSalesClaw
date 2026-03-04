import type { FormEvent } from 'react'
import { useCallback, useEffect, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { customObjectsApi } from '@/api/customObjects'
import { listCustomFieldDefinitions } from '@/api/customFieldDefinitions'
import type { CustomFieldDefinition, CustomObject } from '@/api/types'
import DeleteConfirmDialog from '@/components/DeleteConfirmDialog'
import DataTable, { type Column } from '@/components/DataTable'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Separator } from '@/components/ui/separator'
import { Switch } from '@/components/ui/switch'
import { Textarea } from '@/components/ui/textarea'

const FIELD_COLUMNS: Column<CustomFieldDefinition>[] = [
  { key: 'field_name', label: 'API Name' },
  { key: 'field_label', label: 'Label', render: (r) => r.field_label ?? '—' },
  { key: 'field_type', label: 'Type', render: (r) => <Badge variant="secondary">{r.field_type}</Badge> },
  {
    key: 'is_required',
    label: 'Required',
    render: (r) =>
      r.is_required ? <Badge variant="destructive">Required</Badge> : <span className="text-muted-foreground">—</span>,
  },
]

export default function AdminCustomObjectDetailPage() {
  const { apiName } = useParams<{ apiName: string }>()
  const navigate = useNavigate()

  const [object, setObject] = useState<CustomObject | null>(null)
  const [fields, setFields] = useState<CustomFieldDefinition[]>([])
  const [loading, setLoading] = useState(true)
  const [saveLoading, setSaveLoading] = useState(false)
  const [saveError, setSaveError] = useState<string | null>(null)
  const [showDelete, setShowDelete] = useState(false)
  const [deleteLoading, setDeleteLoading] = useState(false)

  const [form, setForm] = useState({
    label: '',
    plural_label: '',
    description: '',
    icon_name: '',
    is_active: true,
  })

  const load = useCallback(async () => {
    const obj = await customObjectsApi.get(apiName!)
    const fieldData = await listCustomFieldDefinitions({ object_name: `custom_object_${obj.id}`, limit: 200 })
    setObject(obj)
    setFields(fieldData.items)
    setForm({
      label: obj.label,
      plural_label: obj.plural_label,
      description: obj.description ?? '',
      icon_name: obj.icon_name ?? '',
      is_active: obj.is_active,
    })
  }, [apiName])

  useEffect(() => {
    load()
      .catch(() => navigate('/admin/custom-objects'))
      .finally(() => setLoading(false))
  }, [load, navigate])

  const setF = (key: string, value: unknown) => setForm((f) => ({ ...f, [key]: value }))

  const handleSave = async (e: FormEvent) => {
    e.preventDefault()
    setSaveError(null)
    setSaveLoading(true)
    try {
      const updated = await customObjectsApi.update(apiName!, {
        label: form.label,
        plural_label: form.plural_label,
        description: form.description || null,
        icon_name: form.icon_name || null,
        is_active: form.is_active,
      })
      setObject(updated)
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
      await customObjectsApi.delete(apiName!)
      navigate('/admin/custom-objects')
    } finally {
      setDeleteLoading(false)
    }
  }

  if (loading) return <div className="text-sm text-muted-foreground">Loading…</div>
  if (!object) return null

  return (
    <div className="max-w-2xl space-y-6">
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">{object.label}</h1>
          <p className="text-sm text-muted-foreground mt-0.5">
            <span className="font-mono">{object.api_name}</span>
            {' · '}
            {object.is_active ? (
              <Badge variant="secondary">Active</Badge>
            ) : (
              <Badge variant="outline">Inactive</Badge>
            )}
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm" asChild>
            <Link to={`/objects/${object.api_name}`}>View Records</Link>
          </Button>
          <Button variant="destructive" size="sm" onClick={() => setShowDelete(true)}>
            Delete
          </Button>
        </div>
      </div>

      <form onSubmit={(e) => void handleSave(e)} className="space-y-5">
        {saveError && (
          <div className="rounded-md bg-destructive/10 border border-destructive/30 px-4 py-3 text-sm text-destructive">
            {saveError}
          </div>
        )}

        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-1.5">
            <Label htmlFor="label">Label *</Label>
            <Input id="label" required value={form.label} onChange={(e) => setF('label', e.target.value)} />
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="plural_label">Plural Label *</Label>
            <Input
              id="plural_label"
              required
              value={form.plural_label}
              onChange={(e) => setF('plural_label', e.target.value)}
            />
          </div>
        </div>

        <div className="space-y-1.5">
          <Label htmlFor="icon_name">Icon (Lucide name)</Label>
          <Input
            id="icon_name"
            value={form.icon_name}
            onChange={(e) => setF('icon_name', e.target.value)}
            placeholder="e.g. box, folder, star"
          />
        </div>

        <div className="space-y-1.5">
          <Label htmlFor="description">Description</Label>
          <Textarea
            id="description"
            value={form.description}
            onChange={(e) => setF('description', e.target.value)}
            rows={2}
          />
        </div>

        <div className="flex items-center justify-between rounded-lg border p-4">
          <div>
            <p className="text-sm font-medium">Active</p>
            <p className="text-xs text-muted-foreground">
              Inactive objects are hidden from navigation.
            </p>
          </div>
          <Switch checked={form.is_active} onCheckedChange={(v) => setF('is_active', v)} />
        </div>

        <div className="flex gap-3">
          <Button type="submit" disabled={saveLoading}>
            {saveLoading ? 'Saving…' : 'Save Changes'}
          </Button>
          <Button type="button" variant="outline" onClick={() => navigate('/admin/custom-objects')}>
            Back
          </Button>
        </div>
      </form>

      <Separator />

      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold">Custom Fields</h2>
          <Button
            size="sm"
            variant="outline"
            onClick={() => navigate(`/admin/custom-fields/new?object=custom_object_${object.id}&label=${encodeURIComponent(object.label)}`)}
          >
            + Add Field
          </Button>
        </div>
        <DataTable
          columns={FIELD_COLUMNS}
          data={fields}
          loading={false}
          total={fields.length}
          page={1}
          pageSize={200}
          onPageChange={() => undefined}
          onRowClick={(r) => navigate(`/admin/custom-fields/${r.id}`)}
          emptyMessage="No custom fields yet. Add fields to customise records for this object."
        />
      </div>

      <DeleteConfirmDialog
        open={showDelete}
        onOpenChange={setShowDelete}
        onConfirm={() => void handleDelete()}
        loading={deleteLoading}
        description={`Permanently delete the custom object "${object.label}" and all its records? This cannot be undone.`}
      />
    </div>
  )
}
