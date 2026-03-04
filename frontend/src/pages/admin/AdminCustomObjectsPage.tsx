import { useCallback, useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { customObjectsApi } from '@/api/customObjects'
import type { CustomObject } from '@/api/types'
import DataTable, { type Column } from '@/components/DataTable'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'

const COLUMNS: Column<CustomObject>[] = [
  { key: 'label', label: 'Label' },
  { key: 'api_name', label: 'API Name', render: (r) => <span className="font-mono text-xs">{r.api_name}</span> },
  { key: 'plural_label', label: 'Plural Label' },
  {
    key: 'is_active',
    label: 'Status',
    render: (r) =>
      r.is_active ? <Badge variant="secondary">Active</Badge> : <Badge variant="outline">Inactive</Badge>,
  },
]

export default function AdminCustomObjectsPage() {
  const navigate = useNavigate()
  const [items, setItems] = useState<CustomObject[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(false)

  const load = useCallback(async () => {
    setLoading(true)
    try {
      const data = await customObjectsApi.list({ limit: 200 })
      setItems(data.items)
      setTotal(data.total)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    void load()
  }, [load])

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Custom Objects</h1>
          <p className="text-sm text-muted-foreground mt-0.5">
            {total} object{total !== 1 ? 's' : ''} defined
          </p>
        </div>
        <Button onClick={() => navigate('/admin/custom-objects/new')}>+ New Object</Button>
      </div>

      <DataTable
        columns={COLUMNS}
        data={items}
        loading={loading}
        total={total}
        page={1}
        pageSize={200}
        onPageChange={() => undefined}
        onRowClick={(r) => navigate(`/admin/custom-objects/${r.api_name}`)}
        emptyMessage="No custom objects defined. Create one to get started."
      />
    </div>
  )
}
