import { useCallback, useEffect, useMemo, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { accountsApi } from '@/api/accounts'
import { casesApi } from '@/api/cases'
import type { Account, Case, CaseUpdate } from '@/api/types'
import DeleteConfirmDialog from '@/components/DeleteConfirmDialog'
import DetailView, { type FieldDefinition } from '@/components/DetailView'
import DynamicFieldsSection from '@/components/DynamicFieldsSection'
import RecordForm from '@/components/RecordForm'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

const STATUSES = ['New', 'Open', 'In Progress', 'Working', 'Escalated', 'Closed']
const PRIORITIES = ['Low', 'Medium', 'High', 'Critical']

function priorityVariant(p: string): 'default' | 'secondary' | 'destructive' | 'outline' {
  if (p === 'Critical') return 'destructive'
  if (p === 'High') return 'default'
  if (p === 'Medium') return 'secondary'
  return 'outline'
}

export default function CaseDetailPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [caseRecord, setCaseRecord] = useState<Case | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [editing, setEditing] = useState(false)
  const [formValues, setFormValues] = useState<Record<string, string>>({})
  const [saveLoading, setSaveLoading] = useState(false)
  const [saveError, setSaveError] = useState<string | null>(null)
  const [showDelete, setShowDelete] = useState(false)
  const [deleteLoading, setDeleteLoading] = useState(false)
  const [accounts, setAccounts] = useState<Account[]>([])
  const [customFields, setCustomFields] = useState<Record<string, unknown>>({})

  useEffect(() => {
    void accountsApi.list({ limit: 200 }).then((res) => setAccounts(res.items))
  }, [])

  const accountMap = useMemo(() => new Map(accounts.map((a) => [a.id, a.name])), [accounts])
  const accountOptions = useMemo(() => accounts.map((a) => ({ value: String(a.id), label: a.name })), [accounts])

  const detailFields = useMemo<FieldDefinition[]>(
    () => [
      { key: 'case_number', label: 'Case #' },
      { key: 'subject', label: 'Subject' },
      { key: 'status', label: 'Status' },
      { key: 'priority', label: 'Priority' },
      { key: 'origin', label: 'Origin' },
      { key: 'type', label: 'Type' },
      { key: 'reason', label: 'Reason' },
      {
        key: 'account_id',
        label: 'Account',
        format: (v) => (v != null ? (accountMap.get(Number(v)) ?? String(v)) : '—'),
      },
      { key: 'contact_id', label: 'Contact ID' },
      { key: 'description', label: 'Description' },
      { key: 'closed_at', label: 'Closed At' },
      { key: 'created_at', label: 'Created At' },
    ],
    [accountMap],
  )

  const formFields = useMemo(
    () => [
      { key: 'subject', label: 'Subject', required: true },
      { key: 'description', label: 'Description', type: 'textarea' as const },
      { key: 'status', label: 'Status', type: 'select' as const, options: STATUSES.map((s) => ({ value: s, label: s })) },
      { key: 'priority', label: 'Priority', type: 'select' as const, options: PRIORITIES.map((s) => ({ value: s, label: s })) },
      { key: 'account_id', label: 'Account', type: 'combobox' as const, options: accountOptions, placeholder: 'Search accounts…' },
      { key: 'reason', label: 'Reason' },
    ],
    [accountOptions],
  )

  const load = useCallback(async () => {
    if (!id) return
    setLoading(true)
    try {
      const data = await casesApi.get(parseInt(id, 10))
      setCaseRecord(data)
      setCustomFields(data.custom_fields ?? {})
    } catch {
      setError('Case not found.')
    } finally {
      setLoading(false)
    }
  }, [id])

  useEffect(() => { void load() }, [load])

  const startEdit = () => {
    if (!caseRecord) return
    setFormValues(Object.fromEntries(
      formFields.map((f) => [f.key, caseRecord[f.key as keyof Case] != null ? String(caseRecord[f.key as keyof Case]) : ''])
    ))
    setCustomFields(caseRecord.custom_fields ?? {})
    setEditing(true)
  }

  const handleSave = async () => {
    if (!id) return
    setSaveError(null); setSaveLoading(true)
    try {
      const payload: CaseUpdate = {
        subject: formValues.subject || undefined,
        description: formValues.description || null,
        status: formValues.status || undefined,
        priority: formValues.priority || undefined,
        account_id: formValues.account_id ? parseInt(formValues.account_id, 10) : null,
        reason: formValues.reason || null,
        custom_fields: customFields,
      }
      const updated = await casesApi.update(parseInt(id, 10), payload)
      setCaseRecord(updated); setCustomFields(updated.custom_fields ?? {}); setEditing(false)
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
    try { await casesApi.delete(parseInt(id, 10)); navigate('/cases') }
    finally { setDeleteLoading(false) }
  }

  if (loading) return <p className="p-4 text-muted-foreground">Loading…</p>
  if (error || !caseRecord) return <p className="p-4 text-destructive">{error ?? 'Not found.'}</p>

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Button variant="ghost" size="sm" onClick={() => navigate('/cases')}>← Cases</Button>
          <h2 className="text-2xl font-semibold tracking-tight">
            {caseRecord.case_number ?? `Case #${caseRecord.id}`}: {caseRecord.subject}
          </h2>
          <Badge variant={priorityVariant(caseRecord.priority)}>{caseRecord.priority}</Badge>
          <Badge variant={caseRecord.status === 'Closed' ? 'secondary' : 'outline'}>{caseRecord.status}</Badge>
        </div>
        {!editing && (
          <div className="flex gap-2">
            <Button variant="outline" onClick={startEdit}>Edit</Button>
            <Button variant="destructive" onClick={() => setShowDelete(true)}>Delete</Button>
          </div>
        )}
      </div>

      <Card>
        <CardHeader><CardTitle>Case Details</CardTitle></CardHeader>
        <CardContent>
          {editing ? (
            <>
              <RecordForm
                fields={formFields}
                values={formValues}
                onChange={(k, v) => setFormValues((p) => ({ ...p, [k]: v }))}
                onSubmit={handleSave}
                onCancel={() => { setEditing(false); setCustomFields(caseRecord.custom_fields ?? {}) }}
                submitLabel="Save Changes"
                loading={saveLoading}
                error={saveError}
              />
              <DynamicFieldsSection
                objectName="cases"
                values={customFields}
                onChange={setCustomFields}
              />
            </>
          ) : (
            <>
              <DetailView record={caseRecord as unknown as Record<string, unknown>} fields={detailFields} />
              <DynamicFieldsSection
                objectName="cases"
                values={caseRecord.custom_fields ?? {}}
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
        title="Delete Case"
        description={`Delete this case? This cannot be undone.`}
      />
    </div>
  )
}
