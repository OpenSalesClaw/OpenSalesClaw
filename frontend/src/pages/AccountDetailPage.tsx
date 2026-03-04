import { useCallback, useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { accountsApi } from '@/api/accounts'
import { casesApi } from '@/api/cases'
import { contactsApi } from '@/api/contacts'
import { opportunitiesApi } from '@/api/opportunities'
import type { Account, AccountUpdate, Case, Contact, Opportunity } from '@/api/types'
import DataTable, { type Column } from '@/components/DataTable'
import DeleteConfirmDialog from '@/components/DeleteConfirmDialog'
import DetailView, { type FieldDefinition } from '@/components/DetailView'
import DynamicFieldsSection from '@/components/DynamicFieldsSection'
import RecordForm from '@/components/RecordForm'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

const DETAIL_FIELDS: FieldDefinition[] = [
  { key: 'name', label: 'Name' },
  { key: 'type', label: 'Type' },
  { key: 'industry', label: 'Industry' },
  { key: 'phone', label: 'Phone' },
  { key: 'website', label: 'Website' },
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
  { key: 'number_of_employees', label: 'Employees' },
  { key: 'billing_city', label: 'Billing City' },
  { key: 'billing_country', label: 'Billing Country' },
  { key: 'description', label: 'Description' },
  { key: 'created_at', label: 'Created At' },
]

const EDIT_FIELDS = [
  { key: 'name', label: 'Name', required: true },
  {
    key: 'type',
    label: 'Type',
    type: 'select' as const,
    options: ['Customer', 'Partner', 'Prospect', 'Vendor', 'Other'].map((s) => ({ value: s, label: s })),
  },
  { key: 'industry', label: 'Industry' },
  { key: 'phone', label: 'Phone', type: 'tel' as const },
  { key: 'website', label: 'Website', type: 'url' as const },
  { key: 'annual_revenue', label: 'Annual Revenue', type: 'number' as const },
  { key: 'number_of_employees', label: 'Employees', type: 'number' as const },
  { key: 'billing_city', label: 'Billing City' },
  { key: 'billing_country', label: 'Billing Country' },
  { key: 'description', label: 'Description', type: 'textarea' as const },
]

const CONTACT_COLS: Column<Contact>[] = [
  { key: 'name', label: 'Name', render: (r) => `${r.first_name ?? ''} ${r.last_name}`.trim() },
  { key: 'email', label: 'Email' },
  { key: 'title', label: 'Title' },
  { key: 'phone', label: 'Phone' },
]

const OPP_COLS: Column<Opportunity>[] = [
  { key: 'name', label: 'Name' },
  {
    key: 'stage',
    label: 'Stage',
    render: (r) => (
      <Badge variant={r.is_won ? 'secondary' : r.stage === 'Closed Lost' ? 'destructive' : 'outline'}>
        {r.stage}
      </Badge>
    ),
  },
  {
    key: 'amount',
    label: 'Amount',
    render: (r) =>
      r.amount != null
        ? new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(
            r.amount,
          )
        : '—',
  },
  { key: 'close_date', label: 'Close Date' },
]

const CASE_COLS: Column<Case>[] = [
  { key: 'case_number', label: 'Case #' },
  { key: 'subject', label: 'Subject' },
  {
    key: 'status',
    label: 'Status',
    render: (r) => (
      <Badge variant={r.status === 'Closed' ? 'secondary' : 'outline'}>{r.status}</Badge>
    ),
  },
  { key: 'priority', label: 'Priority' },
]

export default function AccountDetailPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()

  const [account, setAccount] = useState<Account | null>(null)
  const [contacts, setContacts] = useState<Contact[]>([])
  const [opportunities, setOpportunities] = useState<Opportunity[]>([])
  const [cases, setCases] = useState<Case[]>([])

  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [editing, setEditing] = useState(false)
  const [formValues, setFormValues] = useState<Record<string, string>>({})
  const [customFields, setCustomFields] = useState<Record<string, unknown>>({})
  const [saveLoading, setSaveLoading] = useState(false)
  const [saveError, setSaveError] = useState<string | null>(null)
  const [showDelete, setShowDelete] = useState(false)
  const [deleteLoading, setDeleteLoading] = useState(false)

  const load = useCallback(async () => {
    if (!id) return
    const numId = parseInt(id, 10)
    setLoading(true)
    try {
      const [acct, conts, opps, css] = await Promise.all([
        accountsApi.get(numId),
        contactsApi.list({ account_id: numId, limit: 50 }),
        opportunitiesApi.list({ account_id: numId, limit: 50 }),
        casesApi.list({ account_id: numId, limit: 50 }),
      ])
      setAccount(acct)
      setCustomFields(acct.custom_fields ?? {})
      setContacts(conts.items)
      setOpportunities(opps.items)
      setCases(css.items)
    } catch {
      setError('Account not found.')
    } finally {
      setLoading(false)
    }
  }, [id])

  useEffect(() => {
    void load()
  }, [load])

  const startEdit = () => {
    if (!account) return
    setFormValues(
      Object.fromEntries(
        EDIT_FIELDS.map((f) => [
          f.key,
          account[f.key as keyof Account] != null ? String(account[f.key as keyof Account]) : '',
        ]),
      ),
    )
    setCustomFields(account.custom_fields ?? {})
    setEditing(true)
  }

  const handleSave = async () => {
    if (!id) return
    setSaveError(null)
    setSaveLoading(true)
    try {
      const payload: AccountUpdate = {
        name: formValues.name || undefined,
        type: formValues.type || null,
        industry: formValues.industry || null,
        phone: formValues.phone || null,
        website: formValues.website || null,
        annual_revenue: formValues.annual_revenue ? parseFloat(formValues.annual_revenue) : null,
        number_of_employees: formValues.number_of_employees
          ? parseInt(formValues.number_of_employees, 10)
          : null,
        billing_city: formValues.billing_city || null,
        billing_country: formValues.billing_country || null,
        description: formValues.description || null,
        custom_fields: customFields,
      }
      const updated = await accountsApi.update(parseInt(id, 10), payload)
      setAccount(updated)
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
      await accountsApi.delete(parseInt(id, 10))
      navigate('/accounts')
    } finally {
      setDeleteLoading(false)
    }
  }

  if (loading) return <p className="p-4 text-muted-foreground">Loading…</p>
  if (error || !account) return <p className="p-4 text-destructive">{error ?? 'Not found.'}</p>

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Button variant="ghost" size="sm" onClick={() => navigate('/accounts')}>
            ← Accounts
          </Button>
          <h2 className="text-2xl font-semibold tracking-tight">{account.name}</h2>
          {account.type && <Badge variant="outline">{account.type}</Badge>}
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

      {/* Account details */}
      <Card>
        <CardHeader>
          <CardTitle>Account Details</CardTitle>
        </CardHeader>
        <CardContent>
          {editing ? (
            <>
              <RecordForm
                fields={EDIT_FIELDS}
                values={formValues}
                onChange={(k, v) => setFormValues((p) => ({ ...p, [k]: v }))}
                onSubmit={handleSave}
                onCancel={() => { setEditing(false); setCustomFields(account.custom_fields ?? {}) }}
                submitLabel="Save Changes"
                loading={saveLoading}
                error={saveError}
              />
              <DynamicFieldsSection
                objectName="accounts"
                values={customFields}
                onChange={setCustomFields}
              />
            </>
          ) : (
            <>
              <DetailView record={account as unknown as Record<string, unknown>} fields={DETAIL_FIELDS} />
              <DynamicFieldsSection
                objectName="accounts"
                values={account.custom_fields ?? {}}
                onChange={() => undefined}
                disabled
              />
            </>
          )}
        </CardContent>
      </Card>

      {/* Related Contacts */}
      <Card>
        <CardHeader>
          <CardTitle>Contacts ({contacts.length})</CardTitle>
        </CardHeader>
        <CardContent>
          <DataTable
            columns={CONTACT_COLS}
            data={contacts}
            total={contacts.length}
            page={1}
            pageSize={50}
            onPageChange={() => undefined}
            onRowClick={(r) => navigate(`/contacts/${r.id}`)}
          />
        </CardContent>
      </Card>

      {/* Related Opportunities */}
      <Card>
        <CardHeader>
          <CardTitle>Opportunities ({opportunities.length})</CardTitle>
        </CardHeader>
        <CardContent>
          <DataTable
            columns={OPP_COLS}
            data={opportunities}
            total={opportunities.length}
            page={1}
            pageSize={50}
            onPageChange={() => undefined}
            onRowClick={(r) => navigate(`/opportunities/${r.id}`)}
          />
        </CardContent>
      </Card>

      {/* Related Cases */}
      <Card>
        <CardHeader>
          <CardTitle>Cases ({cases.length})</CardTitle>
        </CardHeader>
        <CardContent>
          <DataTable
            columns={CASE_COLS}
            data={cases}
            total={cases.length}
            page={1}
            pageSize={50}
            onPageChange={() => undefined}
            onRowClick={(r) => navigate(`/cases/${r.id}`)}
          />
        </CardContent>
      </Card>

      <DeleteConfirmDialog
        open={showDelete}
        onOpenChange={setShowDelete}
        onConfirm={() => void handleDelete()}
        loading={deleteLoading}
        title="Delete Account"
        description={`Delete "${account.name}"? All related records will remain but will no longer reference this account.`}
      />
    </div>
  )
}
