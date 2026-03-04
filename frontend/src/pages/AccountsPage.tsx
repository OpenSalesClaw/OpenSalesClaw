import { useCallback, useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { accountsApi } from '@/api/accounts'
import type { Account, AccountCreate } from '@/api/types'
import DataTable, { type Column } from '@/components/DataTable'
import DeleteConfirmDialog from '@/components/DeleteConfirmDialog'
import FilterBar from '@/components/FilterBar'
import RecordForm from '@/components/RecordForm'
import { Button } from '@/components/ui/button'
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog'

const PAGE_SIZE = 20

const ACCOUNT_TYPES = ['Customer', 'Partner', 'Prospect', 'Vendor', 'Other']

const COLUMNS: Column<Account>[] = [
  { key: 'name', label: 'Name' },
  { key: 'type', label: 'Type' },
  { key: 'industry', label: 'Industry' },
  { key: 'phone', label: 'Phone' },
  { key: 'billing_city', label: 'City' },
  { key: 'billing_country', label: 'Country' },
]

const FORM_FIELDS = [
  { key: 'name', label: 'Name', required: true, placeholder: 'Acme Corp' },
  {
    key: 'type',
    label: 'Type',
    type: 'select' as const,
    options: ACCOUNT_TYPES.map((t) => ({ value: t, label: t })),
  },
  { key: 'industry', label: 'Industry', placeholder: 'Technology' },
  { key: 'phone', label: 'Phone', type: 'tel' as const, placeholder: '+1 555-000-0000' },
  { key: 'website', label: 'Website', type: 'url' as const, placeholder: 'https://example.com' },
]

export default function AccountsPage() {
  const navigate = useNavigate()
  const [accounts, setAccounts] = useState<Account[]>([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [loading, setLoading] = useState(false)
  const [filterValues, setFilterValues] = useState<Record<string, string>>({})
  const [showCreate, setShowCreate] = useState(false)
  const [formValues, setFormValues] = useState<Record<string, string>>({})
  const [formError, setFormError] = useState<string | null>(null)
  const [formLoading, setFormLoading] = useState(false)
  const [deleteId, setDeleteId] = useState<number | null>(null)
  const [deleteLoading, setDeleteLoading] = useState(false)

  const load = useCallback(async (p: number, filters: Record<string, string>) => {
    setLoading(true)
    try {
      const data = await accountsApi.list({
        offset: (p - 1) * PAGE_SIZE,
        limit: PAGE_SIZE,
        ...(filters.name ? { name: filters.name } : {}),
      })
      setAccounts(data.items)
      setTotal(data.total)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    void load(page, filterValues)
  }, [load, page, filterValues])

  const handleCreate = async () => {
    setFormError(null)
    setFormLoading(true)
    try {
      const payload: AccountCreate = {
        name: formValues.name ?? '',
        type: formValues.type || null,
        industry: formValues.industry || null,
        phone: formValues.phone || null,
        website: formValues.website || null,
      }
      await accountsApi.create(payload)
      setShowCreate(false)
      setFormValues({})
      setPage(1)
      await load(1, filterValues)
    } catch {
      setFormError('Failed to create account.')
    } finally {
      setFormLoading(false)
    }
  }

  const handleDelete = async () => {
    if (!deleteId) return
    setDeleteLoading(true)
    try {
      await accountsApi.delete(deleteId)
      setDeleteId(null)
      await load(page, filterValues)
    } finally {
      setDeleteLoading(false)
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-semibold tracking-tight">Accounts</h2>
        <Button onClick={() => setShowCreate(true)}>+ New Account</Button>
      </div>

      <FilterBar
        filters={[{ key: 'name', placeholder: 'Search by name…', type: 'text' }]}
        values={filterValues}
        onChange={(k, v) => {
          setFilterValues((prev) => ({ ...prev, [k]: v }))
          setPage(1)
        }}
        onClear={() => {
          setFilterValues({})
          setPage(1)
        }}
      />

      <DataTable
        columns={COLUMNS}
        data={accounts}
        loading={loading}
        total={total}
        page={page}
        pageSize={PAGE_SIZE}
        onPageChange={setPage}
        onRowClick={(r) => navigate(`/accounts/${r.id}`)}
      />

      <Dialog open={showCreate} onOpenChange={setShowCreate}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>New Account</DialogTitle>
          </DialogHeader>
          <RecordForm
            fields={FORM_FIELDS}
            values={formValues}
            onChange={(k, v) => setFormValues((p) => ({ ...p, [k]: v }))}
            onSubmit={() => void handleCreate()}
            onCancel={() => setShowCreate(false)}
            submitLabel="Create Account"
            loading={formLoading}
            error={formError}
          />
        </DialogContent>
      </Dialog>

      <DeleteConfirmDialog
        open={deleteId !== null}
        onOpenChange={(o) => !o && setDeleteId(null)}
        onConfirm={() => void handleDelete()}
        loading={deleteLoading}
      />
    </div>
  )
}

