import { useCallback, useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { contactsApi } from '@/api/contacts'
import type { Contact, ContactUpdate } from '@/api/types'
import DeleteConfirmDialog from '@/components/DeleteConfirmDialog'
import DetailView, { type FieldDefinition } from '@/components/DetailView'
import RecordForm from '@/components/RecordForm'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

const DETAIL_FIELDS: FieldDefinition[] = [
  { key: 'first_name', label: 'First Name' },
  { key: 'last_name', label: 'Last Name' },
  { key: 'email', label: 'Email' },
  { key: 'phone', label: 'Phone' },
  { key: 'mobile_phone', label: 'Mobile' },
  { key: 'title', label: 'Title' },
  { key: 'department', label: 'Department' },
  { key: 'account_id', label: 'Account ID' },
  { key: 'lead_source', label: 'Lead Source' },
  { key: 'mailing_city', label: 'City' },
  { key: 'mailing_country', label: 'Country' },
  { key: 'created_at', label: 'Created At' },
  { key: 'updated_at', label: 'Updated At' },
]

const FORM_FIELDS = [
  { key: 'last_name', label: 'Last Name', required: true },
  { key: 'first_name', label: 'First Name' },
  { key: 'email', label: 'Email', type: 'email' as const },
  { key: 'phone', label: 'Phone', type: 'tel' as const },
  { key: 'mobile_phone', label: 'Mobile', type: 'tel' as const },
  { key: 'title', label: 'Title' },
  { key: 'department', label: 'Department' },
  { key: 'account_id', label: 'Account ID', type: 'number' as const },
  { key: 'mailing_city', label: 'Mailing City' },
  { key: 'mailing_country', label: 'Mailing Country' },
]

export default function ContactDetailPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [contact, setContact] = useState<Contact | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [editing, setEditing] = useState(false)
  const [formValues, setFormValues] = useState<Record<string, string>>({})
  const [saveLoading, setSaveLoading] = useState(false)
  const [saveError, setSaveError] = useState<string | null>(null)
  const [showDelete, setShowDelete] = useState(false)
  const [deleteLoading, setDeleteLoading] = useState(false)

  const load = useCallback(async () => {
    if (!id) return
    setLoading(true)
    try {
      const data = await contactsApi.get(parseInt(id, 10))
      setContact(data)
    } catch {
      setError('Contact not found.')
    } finally {
      setLoading(false)
    }
  }, [id])

  useEffect(() => {
    void load()
  }, [load])

  const startEdit = () => {
    if (!contact) return
    setFormValues(
      Object.fromEntries(
        FORM_FIELDS.map((f) => [f.key, contact[f.key as keyof Contact] != null ? String(contact[f.key as keyof Contact]) : '']),
      ),
    )
    setEditing(true)
  }

  const handleSave = async () => {
    if (!id) return
    setSaveError(null)
    setSaveLoading(true)
    try {
      const payload: ContactUpdate = {
        last_name: formValues.last_name || undefined,
        first_name: formValues.first_name || null,
        email: formValues.email || null,
        phone: formValues.phone || null,
        mobile_phone: formValues.mobile_phone || null,
        title: formValues.title || null,
        department: formValues.department || null,
        account_id: formValues.account_id ? parseInt(formValues.account_id, 10) : null,
        mailing_city: formValues.mailing_city || null,
        mailing_country: formValues.mailing_country || null,
      }
      const updated = await contactsApi.update(parseInt(id, 10), payload)
      setContact(updated)
      setEditing(false)
    } catch {
      setSaveError('Failed to save changes.')
    } finally {
      setSaveLoading(false)
    }
  }

  const handleDelete = async () => {
    if (!id) return
    setDeleteLoading(true)
    try {
      await contactsApi.delete(parseInt(id, 10))
      navigate('/contacts')
    } finally {
      setDeleteLoading(false)
    }
  }

  if (loading) return <p className="p-4 text-muted-foreground">Loading…</p>
  if (error || !contact) return <p className="p-4 text-destructive">{error ?? 'Not found.'}</p>

  const title = `${contact.first_name ?? ''} ${contact.last_name}`.trim()

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Button variant="ghost" size="sm" onClick={() => navigate('/contacts')}>
            ← Contacts
          </Button>
          <h2 className="text-2xl font-semibold tracking-tight">{title}</h2>
        </div>
        <div className="flex gap-2">
          {!editing && (
            <>
              <Button variant="outline" onClick={startEdit}>
                Edit
              </Button>
              <Button variant="destructive" onClick={() => setShowDelete(true)}>
                Delete
              </Button>
            </>
          )}
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Contact Details</CardTitle>
        </CardHeader>
        <CardContent>
          {editing ? (
            <RecordForm
              fields={FORM_FIELDS}
              values={formValues}
              onChange={(k, v) => setFormValues((p) => ({ ...p, [k]: v }))}
              onSubmit={handleSave}
              onCancel={() => setEditing(false)}
              submitLabel="Save Changes"
              loading={saveLoading}
              error={saveError}
            />
          ) : (
            <DetailView record={contact as unknown as Record<string, unknown>} fields={DETAIL_FIELDS} />
          )}
        </CardContent>
      </Card>

      <DeleteConfirmDialog
        open={showDelete}
        onOpenChange={setShowDelete}
        onConfirm={() => void handleDelete()}
        loading={deleteLoading}
        title="Delete Contact"
        description={`Are you sure you want to delete ${title}? This cannot be undone.`}
      />
    </div>
  )
}
