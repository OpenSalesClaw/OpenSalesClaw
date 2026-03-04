import { useCallback, useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { casesApi } from '@/api/cases'
import type { Case, CaseCreate } from '@/api/types'
import DataTable, { type Column } from '@/components/DataTable'
import DeleteConfirmDialog from '@/components/DeleteConfirmDialog'
import FilterBar from '@/components/FilterBar'
import RecordForm from '@/components/RecordForm'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog'

const PAGE_SIZE = 20

const STATUSES = ['New', 'Working', 'Escalated', 'Closed']
const PRIORITIES = ['Low', 'Medium', 'High', 'Critical']

function priorityVariant(p: string): 'default' | 'secondary' | 'destructive' | 'outline' {
  if (p === 'Critical') return 'destructive'
  if (p === 'High') return 'default'
  if (p === 'Medium') return 'secondary'
  return 'outline'
}

const COLUMNS: Column<Case>[] = [
  { key: 'case_number', label: 'Case #' },
  { key: 'subject', label: 'Subject' },
  {
    key: 'status',
    label: 'Status',
    render: (r) => <Badge variant={r.status === 'Closed' ? 'secondary' : 'outline'}>{r.status}</Badge>,
  },
  {
    key: 'priority',
    label: 'Priority',
    render: (r) => <Badge variant={priorityVariant(r.priority)}>{r.priority}</Badge>,
  },
  { key: 'account_id', label: 'Account ID' },
]

const FORM_FIELDS = [
  { key: 'subject', label: 'Subject', required: true, placeholder: 'Login issue' },
  { key: 'description', label: 'Description', type: 'textarea' as const },
  {
    key: 'status',
    label: 'Status',
    type: 'select' as const,
    options: STATUSES.map((s) => ({ value: s, label: s })),
  },
  {
    key: 'priority',
    label: 'Priority',
    type: 'select' as const,
    options: PRIORITIES.map((s) => ({ value: s, label: s })),
  },
  { key: 'account_id', label: 'Account ID', type: 'number' as const, placeholder: '1' },
  {
    key: 'origin',
    label: 'Origin',
    type: 'select' as const,
    options: ['Phone', 'Email', 'Web'].map((s) => ({ value: s, label: s })),
  },
]

export default function CasesPage() {
  const navigate = useNavigate()
  const [items, setItems] = useState<Case[]>([])
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
      const data = await casesApi.list({
        offset: (p - 1) * PAGE_SIZE,
        limit: PAGE_SIZE,
        ...(filters.status ? { status: filters.status } : {}),
        ...(filters.priority ? { priority: filters.priority } : {}),
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
      const payload: CaseCreate = {
        subject: formValues.subject ?? '',
        description: formValues.description || null,
        status: formValues.status || undefined,
        priority: formValues.priority || undefined,
        account_id: formValues.account_id ? parseInt(formValues.account_id, 10) : null,
        origin: formValues.origin || null,
      }
      await casesApi.create(payload)
      setShowCreate(false)
      setFormValues({})
      setPage(1)
      await load(1, filterValues)
    } catch {
      setFormError('Failed to create case.')
    } finally {
      setFormLoading(false)
    }
  }

  const handleDelete = async () => {
    if (!deleteId) return
    setDeleteLoading(true)
    try {
      await casesApi.delete(deleteId)
      setDeleteId(null)
      await load(page, filterValues)
    } finally {
      setDeleteLoading(false)
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-semibold tracking-tight">Cases</h2>
        <Button onClick={() => setShowCreate(true)}>+ New Case</Button>
      </div>

      <FilterBar
        filters={[
          {
            key: 'status',
            placeholder: 'Filter by status',
            type: 'select',
            options: STATUSES.map((s) => ({ value: s, label: s })),
          },
          {
            key: 'priority',
            placeholder: 'Filter by priority',
            type: 'select',
            options: PRIORITIES.map((s) => ({ value: s, label: s })),
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
        onRowClick={(r) => navigate(`/cases/${r.id}`)}
      />

      <Dialog open={showCreate} onOpenChange={setShowCreate}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>New Case</DialogTitle>
          </DialogHeader>
          <RecordForm
            fields={FORM_FIELDS}
            values={formValues}
            onChange={(k, v) => setFormValues((p) => ({ ...p, [k]: v }))}
            onSubmit={handleCreate}
            onCancel={() => setShowCreate(false)}
            submitLabel="Create Case"
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
