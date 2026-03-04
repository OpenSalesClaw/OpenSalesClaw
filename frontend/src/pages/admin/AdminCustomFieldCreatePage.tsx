import type { FormEvent } from 'react'
import { useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { createCustomFieldDefinition } from '@/api/customFieldDefinitions'
import type { CustomFieldDefinitionCreate, FieldType } from '@/api/types'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Switch } from '@/components/ui/switch'
import { Textarea } from '@/components/ui/textarea'

const STANDARD_OBJECTS = [
  { label: 'Accounts', value: 'accounts' },
  { label: 'Contacts', value: 'contacts' },
  { label: 'Leads', value: 'leads' },
  { label: 'Opportunities', value: 'opportunities' },
  { label: 'Cases', value: 'cases' },
]

const FIELD_TYPES: { label: string; value: FieldType }[] = [
  { label: 'Text', value: 'text' },
  { label: 'Text Area', value: 'textarea' },
  { label: 'Number', value: 'number' },
  { label: 'Currency', value: 'currency' },
  { label: 'Percent', value: 'percent' },
  { label: 'Date', value: 'date' },
  { label: 'Date/Time', value: 'datetime' },
  { label: 'Checkbox (Boolean)', value: 'boolean' },
  { label: 'Picklist', value: 'picklist' },
  { label: 'Email', value: 'email' },
  { label: 'URL', value: 'url' },
  { label: 'Phone', value: 'phone' },
]

export default function AdminCustomFieldCreatePage() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const presetObject = searchParams.get('object') ?? ''
  const presetObjectLabel = searchParams.get('label') ?? presetObject
  const isCustomObjectPreset = presetObject.startsWith('custom_object_')

  const [form, setForm] = useState({
    object_name: presetObject,
    field_name: '',
    field_label: '',
    field_type: 'text' as FieldType,
    is_required: false,
    default_value: '',
    picklist_values: [] as string[],
    field_order: '',
    description: '',
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [picklistInput, setPicklistInput] = useState('')

  const set = (key: string, value: unknown) => setForm((f) => ({ ...f, [key]: value }))

  const addPicklistValue = () => {
    const val = picklistInput.trim()
    if (val && !form.picklist_values.includes(val)) {
      set('picklist_values', [...form.picklist_values, val])
    }
    setPicklistInput('')
  }

  const removePicklistValue = (v: string) => {
    set(
      'picklist_values',
      form.picklist_values.filter((x) => x !== v),
    )
  }

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setError(null)
    setLoading(true)
    try {
      const payload: CustomFieldDefinitionCreate = {
        object_name: form.object_name,
        field_name: form.field_name,
        field_label: form.field_label || null,
        field_type: form.field_type,
        is_required: form.is_required,
        default_value: form.default_value || null,
        picklist_values: form.field_type === 'picklist' ? form.picklist_values : null,
        field_order: form.field_order ? Number(form.field_order) : null,
        description: form.description || null,
      }
      const created = await createCustomFieldDefinition(payload)
      navigate(`/admin/custom-fields/${created.id}`)
    } catch (err: unknown) {
      const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail
      setError(typeof detail === 'string' ? detail : 'Failed to create custom field.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-xl space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">New Custom Field</h1>
        <p className="text-sm text-muted-foreground mt-0.5">Add a custom field to a standard object.</p>
      </div>

      <form onSubmit={(e) => void handleSubmit(e)} className="space-y-5">
        {error && (
          <div className="rounded-md bg-destructive/10 border border-destructive/30 px-4 py-3 text-sm text-destructive">
            {error}
          </div>
        )}

        <div className="space-y-1.5">
          <Label htmlFor="object_name">Object *</Label>
          {isCustomObjectPreset ? (
            <>
              <Input id="object_name" value={presetObjectLabel} disabled readOnly />
              <input type="hidden" value={form.object_name} />
            </>
          ) : (
            <Select value={form.object_name} onValueChange={(v) => set('object_name', v)} required>
              <SelectTrigger id="object_name">
                <SelectValue placeholder="Select object…" />
              </SelectTrigger>
              <SelectContent>
                {STANDARD_OBJECTS.map((o) => (
                  <SelectItem key={o.value} value={o.value}>
                    {o.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          )}
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-1.5">
            <Label htmlFor="field_name">API Name *</Label>
            <Input
              id="field_name"
              required
              value={form.field_name}
              onChange={(e) => set('field_name', e.target.value)}
              placeholder="my_custom_field"
            />
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="field_label">Label</Label>
            <Input
              id="field_label"
              value={form.field_label}
              onChange={(e) => set('field_label', e.target.value)}
              placeholder="My Custom Field"
            />
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-1.5">
            <Label htmlFor="field_type">Field Type *</Label>
            <Select value={form.field_type} onValueChange={(v) => set('field_type', v as FieldType)}>
              <SelectTrigger id="field_type">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {FIELD_TYPES.map((t) => (
                  <SelectItem key={t.value} value={t.value}>
                    {t.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="field_order">Display Order</Label>
            <Input
              id="field_order"
              type="number"
              value={form.field_order}
              onChange={(e) => set('field_order', e.target.value)}
              placeholder="1"
            />
          </div>
        </div>

        {form.field_type === 'picklist' && (
          <div className="space-y-2">
            <Label>Picklist Values *</Label>
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
                placeholder="Type a value and press Enter"
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
            onChange={(e) => set('default_value', e.target.value)}
            placeholder="Optional default"
          />
        </div>

        <div className="space-y-1.5">
          <Label htmlFor="description">Description</Label>
          <Textarea
            id="description"
            value={form.description}
            onChange={(e) => set('description', e.target.value)}
            rows={2}
            placeholder="Optional description"
          />
        </div>

        <div className="flex items-center justify-between rounded-lg border p-4">
          <div>
            <p className="text-sm font-medium">Required</p>
            <p className="text-xs text-muted-foreground">Records must provide a value for this field.</p>
          </div>
          <Switch
            checked={form.is_required}
            onCheckedChange={(v) => set('is_required', v)}
          />
        </div>

        <div className="flex gap-3">
          <Button type="submit" disabled={loading}>
            {loading ? 'Creating…' : 'Create Field'}
          </Button>
          <Button type="button" variant="outline" onClick={() => navigate('/admin/custom-fields')}>
            Cancel
          </Button>
        </div>
      </form>
    </div>
  )
}
