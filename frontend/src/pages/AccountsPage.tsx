import { type FormEvent, useCallback, useEffect, useState } from 'react'
import apiClient from '../api/client'

interface Account {
  id: number
  name: string
  type: string | null
  industry: string | null
  phone: string | null
  website: string | null
  billing_city: string | null
  billing_country: string | null
}

interface PaginatedResponse<T> {
  items: T[]
  total: number
  offset: number
  limit: number
}

const LIMIT = 20

const ACCOUNT_TYPES = ['Customer', 'Partner', 'Prospect', 'Vendor', 'Other']

export default function AccountsPage() {
  const [accounts, setAccounts] = useState<Account[]>([])
  const [total, setTotal] = useState(0)
  const [offset, setOffset] = useState(0)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const [showForm, setShowForm] = useState(false)
  const [formName, setFormName] = useState('')
  const [formType, setFormType] = useState('')
  const [formIndustry, setFormIndustry] = useState('')
  const [formPhone, setFormPhone] = useState('')
  const [formWebsite, setFormWebsite] = useState('')
  const [formSubmitting, setFormSubmitting] = useState(false)
  const [formError, setFormError] = useState<string | null>(null)

  const fetchAccounts = useCallback(async (currentOffset: number) => {
    setLoading(true)
    setError(null)
    try {
      const { data } = await apiClient.get<PaginatedResponse<Account>>('/api/accounts', {
        params: { offset: currentOffset, limit: LIMIT },
      })
      setAccounts(data.items)
      setTotal(data.total)
    } catch {
      setError('Failed to load accounts.')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    void fetchAccounts(offset)
  }, [fetchAccounts, offset])

  const handleCreate = async (e: FormEvent) => {
    e.preventDefault()
    setFormError(null)
    setFormSubmitting(true)
    try {
      await apiClient.post('/api/accounts', {
        name: formName,
        type: formType || null,
        industry: formIndustry || null,
        phone: formPhone || null,
        website: formWebsite || null,
      })
      setShowForm(false)
      setFormName('')
      setFormType('')
      setFormIndustry('')
      setFormPhone('')
      setFormWebsite('')
      setOffset(0)
      await fetchAccounts(0)
    } catch {
      setFormError('Failed to create account. Please check your input.')
    } finally {
      setFormSubmitting(false)
    }
  }

  const totalPages = Math.ceil(total / LIMIT)
  const currentPage = Math.floor(offset / LIMIT) + 1

  return (
    <div>
      <div style={styles.header}>
        <h2 style={styles.heading}>Accounts</h2>
        <button style={styles.primaryButton} onClick={() => setShowForm(true)}>
          + New Account
        </button>
      </div>

      {showForm && (
        <div style={styles.modal}>
          <div style={styles.modalCard}>
            <h3 style={{ margin: '0 0 1rem', color: '#111827' }}>New Account</h3>
            <form onSubmit={handleCreate} style={styles.form}>
              <FormField label="Name *">
                <input
                  required
                  value={formName}
                  onChange={(e) => setFormName(e.target.value)}
                  style={styles.input}
                  placeholder="Acme Corp"
                />
              </FormField>
              <FormField label="Type">
                <select value={formType} onChange={(e) => setFormType(e.target.value)} style={styles.input}>
                  <option value="">— select —</option>
                  {ACCOUNT_TYPES.map((t) => (
                    <option key={t} value={t}>
                      {t}
                    </option>
                  ))}
                </select>
              </FormField>
              <FormField label="Industry">
                <input
                  value={formIndustry}
                  onChange={(e) => setFormIndustry(e.target.value)}
                  style={styles.input}
                  placeholder="Technology"
                />
              </FormField>
              <FormField label="Phone">
                <input
                  value={formPhone}
                  onChange={(e) => setFormPhone(e.target.value)}
                  style={styles.input}
                  placeholder="+1 555-000-0000"
                />
              </FormField>
              <FormField label="Website">
                <input
                  value={formWebsite}
                  onChange={(e) => setFormWebsite(e.target.value)}
                  style={styles.input}
                  placeholder="https://example.com"
                />
              </FormField>

              {formError && <p style={styles.errorText}>{formError}</p>}

              <div style={styles.formActions}>
                <button
                  type="button"
                  onClick={() => setShowForm(false)}
                  style={styles.secondaryButton}
                  disabled={formSubmitting}
                >
                  Cancel
                </button>
                <button type="submit" style={styles.primaryButton} disabled={formSubmitting}>
                  {formSubmitting ? 'Creating…' : 'Create'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {error && <p style={styles.errorText}>{error}</p>}

      {loading ? (
        <p style={{ color: '#6b7280' }}>Loading…</p>
      ) : (
        <>
          <div style={styles.tableWrapper}>
            <table style={styles.table}>
              <thead>
                <tr>
                  {['Name', 'Type', 'Industry', 'Phone', 'City', 'Country'].map((h) => (
                    <th key={h} style={styles.th}>
                      {h}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {accounts.length === 0 ? (
                  <tr>
                    <td colSpan={6} style={{ ...styles.td, textAlign: 'center', color: '#9ca3af' }}>
                      No accounts yet.
                    </td>
                  </tr>
                ) : (
                  accounts.map((a) => (
                    <tr key={a.id} style={styles.row}>
                      <td style={{ ...styles.td, fontWeight: 500, color: '#2563eb' }}>{a.name}</td>
                      <td style={styles.td}>{a.type ?? '—'}</td>
                      <td style={styles.td}>{a.industry ?? '—'}</td>
                      <td style={styles.td}>{a.phone ?? '—'}</td>
                      <td style={styles.td}>{a.billing_city ?? '—'}</td>
                      <td style={styles.td}>{a.billing_country ?? '—'}</td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>

          <div style={styles.pagination}>
            <button
              style={styles.pageButton}
              disabled={offset === 0}
              onClick={() => setOffset(Math.max(0, offset - LIMIT))}
            >
              ‹ Prev
            </button>
            <span style={{ fontSize: '0.875rem', color: '#374151' }}>
              Page {currentPage} of {totalPages || 1} &nbsp;·&nbsp; {total} total
            </span>
            <button
              style={styles.pageButton}
              disabled={offset + LIMIT >= total}
              onClick={() => setOffset(offset + LIMIT)}
            >
              Next ›
            </button>
          </div>
        </>
      )}
    </div>
  )
}

function FormField({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
      <label style={{ fontSize: '0.875rem', fontWeight: 500, color: '#374151' }}>{label}</label>
      {children}
    </div>
  )
}

const styles: Record<string, React.CSSProperties> = {
  header: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: '1.25rem',
  },
  heading: {
    margin: 0,
    color: '#111827',
  },
  primaryButton: {
    padding: '0.5rem 1rem',
    backgroundColor: '#2563eb',
    color: '#fff',
    border: 'none',
    borderRadius: 6,
    fontSize: '0.875rem',
    fontWeight: 600,
    cursor: 'pointer',
  },
  secondaryButton: {
    padding: '0.5rem 1rem',
    backgroundColor: '#f3f4f6',
    color: '#374151',
    border: '1px solid #d1d5db',
    borderRadius: 6,
    fontSize: '0.875rem',
    fontWeight: 500,
    cursor: 'pointer',
  },
  modal: {
    position: 'fixed',
    inset: 0,
    backgroundColor: 'rgba(0,0,0,0.4)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    zIndex: 50,
  },
  modalCard: {
    backgroundColor: '#fff',
    borderRadius: 8,
    padding: '2rem',
    width: '100%',
    maxWidth: 480,
    boxShadow: '0 4px 24px rgba(0,0,0,0.15)',
  },
  form: {
    display: 'flex',
    flexDirection: 'column',
    gap: '0.875rem',
  },
  input: {
    padding: '0.5rem 0.75rem',
    border: '1px solid #d1d5db',
    borderRadius: 6,
    fontSize: '0.9375rem',
    color: '#111827',
    outline: 'none',
  },
  formActions: {
    display: 'flex',
    gap: '0.75rem',
    justifyContent: 'flex-end',
    marginTop: '0.5rem',
  },
  errorText: {
    fontSize: '0.875rem',
    color: '#dc2626',
    margin: 0,
  },
  tableWrapper: {
    overflowX: 'auto',
    border: '1px solid #e5e7eb',
    borderRadius: 8,
    backgroundColor: '#fff',
  },
  table: {
    width: '100%',
    borderCollapse: 'collapse',
    fontSize: '0.875rem',
  },
  th: {
    padding: '0.75rem 1rem',
    textAlign: 'left',
    fontWeight: 600,
    color: '#6b7280',
    borderBottom: '1px solid #e5e7eb',
    backgroundColor: '#f9fafb',
  },
  td: {
    padding: '0.75rem 1rem',
    color: '#374151',
    borderBottom: '1px solid #f3f4f6',
  },
  row: {
    transition: 'background 0.1s',
  },
  pagination: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginTop: '1rem',
  },
  pageButton: {
    padding: '0.375rem 0.75rem',
    border: '1px solid #d1d5db',
    borderRadius: 6,
    backgroundColor: '#fff',
    fontSize: '0.875rem',
    cursor: 'pointer',
    color: '#374151',
  },
}
