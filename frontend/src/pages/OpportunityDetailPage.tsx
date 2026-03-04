import { useCallback, useEffect, useMemo, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { accountsApi } from '@/api/accounts'
import { opportunitiesApi } from '@/api/opportunities'
import type { Account, Opportunity, OpportunityUpdate } from '@/api/types'
import DeleteConfirmDialog from '@/components/DeleteConfirmDialog'
import DetailView, { type FieldDefinition } from '@/components/DetailView'
import RecordForm from '@/components/RecordForm'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

const STAGES = [
  'Prospecting', 'Qualification', 'Needs Analysis', 'Value Proposition',
  'Id. Decision Makers', 'Perception Analysis', 'Proposal/Price Quote',
  'Negotiation/Review', 'Closed Won', 'Closed Lost',
]

export default function OpportunityDetailPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [opp, setOpp] = useState<Opportunity | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [editing, setEditing] = useState(false)
  const [formValues, setFormValues] = useState<Record<string, string>>({})
  const [saveLoading, setSaveLoading] = useState(false)
  const [saveError, setSaveError] = useState<string | null>(null)
  const [showDelete, setShowDelete] = useState(false)
  const [deleteLoading, setDeleteLoading] = useState(false)
  const [accounts, setAccounts] = useState<Account[]>([])

  useEffect(() => {
    void accountsApi.list({ limit: 200 }).then((res) => setAccounts(res.items))
  }, [])

  const accountMap = useMemo(() => new Map(accounts.map((a) => [a.id, a.name])), [accounts])
  const accountOptions = useMemo(() => accounts.map((a) => ({ value: String(a.id), label: a.name })), [accounts])

  const detailFields = useMemo<FieldDefinition[]>(
    () => [
      { key: 'name', label: 'Name' },
      {
        key: 'account_id',
        label: 'Account',
        format: (v) => (v != null ? (accountMap.get(Number(v)) ?? String(v)) : '—'),
      },
      { key: 'contact_id', label: 'Contact ID' },
      { key: 'stage', label: 'Stage' },
      {
        key: 'amount',
        label: 'Amount',
        format: (v) =>
          v != null
            ? new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(Number(v))
            : '—',
      },
      { key: 'probability', label: 'Probability (%)', format: (v) => (v != null ? `${String(v)}%` : '—') },
      { key: 'close_date', label: 'Close Date' },
      { key: 'lead_source', label: 'Lead Source' },
      { key: 'next_step', label: 'Next Step' },
      { key: 'description', label: 'Description' },
      { key: 'is_won', label: 'Won' },
      { key: 'is_closed', label: 'Closed' },
      { key: 'created_at', label: 'Created At' },
    ],
    [accountMap],
  )

  const formFields = useMemo(
    () => [
      { key: 'name', label: 'Name', required: true },
      { key: 'close_date', label: 'Close Date', required: true, type: 'date' as const },
      { key: 'stage', label: 'Stage', type: 'select' as const, options: STAGES.map((s) => ({ value: s, label: s })) },
      { key: 'amount', label: 'Amount', type: 'number' as const },
      { key: 'probability', label: 'Probability (%)', type: 'number' as const },
      { key: 'account_id', label: 'Account', type: 'combobox' as const, options: accountOptions, placeholder: 'Search accounts…' },
      { key: 'next_step', label: 'Next Step' },
      { key: 'description', label: 'Description', type: 'textarea' as const },
    ],
    [accountOptions],
  )

  const load = useCallback(async () => {
    if (!id) return
    setLoading(true)
    try {
      const data = await opportunitiesApi.get(parseInt(id, 10))
      setOpp(data)
    } catch {
      setError('Opportunity not found.')
    } finally {
      setLoading(false)
    }
  }, [id])

  useEffect(() => { void load() }, [load])

  const startEdit = () => {
    if (!opp) return
    setFormValues(Object.fromEntries(
      formFields.map((f) => [f.key, opp[f.key as keyof Opportunity] != null ? String(opp[f.key as keyof Opportunity]) : ''])
    ))
    setEditing(true)
  }

  const handleSave = async () => {
    if (!id) return
    setSaveError(null); setSaveLoading(true)
    try {
      const payload: OpportunityUpdate = {
        name: formValues.name || undefined,
        close_date: formValues.close_date || undefined,
        stage: formValues.stage || undefined,
        amount: formValues.amount ? parseFloat(formValues.amount) : null,
        probability: formValues.probability ? parseInt(formValues.probability, 10) : null,
        account_id: formValues.account_id ? parseInt(formValues.account_id, 10) : null,
        next_step: formValues.next_step || null,
        description: formValues.description || null,
      }
      const updated = await opportunitiesApi.update(parseInt(id, 10), payload)
      setOpp(updated); setEditing(false)
    } catch {
      setSaveError('Failed to save changes.')
    } finally {
      setSaveLoading(false)
    }
  }

  const handleDelete = async () => {
    if (!id) return
    setDeleteLoading(true)
    try { await opportunitiesApi.delete(parseInt(id, 10)); navigate('/opportunities') }
    finally { setDeleteLoading(false) }
  }

  if (loading) return <p className="p-4 text-muted-foreground">Loading…</p>
  if (error || !opp) return <p className="p-4 text-destructive">{error ?? 'Not found.'}</p>

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Button variant="ghost" size="sm" onClick={() => navigate('/opportunities')}>← Opportunities</Button>
          <h2 className="text-2xl font-semibold tracking-tight">{opp.name}</h2>
          <Badge variant={opp.is_won ? 'secondary' : opp.stage === 'Closed Lost' ? 'destructive' : 'outline'}>
            {opp.stage}
          </Badge>
        </div>
        {!editing && (
          <div className="flex gap-2">
            <Button variant="outline" onClick={startEdit}>Edit</Button>
            <Button variant="destructive" onClick={() => setShowDelete(true)}>Delete</Button>
          </div>
        )}
      </div>

      <Card>
        <CardHeader><CardTitle>Opportunity Details</CardTitle></CardHeader>
        <CardContent>
          {editing ? (
            <RecordForm
              fields={formFields}
              values={formValues}
              onChange={(k, v) => setFormValues((p) => ({ ...p, [k]: v }))}
              onSubmit={handleSave}
              onCancel={() => setEditing(false)}
              submitLabel="Save Changes"
              loading={saveLoading}
              error={saveError}
            />
          ) : (
            <DetailView record={opp as unknown as Record<string, unknown>} fields={detailFields} />
          )}
        </CardContent>
      </Card>

      <DeleteConfirmDialog
        open={showDelete}
        onOpenChange={setShowDelete}
        onConfirm={() => void handleDelete()}
        loading={deleteLoading}
        title="Delete Opportunity"
        description={`Delete "${opp.name}"? This cannot be undone.`}
      />
    </div>
  )
}
