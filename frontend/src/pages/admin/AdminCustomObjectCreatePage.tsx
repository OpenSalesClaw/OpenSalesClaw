import type { FormEvent } from 'react'
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { customObjectsApi } from '@/api/customObjects'
import type { CustomObjectCreate } from '@/api/types'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Switch } from '@/components/ui/switch'
import { Textarea } from '@/components/ui/textarea'

export default function AdminCustomObjectCreatePage() {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const [form, setForm] = useState({
    api_name: '',
    label: '',
    plural_label: '',
    description: '',
    icon_name: '',
    is_active: true,
  })

  const set = (key: string, value: unknown) => setForm((f) => ({ ...f, [key]: value }))

  // Auto-suggest plural label and api_name from label
  const handleLabelChange = (label: string) => {
    setForm((f) => ({
      ...f,
      label,
      plural_label: f.plural_label || label ? f.plural_label || `${label}s` : '',
      api_name:
        f.api_name ||
        label
          .toLowerCase()
          .replace(/\s+/g, '_')
          .replace(/[^a-z0-9_]/g, ''),
    }))
  }

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setError(null)
    setLoading(true)
    try {
      const payload: CustomObjectCreate = {
        api_name: form.api_name,
        label: form.label,
        plural_label: form.plural_label,
        description: form.description || null,
        icon_name: form.icon_name || null,
        is_active: form.is_active,
      }
      const created = await customObjectsApi.create(payload)
      navigate(`/admin/custom-objects/${created.api_name}`)
    } catch (err: unknown) {
      const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail
      setError(typeof detail === 'string' ? detail : 'Failed to create custom object.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-xl space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">New Custom Object</h1>
        <p className="text-sm text-muted-foreground mt-0.5">
          Define a new custom object. Once created, you can add custom fields and create records.
        </p>
      </div>

      <form onSubmit={(e) => void handleSubmit(e)} className="space-y-5">
        {error && (
          <div className="rounded-md bg-destructive/10 border border-destructive/30 px-4 py-3 text-sm text-destructive">
            {error}
          </div>
        )}

        <div className="space-y-1.5">
          <Label htmlFor="label">Label *</Label>
          <Input
            id="label"
            required
            value={form.label}
            onChange={(e) => handleLabelChange(e.target.value)}
            placeholder="e.g. Project"
          />
          <p className="text-xs text-muted-foreground">The singular human-readable name for this object.</p>
        </div>

        <div className="space-y-1.5">
          <Label htmlFor="plural_label">Plural Label *</Label>
          <Input
            id="plural_label"
            required
            value={form.plural_label}
            onChange={(e) => set('plural_label', e.target.value)}
            placeholder="e.g. Projects"
          />
        </div>

        <div className="space-y-1.5">
          <Label htmlFor="api_name">API Name *</Label>
          <Input
            id="api_name"
            required
            value={form.api_name}
            onChange={(e) => set('api_name', e.target.value)}
            placeholder="e.g. project"
            pattern="[a-z][a-z0-9_]*"
            title="Lowercase letters, digits, and underscores. Must start with a letter."
          />
          <p className="text-xs text-muted-foreground">
            Used in API URLs (e.g. <span className="font-mono">/api/custom-objects/project/records</span>).
            Cannot be changed after creation.
          </p>
        </div>

        <div className="space-y-1.5">
          <Label htmlFor="icon_name">Icon (Lucide name)</Label>
          <Input
            id="icon_name"
            value={form.icon_name}
            onChange={(e) => set('icon_name', e.target.value)}
            placeholder="e.g. box, folder, star"
          />
          <p className="text-xs text-muted-foreground">
            Optional{' '}
            <a
              href="https://lucide.dev/icons/"
              target="_blank"
              rel="noopener noreferrer"
              className="underline hover:text-foreground"
            >
              Lucide icon
            </a>{' '}
            name for the sidebar.
          </p>
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
            <p className="text-sm font-medium">Active</p>
            <p className="text-xs text-muted-foreground">Inactive objects are hidden from navigation and cannot receive new records.</p>
          </div>
          <Switch checked={form.is_active} onCheckedChange={(v) => set('is_active', v)} />
        </div>

        <div className="flex gap-3">
          <Button type="submit" disabled={loading}>
            {loading ? 'Creating…' : 'Create Object'}
          </Button>
          <Button type="button" variant="outline" onClick={() => navigate('/admin/custom-objects')}>
            Cancel
          </Button>
        </div>
      </form>
    </div>
  )
}
