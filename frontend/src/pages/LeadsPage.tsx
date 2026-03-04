import { useCallback, useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { leadsApi } from '@/api/leads'
import type { Lead, LeadCreate } from '@/api/types'
import DataTable, { type Column } from '@/components/DataTable'
import DeleteConfirmDialog from '@/components/DeleteConfirmDialog'
import FilterBar from '@/components/FilterBar'
import RecordForm from '@/components/RecordForm'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog'

const PAGE_SIZE = 20
const LEAD_STATUSES = ['New', 'Working', 'Nurturing', 'Unqualified', 'Converted']

const COLUMNS: Column<Lead>[] = [
  { key: 'name', label: 'Name', render: (r) => `${r.first_name ?? ''} ${r.last_name}`.trim() },
  { key: 'company', label: 'Company' },
  {
    key: 'status', label: 'Status',
    render: (r) => <Badge variant={r.status === 'Converted' ? 'secondary' : r.status === 'Unqualified' ? 'destructive' : 'default'}>{r.status}</Badge>,
  },
  { key: 'email', label: 'Email' },
  { key: 'lead_source', label: 'Source' },
]

const FORM_FIELDS = [
  { key: 'last_name', label: 'Last Name', required: true, placeholder: 'Smith' },
  { key: 'first_name', label: 'First Name', placeholder: 'Jane' },
  { key: 'company', label: 'Company', placeholder: 'Acme Corp' },
  { key: 'email', label: 'Email', type: 'email' as const, placeholder: 'jane@example.com' },
  { key: 'phone', label: 'Phone', type: 'tel' as const },
  { key: 'status', label: 'Status', type: 'select' as const, options: LEAD_STATUSES.map((s) => ({ value: s, label: s })) },
  { key: 'lead_source', label: 'Lead Source', type: 'select' as const, options: ['Web', 'Phone Inquiry', 'Partner Referral', 'Purchased List', 'Other'].map((s) => ({ value: s, label: s })) },
]

export default function LeadsPage() {
  const navigate = useNavigate()
  const [leads, setLeads] = useState<Lead[]>([])
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
      const data = await leadsApi.list({ offset: (p - 1) * PAGE_SIZE, limit: PAGE_SIZE, ...(filters.status ? { status: filters.status } : {}) })
      setLeads(data.items)
      setTotal(data.total)
    } finally { setLoading(false) }
  }, [])

  useEffect(() => { void load(page, filterValues) }, [load, page, filterValues])

  const handleCreate = async () => {
    setFormError(null); setFormLoading(true)
    try {
      const payload: LeadCreate = { last_name: formValues.last_name ?? '', first_name: formValues.first_name || null, company: formValues.company || null, email: formValues.email || null, phone: formValues.phone || null, status: formValues.status || 'New', lead_source: formValues.lead_source || null }
      await leadsApi.create(payload)
      setShowCreate(false); setFormValues({}); setPage(1)
      await load(1, filterValues)
    } catch { setFormError('Failed to create lead.') } finally { setFormLoading(false) }
  }

  const handleDelete = async () => {
    if (!deleteId) return
    setDeleteLoading(true)
    try { await leadsApi.delete(deleteId); setDeleteId(null); await load(page, filterValues) } finally { setDeleteLoading(false) }
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-semibold tracking-tight">Leads</h2>
        <Button onClick={() => setShowCreate(true)}>+ New Lead</Button>
      </div>
      <FilterBar
        filters={[{ key: 'status', placeholder: 'Filter by status', type: 'select', options: LEAD_STATUSES.map((s) => ({ value: s, label: s })) }]}
        values={filterValues}
        onChange={(k, v) => { setFilterValues((prev) => ({ ...prev, [k]: v })); setPage(1) }}
        onClear={() => { setFilterValues({}); setPage(1) }}
      />
      <DataTable columns={COLUMNS} data={leads} loading={loading} total={total} page={page} pageSize={PAGE_SIZE} onPageChange={setPage} onRowClick={(r) => navigate(`/leads/${r.id}`)} />
      <Dialog open={showCreate} onOpenChange={setShowCreate}>
        <DialogContent>
          <DialogHeader><DialogTitle>New Lead</DialogTitle></DialogHeader>
          <RecordForm fields={FORM_FIELDS} values={formValues} onChange={(k, v) => setFormValues((p) => ({ ...p, [k]: v }))} onSubmit={handleCreate} onCancel={() => setShowCreate(false)} submitLabel="Create Lead" loading={formLoading} error={formError} />
        </DialogContent>
      </Dialog>
      <DeleteConfirmDialog open={deleteId !== null} onOpenChange={(o) => !o && setDeleteId(null)} onConfirm={() => void handleDelete()} loading={deleteLoading} />
    </div>
  )
}
