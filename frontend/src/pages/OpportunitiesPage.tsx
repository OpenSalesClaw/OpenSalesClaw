import { useNavigate } from 'react-router-dom'
import { opportunitiesApi } from '@/api/opportunities'
import type { Opportunity, OpportunityCreate } from '@/api/types'
import DataTable, { type Column } from '@/components/DataTable'
import FilterBar from '@/components/FilterBar'
import RecordForm from '@/components/RecordForm'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { useEntityCRUD } from '@/lib/hooks/useEntityCRUD'

const PAGE_SIZE = 20

const STAGES = [
  'Prospecting',
  'Qualification',
  'Needs Analysis',
  'Value Proposition',
  'Id. Decision Makers',
  'Perception Analysis',
  'Proposal/Price Quote',
  'Negotiation/Review',
  'Closed Won',
  'Closed Lost',
]

function stageVariant(stage: string): 'default' | 'secondary' | 'destructive' | 'outline' {
  if (stage === 'Closed Won') return 'secondary'
  if (stage === 'Closed Lost') return 'destructive'
  return 'outline'
}

function formatCurrency(value: number | null) {
  if (value === null || value === undefined) return '—'
  return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(value)
}

const COLUMNS: Column<Opportunity>[] = [
  { key: 'name', label: 'Name' },
  { key: 'account_id', label: 'Account ID' },
  {
    key: 'stage',
    label: 'Stage',
    render: (r) => <Badge variant={stageVariant(r.stage)}>{r.stage}</Badge>,
  },
  { key: 'amount', label: 'Amount', render: (r) => formatCurrency(r.amount) },
  { key: 'close_date', label: 'Close Date' },
]

const FORM_FIELDS = [
  { key: 'name', label: 'Name', required: true, placeholder: 'Q3 Deal' },
  { key: 'close_date', label: 'Close Date', required: true, type: 'date' as const },
  { key: 'stage', label: 'Stage', type: 'select' as const, options: STAGES.map((s) => ({ value: s, label: s })) },
  { key: 'amount', label: 'Amount', type: 'number' as const, placeholder: '50000' },
  { key: 'account_id', label: 'Account ID', type: 'number' as const, placeholder: '1' },
  { key: 'probability', label: 'Probability (%)', type: 'number' as const, placeholder: 'Auto from stage' },
]

function buildListParams(f: Record<string, string>) {
  return f.stage ? { stage: f.stage } : {}
}

function buildCreatePayload(f: Record<string, string>): OpportunityCreate {
  return {
    name: f.name ?? '',
    close_date: f.close_date ?? '',
    stage: f.stage || undefined,
    amount: f.amount ? parseFloat(f.amount) : null,
    account_id: f.account_id ? parseInt(f.account_id, 10) : null,
    probability: f.probability ? parseInt(f.probability, 10) : null,
  }
}

export default function OpportunitiesPage() {
  const navigate = useNavigate()
  const crud = useEntityCRUD<Opportunity, OpportunityCreate>({
    api: opportunitiesApi,
    pageSize: PAGE_SIZE,
    buildListParams,
    buildCreatePayload,
    createErrorMessage: 'Failed to create opportunity.',
  })

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-semibold tracking-tight">Opportunities</h2>
        <Button onClick={() => crud.setShowCreate(true)}>+ New Opportunity</Button>
      </div>

      <FilterBar
        filters={[
          {
            key: 'stage',
            placeholder: 'Filter by stage',
            type: 'select',
            options: STAGES.map((s) => ({ value: s, label: s })),
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
        onRowClick={(r) => navigate(`/opportunities/${r.id}`)}
      />

      <Dialog open={crud.showCreate} onOpenChange={crud.setShowCreate}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>New Opportunity</DialogTitle>
          </DialogHeader>
          <RecordForm
            fields={FORM_FIELDS}
            values={crud.formValues}
            onChange={crud.setFormValue}
            onSubmit={() => void crud.handleCreate()}
            onCancel={() => crud.setShowCreate(false)}
            submitLabel="Create Opportunity"
            loading={crud.formLoading}
            error={crud.formError}
          />
        </DialogContent>
      </Dialog>
    </div>
  )
}
