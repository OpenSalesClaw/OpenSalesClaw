import type { FormEvent } from 'react'
import { useCallback, useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import {
  deleteCustomFieldDefinition,
  getCustomFieldDefinition,
  updateCustomFieldDefinition,
} from '@/api/customFieldDefinitions'
import type { CustomFieldDefinition } from '@/api/types'
import DeleteConfirmDialog from '@/components/DeleteConfirmDialog'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Switch } from '@/components/ui/switch'
import { Textarea } from '@/components/ui/textarea'

export default function AdminCustomFieldDetailPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()

  const [definition, setDefinition] = useState<CustomFieldDefinition | null>(null)
  const [loading, setLoading] = useState(true)
  const [saveLoading, setSaveLoading] = useState(false)
  const [saveError, setSaveError] = useState<string | null>(null)
  const [showDelete, setShowDelete] = useState(false)
  const [deleteLoading, setDeleteLoading] = useState(false)
  const [picklistInput, setPicklistInput] = useState('')

  const [form, setForm] = useState({
    field_label: '',
    is_required: false,
    default_value: '',
    picklist_values: [] as string[],
    field_order: '',
    description: '',
  })

  const load = useCallback(async () => {
    const def = await getCustomFieldDefinition(Number(id))
    setDefinition(def)
    setForm({
      field_label: def.field_label ?? '',
      is_required: def.is_required,
      default_value: def.default_value ?? '',
      picklist_values: def.picklist_values ?? [],
      field_order: def.field_order != null ? String(def.field_order) : '',
      description: def.description ?? '',
    })
  }, [id])

  useEffect(() => {
    load()
      .catch(() => navigate('/admin/custom-fields'))
      .finally(() => setLoading(false))
  }, [load, navigate])

  const setF = (key: string, value: unknown) => setForm((f) => ({ ...f, [key]: value }))

  const addPicklistValue = () => {
    const val = picklistInput.trim()
    if (val && !form.picklist_values.includes(val)) setF('picklist_values', [...form.picklist_values, val])
    setPicklistInput('')
  }

  const removePicklistValue = (v: string) =>
    setF('picklist_values', form.picklist_values.filter((x) => x !== v))

  const handleSave = async (e: FormEvent) => {
    e.preventDefault()
    setSaveError(null)
    setSaveLoading(true)
    try {
      const updated = await updateCustomFieldDefinition(Number(id), {
        field_label: form.field_label || null,
        is_required: form.is_required,
        default_value: form.default_value || null,
        picklist_values: definition?.field_type === 'picklist' ? form.picklist_values : null,
        field_order: form.field_order ? Number(form.field_order) : null,
        description: form.description || null,
      })
      setDefinition(updated)
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
      await deleteCustomFieldDefinition(Number(id))
      navigate('/admin/custom-fields')
    } finally {
      setDeleteLoading(false)
    }
  }

  if (loading) return <div className="text-sm text-muted-foreground">Loading…</div>
  if (!definition) return null

  return (
    <div className="max-w-xl space-y-6">
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">{definition.field_label ?? definition.field_name}</h1>
          <p className="text-sm text-muted-foreground mt-0.5">
            <span className="font-mono">{definition.object_name}.{definition.field_name}</span>
            {' · '}
            <Badge variant="secondary">{definition.field_type}</Badge>
          </p>
        </div>
        <Button variant="destructive" size="sm" onClick={() => setShowDelete(true)}>
          Delete
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Read-only Properties</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2 text-sm">
          <div className="flex justify-between">
            <span className="text-muted-foreground">Object</span>
            <span className="font-medium">{definition.object_name}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-muted-foreground">API Name</span>
            <span className="font-mono">{definition.field_name}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-muted-foreground">Type</span>
            <Badge variant="secondary">{definition.field_type}</Badge>
          </div>
        </CardContent>
      </Card>

      <form onSubmit={(e) => void handleSave(e)} className="space-y-5">
        {saveError && (
          <div className="rounded-md bg-destructive/10 border border-destructive/30 px-4 py-3 text-sm text-destructive">
            {saveError}
          </div>
        )}

        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-1.5">
            <Label htmlFor="field_label">Label</Label>
            <Input
              id="field_label"
              value={form.field_label}
              onChange={(e) => setF('field_label', e.target.value)}
              placeholder="Human-readable label"
            />
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="field_order">Display Order</Label>
            <Input
              id="field_order"
              type="number"
              value={form.field_order}
              onChange={(e) => setF('field_order', e.target.value)}
              placeholder="1"
            />
          </div>
        </div>

        {definition.field_type === 'picklist' && (
          <div className="space-y-2">
            <Label>Picklist Values</Label>
            <div className="flex gap-2">
              <Input
                value={picklistInput}
                onChange={(e) => setPicklistInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    e.preventDefault()
                    addPicklistValue()
                  }
                }}
                placeholder="Add a value…"
              />
              <Button type="button" variant="outline" onClick={addPicklistValue}>
                Add
              </Button>
            </div>
            {form.picklist_values.length > 0 && (
              <div className="flex flex-wrap gap-1.5">
                {form.picklist_values.map((v) => (
                  <span
                    key={v}
                    className="inline-flex items-center gap-1 bg-secondary text-secondary-foreground rounded px-2 py-0.5 text-xs"
                  >
                    {v}
                    <button type="button" onClick={() => removePicklistValue(v)} className="hover:text-destructive">
                      ×
                    </button>
                  </span>
                ))}
              </div>
            )}
          </div>
        )}

        <div className="space-y-1.5">
          <Label htmlFor="default_value">Default Value</Label>
          <Input
            id="default_value"
            value={form.default_value}
            onChange={(e) => setF('default_value', e.target.value)}
            placeholder="Optional default"
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
            <p className="text-sm font-medium">Required</p>
            <p className="text-xs text-muted-foreground">Records must provide a value for this field.</p>
          </div>
          <Switch checked={form.is_required} onCheckedChange={(v) => setF('is_required', v)} />
        </div>

        <div className="flex gap-3">
          <Button type="submit" disabled={saveLoading}>
            {saveLoading ? 'Saving…' : 'Save Changes'}
          </Button>
          <Button type="button" variant="outline" onClick={() => navigate('/admin/custom-fields')}>
            Back
          </Button>
        </div>
      </form>

      <DeleteConfirmDialog
        open={showDelete}
        onOpenChange={setShowDelete}
        onConfirm={() => void handleDelete()}
        loading={deleteLoading}
        description={`Permanently delete the custom field "${definition.field_label ?? definition.field_name}"? Existing values stored in custom_fields JSON will no longer be validated.`}
      />
    </div>
  )
}
