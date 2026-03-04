import { useNavigate } from 'react-router-dom'
import { accountsApi } from '@/api/accounts'
import type { Account, AccountCreate } from '@/api/types'
import DataTable, { type Column } from '@/components/DataTable'
import FilterBar from '@/components/FilterBar'
import RecordForm from '@/components/RecordForm'
import { Button } from '@/components/ui/button'
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { useEntityCRUD } from '@/lib/hooks/useEntityCRUD'

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

function buildListParams(f: Record<string, string>) {
  return f.name ? { name: f.name } : {}
}

function buildCreatePayload(f: Record<string, string>): AccountCreate {
  return {
    name: f.name ?? '',
    type: f.type || null,
    industry: f.industry || null,
    phone: f.phone || null,
    website: f.website || null,
  }
}

export default function AccountsPage() {
  const navigate = useNavigate()
  const crud = useEntityCRUD<Account, AccountCreate>({
    api: accountsApi,
    pageSize: PAGE_SIZE,
    buildListParams,
    buildCreatePayload,
    createErrorMessage: 'Failed to create account.',
  })

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-semibold tracking-tight">Accounts</h2>
        <Button onClick={() => crud.setShowCreate(true)}>+ New Account</Button>
      </div>

      <FilterBar
        filters={[{ key: 'name', placeholder: 'Search by name…', type: 'text' }]}
        values={crud.filterValues}
        onChange={crud.setFilter}
        onClear={crud.clearFilters}
      />

      <DataTable
        columns={COLUMNS}
        data={crud.items}
        loading={crud.loading}
        total={crud.total}
        page={crud.page}
        pageSize={PAGE_SIZE}
        onPageChange={crud.setPage}
        onRowClick={(r) => navigate(`/accounts/${r.id}`)}
      />

      <Dialog open={crud.showCreate} onOpenChange={crud.setShowCreate}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>New Account</DialogTitle>
          </DialogHeader>
          <RecordForm
            fields={FORM_FIELDS}
            values={crud.formValues}
            onChange={crud.setFormValue}
            onSubmit={() => void crud.handleCreate()}
            onCancel={() => crud.setShowCreate(false)}
            submitLabel="Create Account"
            loading={crud.formLoading}
            error={crud.formError}
          />
        </DialogContent>
      </Dialog>
    </div>
  )
}
