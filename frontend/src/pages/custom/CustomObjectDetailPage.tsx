import type { FormEvent } from 'react'
import { useCallback, useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { customObjectsApi } from '@/api/customObjects'
import type { CustomObject, CustomObjectRecord } from '@/api/types'
import DeleteConfirmDialog from '@/components/DeleteConfirmDialog'
import DynamicFieldsSection from '@/components/DynamicFieldsSection'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Separator } from '@/components/ui/separator'

export default function CustomObjectDetailPage() {
  const { apiName, id } = useParams<{ apiName: string; id: string }>()
  const navigate = useNavigate()

  const [object, setObject] = useState<CustomObject | null>(null)
  const [record, setRecord] = useState<CustomObjectRecord | null>(null)
  const [loading, setLoading] = useState(true)
  const [saveLoading, setSaveLoading] = useState(false)
  const [saveError, setSaveError] = useState<string | null>(null)
  const [showDelete, setShowDelete] = useState(false)
  const [deleteLoading, setDeleteLoading] = useState(false)

  const [form, setForm] = useState<{ name: string; data: Record<string, unknown> }>({
    name: '',
    data: {},
  })

  const load = useCallback(async () => {
    const [obj, rec] = await Promise.all([
      customObjectsApi.get(apiName!),
      customObjectsApi.getRecord(apiName!, Number(id)),
    ])
    setObject(obj)
    setRecord(rec)
    setForm({ name: rec.name ?? '', data: rec.data })
  }, [apiName, id])

  useEffect(() => {
    load()
      .catch(() => navigate(`/objects/${apiName}`))
      .finally(() => setLoading(false))
  }, [load, navigate, apiName])

  const handleSave = async (e: FormEvent) => {
    e.preventDefault()
    setSaveError(null)
    setSaveLoading(true)
    try {
      const updated = await customObjectsApi.updateRecord(apiName!, Number(id), {
        name: form.name || null,
        data: form.data,
      })
      setRecord(updated)
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
      await customObjectsApi.deleteRecord(apiName!, Number(id))
      navigate(`/objects/${apiName}`)
    } finally {
      setDeleteLoading(false)
    }
  }

  if (loading) return <div className="text-sm text-muted-foreground">Loading…</div>
  if (!object || !record) return null

  return (
    <div className="max-w-xl space-y-6">
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">{record.name ?? `${object.label} #${record.id}`}</h1>
          <p className="text-sm text-muted-foreground mt-0.5">{object.label} · #{record.id}</p>
        </div>
        <Button variant="destructive" size="sm" onClick={() => setShowDelete(true)}>
          Delete
        </Button>
      </div>

      <form onSubmit={(e) => void handleSave(e)} className="space-y-5">
        {saveError && (
          <div className="rounded-md bg-destructive/10 border border-destructive/30 px-4 py-3 text-sm text-destructive">
            {saveError}
          </div>
        )}

        <div className="space-y-1.5">
          <Label htmlFor="name">Name</Label>
          <Input
            id="name"
            value={form.name}
            onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
            placeholder={`${object.label} name`}
          />
        </div>

        <DynamicFieldsSection
          objectName={`custom_object_${object.id}`}
          values={form.data}
          onChange={(updated) => setForm((f) => ({ ...f, data: updated }))}
          showHeading={true}
        />

        <Separator />

        <div className="grid grid-cols-2 gap-4 text-sm text-muted-foreground">
          <div>
            <span className="font-medium">Created</span>
            <p>{new Date(record.created_at).toLocaleString()}</p>
          </div>
          <div>
            <span className="font-medium">Updated</span>
            <p>{new Date(record.updated_at).toLocaleString()}</p>
          </div>
        </div>

        <div className="flex gap-3">
          <Button type="submit" disabled={saveLoading}>
            {saveLoading ? 'Saving…' : 'Save Changes'}
          </Button>
          <Button type="button" variant="outline" onClick={() => navigate(`/objects/${apiName}`)}>
            Back to list
          </Button>
        </div>
      </form>

      <DeleteConfirmDialog
        open={showDelete}
        onOpenChange={setShowDelete}
        onConfirm={() => void handleDelete()}
        loading={deleteLoading}
        description={`Delete this ${object.label} record? This action cannot be undone.`}
      />
    </div>
  )
}
