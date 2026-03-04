import { useNavigate } from 'react-router-dom'
import { leadsApi } from '@/api/leads'
import type { Lead, LeadCreate } from '@/api/types'
import DataTable, { type Column } from '@/components/DataTable'
import FilterBar from '@/components/FilterBar'
import RecordForm from '@/components/RecordForm'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { useEntityCRUD } from '@/lib/hooks/useEntityCRUD'

const PAGE_SIZE = 20
const LEAD_STATUSES = ['New', 'Working', 'Nurturing', 'Unqualified', 'Converted']

const COLUMNS: Column<Lead>[] = [
  { key: 'name', label: 'Name', render: (r) => `${r.first_name ?? ''} ${r.last_name}`.trim() },
  { key: 'company', label: 'Company' },
  {
    key: 'status',
    label: 'Status',
    render: (r) => (
      <Badge variant={r.status === 'Converted' ? 'secondary' : r.status === 'Unqualified' ? 'destructive' : 'default'}>
        {r.status}
      </Badge>
    ),
  },
  { key: 'email', label: 'Email' },
  { key: 'lead_source', label: 'Source' },
]

const FORM_FIELDS = [
  { key: 'last_name', label: 'Last Name', required: true, placeholder: 'Smith' },
  { key: 'first_name', label: 'First Name', placeholder: 'Jane' },
  { key: 'company', label: 'Company', required: true, placeholder: 'Acme Corp' },
  { key: 'email', label: 'Email', type: 'email' as const, placeholder: 'jane@example.com' },
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
    options: ['Web', 'Phone Inquiry', 'Partner Referral', 'Purchased List', 'Other'].map((s) => ({ value: s, label: s })),
  },
]

function buildListParams(f: Record<string, string>) {
  return f.status ? { status: f.status } : {}
}

function buildCreatePayload(f: Record<string, string>): LeadCreate {
  return {
    last_name: f.last_name ?? '',
    company: f.company ?? '',
    first_name: f.first_name || null,
    email: f.email || null,
    phone: f.phone || null,
    status: f.status || 'New',
    lead_source: f.lead_source || null,
  }
}

export default function LeadsPage() {
  const navigate = useNavigate()
  const crud = useEntityCRUD<Lead, LeadCreate>({
    api: leadsApi,
    pageSize: PAGE_SIZE,
    buildListParams,
    buildCreatePayload,
    createErrorMessage: 'Failed to create lead.',
  })

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-semibold tracking-tight">Leads</h2>
        <Button onClick={() => crud.setShowCreate(true)}>+ New Lead</Button>
      </div>

      <FilterBar
        filters={[
          {
            key: 'status',
            placeholder: 'Filter by status',
            type: 'select',
            options: LEAD_STATUSES.map((s) => ({ value: s, label: s })),
          },
        ]}
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
        onRowClick={(r) => navigate(`/leads/${r.id}`)}
      />

      <Dialog open={crud.showCreate} onOpenChange={crud.setShowCreate}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>New Lead</DialogTitle>
          </DialogHeader>
          <RecordForm
            fields={FORM_FIELDS}
            values={crud.formValues}
            onChange={crud.setFormValue}
            onSubmit={() => void crud.handleCreate()}
            onCancel={() => crud.setShowCreate(false)}
            submitLabel="Create Lead"
            loading={crud.formLoading}
            error={crud.formError}
          />
        </DialogContent>
      </Dialog>
    </div>
  )
}
