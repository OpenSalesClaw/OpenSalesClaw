import { useCallback, useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { leadsApi } from '@/api/leads'
import type { Lead, LeadUpdate } from '@/api/types'
import DeleteConfirmDialog from '@/components/DeleteConfirmDialog'
import DetailView, { type FieldDefinition } from '@/components/DetailView'
import DynamicFieldsSection from '@/components/DynamicFieldsSection'
import RecordForm from '@/components/RecordForm'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

const LEAD_STATUSES = ['New', 'Working', 'Nurturing', 'Unqualified', 'Converted']

const DETAIL_FIELDS: FieldDefinition[] = [
  { key: 'first_name', label: 'First Name' },
  { key: 'last_name', label: 'Last Name' },
  { key: 'company', label: 'Company' },
  { key: 'email', label: 'Email' },
  { key: 'phone', label: 'Phone' },
  { key: 'status', label: 'Status' },
  { key: 'lead_source', label: 'Lead Source' },
  { key: 'title', label: 'Title' },
  { key: 'industry', label: 'Industry' },
  {
    key: 'annual_revenue',
    label: 'Annual Revenue',
    format: (v) =>
      v != null
        ? new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(
            Number(v),
          )
        : '—',
  },
  { key: 'rating', label: 'Rating' },
  { key: 'is_converted', label: 'Converted' },
  { key: 'created_at', label: 'Created At' },
]

const FORM_FIELDS = [
  { key: 'last_name', label: 'Last Name', required: true },
  { key: 'first_name', label: 'First Name' },
  { key: 'company', label: 'Company' },
  { key: 'email', label: 'Email', type: 'email' as const },
  { key: 'phone', label: 'Phone', type: 'tel' as const },
  {
    key: 'status',
    label: 'Status',
    type: 'select' as const,
    options: LEAD_STATUSES.map((s) => ({ value: s, label: s })),
  },
  {
    key: 'lead_source',
    label: 'Lead Source',
    type: 'select' as const,
    options: ['Web', 'Phone Inquiry', 'Partner Referral', 'Purchased List', 'Other'].map((s) => ({
      value: s,
      label: s,
    })),
  },
  { key: 'title', label: 'Title' },
  { key: 'industry', label: 'Industry' },
]

export default function LeadDetailPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [lead, setLead] = useState<Lead | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [editing, setEditing] = useState(false)
  const [formValues, setFormValues] = useState<Record<string, string>>({})
  const [saveLoading, setSaveLoading] = useState(false)
  const [saveError, setSaveError] = useState<string | null>(null)
  const [showDelete, setShowDelete] = useState(false)
  const [deleteLoading, setDeleteLoading] = useState(false)
  const [customFields, setCustomFields] = useState<Record<string, unknown>>({})

  const load = useCallback(async () => {
    if (!id) return
    setLoading(true)
    try {
      const data = await leadsApi.get(parseInt(id, 10))
      setLead(data)
      setCustomFields(data.custom_fields ?? {})
    } catch {
      setError('Lead not found.')
    } finally {
      setLoading(false)
    }
  }, [id])

  useEffect(() => {
    void load()
  }, [load])

  const startEdit = () => {
    if (!lead) return
    setFormValues(
      Object.fromEntries(
        FORM_FIELDS.map((f) => [f.key, lead[f.key as keyof Lead] != null ? String(lead[f.key as keyof Lead]) : '']),
      ),
    )
    setCustomFields(lead.custom_fields ?? {})
    setEditing(true)
  }

  const handleSave = async () => {
    if (!id) return
    setSaveError(null)
    setSaveLoading(true)
    try {
      const payload: LeadUpdate = {
        last_name: formValues.last_name || undefined,
        first_name: formValues.first_name || null,
        company: formValues.company || null,
        email: formValues.email || null,
        phone: formValues.phone || null,
        status: formValues.status || undefined,
        lead_source: formValues.lead_source || null,
        title: formValues.title || null,
        industry: formValues.industry || null,
        custom_fields: customFields,
      }
      const updated = await leadsApi.update(parseInt(id, 10), payload)
      setLead(updated)
      setCustomFields(updated.custom_fields ?? {})
      setEditing(false)
    } catch (err: unknown) {
      const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail
      setSaveError(typeof detail === 'string' ? detail : 'Failed to save changes.')
    } finally {
      setSaveLoading(false)
    }
  }

  const handleDelete = async () => {
    if (!id) return
    setDeleteLoading(true)
    try {
      await leadsApi.delete(parseInt(id, 10))
      navigate('/leads')
    } finally {
      setDeleteLoading(false)
    }
  }

  if (loading) return <p className="p-4 text-muted-foreground">Loading…</p>
  if (error || !lead) return <p className="p-4 text-destructive">{error ?? 'Not found.'}</p>

  const title = `${lead.first_name ?? ''} ${lead.last_name}`.trim()

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Button variant="ghost" size="sm" onClick={() => navigate('/leads')}>
            ← Leads
          </Button>
          <h2 className="text-2xl font-semibold tracking-tight">{title}</h2>
        </div>
        {!editing && (
          <div className="flex gap-2">
            <Button variant="outline" onClick={startEdit}>
              Edit
            </Button>
            <Button variant="destructive" onClick={() => setShowDelete(true)}>
              Delete
            </Button>
          </div>
        )}
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Lead Details</CardTitle>
        </CardHeader>
        <CardContent>
          {editing ? (
            <>
              <RecordForm
                fields={FORM_FIELDS}
                values={formValues}
                onChange={(k, v) => setFormValues((p) => ({ ...p, [k]: v }))}
                onSubmit={handleSave}
                onCancel={() => { setEditing(false); setCustomFields(lead.custom_fields ?? {}) }}
                submitLabel="Save Changes"
                loading={saveLoading}
                error={saveError}
              />
              <DynamicFieldsSection
                objectName="leads"
                values={customFields}
                onChange={setCustomFields}
              />
            </>
          ) : (
            <>
              <DetailView record={lead as unknown as Record<string, unknown>} fields={DETAIL_FIELDS} />
              <DynamicFieldsSection
                objectName="leads"
                values={lead.custom_fields ?? {}}
                onChange={() => undefined}
                disabled
              />
            </>
          )}
        </CardContent>
      </Card>

      <DeleteConfirmDialog
        open={showDelete}
        onOpenChange={setShowDelete}
        onConfirm={() => void handleDelete()}
        loading={deleteLoading}
        title="Delete Lead"
        description={`Are you sure you want to delete ${title}?`}
      />
    </div>
  )
}
