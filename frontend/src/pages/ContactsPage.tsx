import { useEffect, useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { accountsApi } from '@/api/accounts'
import { contactsApi } from '@/api/contacts'
import type { Account, Contact, ContactCreate } from '@/api/types'
import DataTable, { type Column } from '@/components/DataTable'
import FilterBar from '@/components/FilterBar'
import RecordForm from '@/components/RecordForm'
import { Button } from '@/components/ui/button'
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { useEntityCRUD } from '@/lib/hooks/useEntityCRUD'

const PAGE_SIZE = 20

function buildListParams(f: Record<string, string>) {
  return f.email ? { email: f.email } : {}
}

function buildCreatePayload(f: Record<string, string>): ContactCreate {
  return {
    last_name: f.last_name ?? '',
    first_name: f.first_name || null,
    email: f.email || null,
    phone: f.phone || null,
    title: f.title || null,
    account_id: f.account_id ? parseInt(f.account_id, 10) : null,
  }
}

export default function ContactsPage() {
  const navigate = useNavigate()
  const [accounts, setAccounts] = useState<Account[]>([])

  useEffect(() => {
    void accountsApi.list({ limit: 200 }).then((res) => setAccounts(res.items))
  }, [])

  const accountMap = useMemo(() => new Map(accounts.map((a) => [a.id, a.name])), [accounts])
  const accountOptions = useMemo(() => accounts.map((a) => ({ value: String(a.id), label: a.name })), [accounts])

  const columns = useMemo<Column<Contact>[]>(
    () => [
      { key: 'name', label: 'Name', render: (r) => `${r.first_name ?? ''} ${r.last_name}`.trim() },
      { key: 'email', label: 'Email' },
      { key: 'phone', label: 'Phone' },
      {
        key: 'account_id',
        label: 'Account',
        render: (r) => (r.account_id != null ? (accountMap.get(r.account_id) ?? String(r.account_id)) : '—'),
      },
      { key: 'title', label: 'Title' },
    ],
    [accountMap],
  )

  const formFields = useMemo(
    () => [
      { key: 'last_name', label: 'Last Name', required: true, placeholder: 'Smith' },
      { key: 'first_name', label: 'First Name', placeholder: 'Jane' },
      { key: 'email', label: 'Email', type: 'email' as const, placeholder: 'jane@example.com' },
      { key: 'phone', label: 'Phone', type: 'tel' as const, placeholder: '+1 555-000-0000' },
      { key: 'title', label: 'Title', placeholder: 'VP Sales' },
      { key: 'account_id', label: 'Account', type: 'combobox' as const, options: accountOptions, placeholder: 'Search accounts…' },
    ],
    [accountOptions],
  )

  const crud = useEntityCRUD<Contact, ContactCreate>({
    api: contactsApi,
    pageSize: PAGE_SIZE,
    buildListParams,
    buildCreatePayload,
    createErrorMessage: 'Failed to create contact.',
  })

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-semibold tracking-tight">Contacts</h2>
        <Button onClick={() => crud.setShowCreate(true)}>+ New Contact</Button>
      </div>

      <FilterBar
        filters={[{ key: 'email', placeholder: 'Search email…', type: 'text' }]}
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
        onRowClick={(r) => navigate(`/contacts/${r.id}`)}
      />

      <Dialog open={crud.showCreate} onOpenChange={crud.setShowCreate}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>New Contact</DialogTitle>
          </DialogHeader>
          <RecordForm
            fields={formFields}
            values={crud.formValues}
            onChange={crud.setFormValue}
            onSubmit={() => void crud.handleCreate()}
            onCancel={() => crud.setShowCreate(false)}
            submitLabel="Create Contact"
            loading={crud.formLoading}
            error={crud.formError}
          />
        </DialogContent>
      </Dialog>
    </div>
  )
}
