import type { FormEvent } from 'react'
import { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { customObjectsApi } from '@/api/customObjects'
import type { CustomObject, CustomObjectRecordCreate } from '@/api/types'
import DynamicFieldsSection from '@/components/DynamicFieldsSection'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'

export default function CustomObjectCreatePage() {
  const { apiName } = useParams<{ apiName: string }>()
  const navigate = useNavigate()

  const [object, setObject] = useState<CustomObject | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [form, setForm] = useState<{ name: string; data: Record<string, unknown> }>({
    name: '',
    data: {},
  })

  useEffect(() => {
    customObjectsApi.get(apiName!).then(setObject).catch(() => navigate('/'))
  }, [apiName, navigate])

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setError(null)
    setLoading(true)
    try {
      const payload: CustomObjectRecordCreate = {
        name: form.name || null,
        data: form.data,
      }
      const record = await customObjectsApi.createRecord(apiName!, payload)
      navigate(`/objects/${apiName}/${record.id}`)
    } catch (err: unknown) {
      const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail
      setError(typeof detail === 'string' ? detail : 'Failed to create record.')
    } finally {
      setLoading(false)
    }
  }

  if (!object) return <div className="text-sm text-muted-foreground">Loading…</div>

  return (
    <div className="max-w-xl space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">New {object.label}</h1>
      </div>

      <form onSubmit={(e) => void handleSubmit(e)} className="space-y-5">
        {error && (
          <div className="rounded-md bg-destructive/10 border border-destructive/30 px-4 py-3 text-sm text-destructive">
            {error}
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
          showHeading={false}
        />

        <div className="flex gap-3 pt-2">
          <Button type="submit" disabled={loading}>
            {loading ? 'Creating…' : `Create ${object.label}`}
          </Button>
          <Button type="button" variant="outline" onClick={() => navigate(`/objects/${apiName}`)}>
            Cancel
          </Button>
        </div>
      </form>
    </div>
  )
}
