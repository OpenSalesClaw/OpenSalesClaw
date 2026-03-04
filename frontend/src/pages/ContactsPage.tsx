import { useCallback, useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { contactsApi } from '@/api/contacts'
import type { Contact, ContactCreate } from '@/api/types'
import DataTable, { type Column } from '@/components/DataTable'
import DeleteConfirmDialog from '@/components/DeleteConfirmDialog'
import FilterBar from '@/components/FilterBar'
import RecordForm from '@/components/RecordForm'
import { Button } from '@/components/ui/button'
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog'

const PAGE_SIZE = 20

const COLUMNS: Column<Contact>[] = [
  {
    key: 'name',
    label: 'Name',
    render: (r) => `${r.first_name ?? ''} ${r.last_name}`.trim(),
  },
  { key: 'email', label: 'Email' },
  { key: 'phone', label: 'Phone' },
  { key: 'account_id', label: 'Account ID' },
  { key: 'title', label: 'Title' },
]

const FORM_FIELDS = [
  { key: 'last_name', label: 'Last Name', required: true, placeholder: 'Smith' },
  { key: 'first_name', label: 'First Name', placeholder: 'Jane' },
  { key: 'email', label: 'Email', type: 'email' as const, placeholder: 'jane@example.com' },
  { key: 'phone', label: 'Phone', type: 'tel' as const, placeholder: '+1 555-000-0000' },
  { key: 'title', label: 'Title', placeholder: 'VP Sales' },
  { key: 'account_id', label: 'Account ID', type: 'number' as const, placeholder: '1' },
]

export default function ContactsPage() {
  const navigate = useNavigate()
  const [contacts, setContacts] = useState<Contact[]>([])
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
      const data = await contactsApi.list({
        offset: (p - 1) * PAGE_SIZE,
        limit: PAGE_SIZE,
        ...(filters.email ? { email: filters.email } : {}),
      })
      setContacts(data.items)
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
      const payload: ContactCreate = {
        last_name: formValues.last_name ?? '',
        first_name: formValues.first_name || null,
        email: formValues.email || null,
        phone: formValues.phone || null,
        title: formValues.title || null,
        account_id: formValues.account_id ? parseInt(formValues.account_id, 10) : null,
      }
      await contactsApi.create(payload)
      setShowCreate(false)
      setFormValues({})
      setPage(1)
      await load(1, filterValues)
    } catch {
      setFormError('Failed to create contact.')
    } finally {
      setFormLoading(false)
    }
  }

  const handleDelete = async () => {
    if (!deleteId) return
    setDeleteLoading(true)
    try {
      await contactsApi.delete(deleteId)
      setDeleteId(null)
      await load(page, filterValues)
    } finally {
      setDeleteLoading(false)
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-semibold tracking-tight">Contacts</h2>
        <Button onClick={() => setShowCreate(true)}>+ New Contact</Button>
      </div>

      <FilterBar
        filters={[{ key: 'email', placeholder: 'Search email…', type: 'text' }]}
        values={filterValues}
        onChange={(k, v) => { setFilterValues((prev) => ({ ...prev, [k]: v })); setPage(1) }}
        onClear={() => { setFilterValues({}); setPage(1) }}
      />

      <DataTable
        columns={COLUMNS}
        data={contacts}
        loading={loading}
        total={total}
        page={page}
        pageSize={PAGE_SIZE}
        onPageChange={setPage}
        onRowClick={(r) => navigate(`/contacts/${r.id}`)}
      />

      <Dialog open={showCreate} onOpenChange={setShowCreate}>
        <DialogContent>
          <DialogHeader><DialogTitle>New Contact</DialogTitle></DialogHeader>
          <RecordForm
            fields={FORM_FIELDS}
            values={formValues}
            onChange={(k, v) => setFormValues((p) => ({ ...p, [k]: v }))}
            onSubmit={handleCreate}
            onCancel={() => setShowCreate(false)}
            submitLabel="Create Contact"
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
