import { useCallback, useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { opportunitiesApi } from '@/api/opportunities'
import type { Opportunity, OpportunityCreate } from '@/api/types'
import DataTable, { type Column } from '@/components/DataTable'
import DeleteConfirmDialog from '@/components/DeleteConfirmDialog'
import FilterBar from '@/components/FilterBar'
import RecordForm from '@/components/RecordForm'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog'

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
  {
    key: 'probability',
    label: 'Probability (%)',
    type: 'number' as const,
    placeholder: 'Auto from stage',
  },
]

export default function OpportunitiesPage() {
  const navigate = useNavigate()
  const [items, setItems] = useState<Opportunity[]>([])
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
      const data = await opportunitiesApi.list({
        offset: (p - 1) * PAGE_SIZE,
        limit: PAGE_SIZE,
        ...(filters.stage ? { stage: filters.stage } : {}),
      })
      setItems(data.items)
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
      const payload: OpportunityCreate = {
        name: formValues.name ?? '',
        close_date: formValues.close_date ?? '',
        stage: formValues.stage || undefined,
        amount: formValues.amount ? parseFloat(formValues.amount) : null,
        account_id: formValues.account_id ? parseInt(formValues.account_id, 10) : null,
        probability: formValues.probability ? parseInt(formValues.probability, 10) : null,
      }
      await opportunitiesApi.create(payload)
      setShowCreate(false)
      setFormValues({})
      setPage(1)
      await load(1, filterValues)
    } catch {
      setFormError('Failed to create opportunity.')
    } finally {
      setFormLoading(false)
    }
  }

  const handleDelete = async () => {
    if (!deleteId) return
    setDeleteLoading(true)
    try {
      await opportunitiesApi.delete(deleteId)
      setDeleteId(null)
      await load(page, filterValues)
    } finally {
      setDeleteLoading(false)
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-semibold tracking-tight">Opportunities</h2>
        <Button onClick={() => setShowCreate(true)}>+ New Opportunity</Button>
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
        data={items}
        loading={loading}
        total={total}
        page={page}
        pageSize={PAGE_SIZE}
        onPageChange={setPage}
        onRowClick={(r) => navigate(`/opportunities/${r.id}`)}
      />

      <Dialog open={showCreate} onOpenChange={setShowCreate}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>New Opportunity</DialogTitle>
          </DialogHeader>
          <RecordForm
            fields={FORM_FIELDS}
            values={formValues}
            onChange={(k, v) => setFormValues((p) => ({ ...p, [k]: v }))}
            onSubmit={handleCreate}
            onCancel={() => setShowCreate(false)}
            submitLabel="Create Opportunity"
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
