import { useEffect, useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { accountsApi } from '@/api/accounts'
import { casesApi } from '@/api/cases'
import type { Account, Case, CaseCreate } from '@/api/types'
import DataTable, { type Column } from '@/components/DataTable'
import FilterBar from '@/components/FilterBar'
import RecordForm from '@/components/RecordForm'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { useEntityCRUD } from '@/lib/hooks/useEntityCRUD'

const PAGE_SIZE = 20
const STATUSES = ['New', 'Working', 'Escalated', 'Closed']
const PRIORITIES = ['Low', 'Medium', 'High', 'Critical']

function priorityVariant(p: string): 'default' | 'secondary' | 'destructive' | 'outline' {
  if (p === 'Critical') return 'destructive'
  if (p === 'High') return 'default'
  if (p === 'Medium') return 'secondary'
  return 'outline'
}



function buildListParams(f: Record<string, string>) {
  return {
    ...(f.status ? { status: f.status } : {}),
    ...(f.priority ? { priority: f.priority } : {}),
  }
}

function buildCreatePayload(f: Record<string, string>): CaseCreate {
  return {
    subject: f.subject ?? '',
    description: f.description || null,
    status: f.status || undefined,
    priority: f.priority || undefined,
    account_id: f.account_id ? parseInt(f.account_id, 10) : null,
    origin: f.origin || null,
  }
}

export default function CasesPage() {
  const navigate = useNavigate()
  const [accounts, setAccounts] = useState<Account[]>([])

  useEffect(() => {
    void accountsApi.list({ limit: 200 }).then((res) => setAccounts(res.items))
  }, [])

  const accountMap = useMemo(() => new Map(accounts.map((a) => [a.id, a.name])), [accounts])
  const accountOptions = useMemo(() => accounts.map((a) => ({ value: String(a.id), label: a.name })), [accounts])

  const columns = useMemo<Column<Case>[]>(
    () => [
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
      {
        key: 'account_id',
        label: 'Account',
        render: (r) => (r.account_id != null ? (accountMap.get(r.account_id) ?? String(r.account_id)) : '—'),
      },
    ],
    [accountMap],
  )

  const formFields = useMemo(
    () => [
      { key: 'subject', label: 'Subject', required: true, placeholder: 'Login issue' },
      { key: 'description', label: 'Description', type: 'textarea' as const },
      { key: 'status', label: 'Status', type: 'select' as const, options: STATUSES.map((s) => ({ value: s, label: s })) },
      { key: 'priority', label: 'Priority', type: 'select' as const, options: PRIORITIES.map((s) => ({ value: s, label: s })) },
      { key: 'account_id', label: 'Account', type: 'combobox' as const, options: accountOptions, placeholder: 'Search accounts…' },
      { key: 'origin', label: 'Origin', type: 'select' as const, options: ['Phone', 'Email', 'Web'].map((s) => ({ value: s, label: s })) },
    ],
    [accountOptions],
  )

  const crud = useEntityCRUD<Case, CaseCreate>({
    api: casesApi,
    pageSize: PAGE_SIZE,
    buildListParams,
    buildCreatePayload,
    createErrorMessage: 'Failed to create case.',
  })

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-semibold tracking-tight">Cases</h2>
        <Button onClick={() => crud.setShowCreate(true)}>+ New Case</Button>
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
        values={crud.filterValues}
        onChange={crud.setFilter}
        onClear={crud.clearFilters}
      />

      <DataTable
        columns={columns}
        data={crud.items}
        loading={crud.loading}
        total={crud.total}
        page={crud.page}
        pageSize={PAGE_SIZE}
        onPageChange={crud.setPage}
        onRowClick={(r) => navigate(`/cases/${r.id}`)}
      />

      <Dialog open={crud.showCreate} onOpenChange={crud.setShowCreate}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>New Case</DialogTitle>
          </DialogHeader>
          <RecordForm
            fields={formFields}
            values={crud.formValues}
            onChange={crud.setFormValue}
            onSubmit={() => void crud.handleCreate()}
            onCancel={() => crud.setShowCreate(false)}
            submitLabel="Create Case"
            loading={crud.formLoading}
            error={crud.formError}
          />
        </DialogContent>
      </Dialog>
    </div>
  )
}
