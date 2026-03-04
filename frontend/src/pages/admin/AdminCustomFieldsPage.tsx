import { useCallback, useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { listCustomFieldDefinitions } from '@/api/customFieldDefinitions'
import type { CustomFieldDefinition } from '@/api/types'
import DataTable, { type Column } from '@/components/DataTable'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'

const STANDARD_OBJECTS = [
  { label: 'Accounts', value: 'accounts' },
  { label: 'Contacts', value: 'contacts' },
  { label: 'Leads', value: 'leads' },
  { label: 'Opportunities', value: 'opportunities' },
  { label: 'Cases', value: 'cases' },
]

const COLUMNS: Column<CustomFieldDefinition>[] = [
  { key: 'field_name', label: 'API Name' },
  { key: 'field_label', label: 'Label', render: (r) => r.field_label ?? '—' },
  {
    key: 'field_type',
    label: 'Type',
    render: (r) => <Badge variant="secondary">{r.field_type}</Badge>,
  },
  {
    key: 'is_required',
    label: 'Required',
    render: (r) =>
      r.is_required ? <Badge variant="destructive">Required</Badge> : <span className="text-muted-foreground">—</span>,
  },
  { key: 'field_order', label: 'Order', render: (r) => r.field_order ?? '—' },
]

function ObjectFieldsTab({ objectName }: { objectName: string }) {
  const navigate = useNavigate()
  const [items, setItems] = useState<CustomFieldDefinition[]>([])
  const [loading, setLoading] = useState(false)

  const load = useCallback(async () => {
    setLoading(true)
    try {
      const result = await listCustomFieldDefinitions({ object_name: objectName, limit: 200 })
      setItems(result.items)
    } finally {
      setLoading(false)
    }
  }, [objectName])

  useEffect(() => {
    void load()
  }, [load])

  return (
    <div className="space-y-4">
      <div className="flex justify-end">
        <Button size="sm" onClick={() => navigate(`/admin/custom-fields/new?object=${objectName}`)}>
          + New Field
        </Button>
      </div>
      <DataTable
        columns={COLUMNS}
        data={items}
        loading={loading}
        total={items.length}
        page={1}
        pageSize={200}
        onPageChange={() => undefined}
        onRowClick={(r) => navigate(`/admin/custom-fields/${r.id}`)}
        emptyMessage="No custom fields defined for this object."
      />
    </div>
  )
}

export default function AdminCustomFieldsPage() {
  const [activeTab, setActiveTab] = useState(STANDARD_OBJECTS[0].value)

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Custom Fields</h1>
        <p className="text-sm text-muted-foreground mt-0.5">
          Define custom fields on standard objects. Fields are stored as JSONB and validated at runtime.
        </p>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList>
          {STANDARD_OBJECTS.map((o) => (
            <TabsTrigger key={o.value} value={o.value}>
              {o.label}
            </TabsTrigger>
          ))}
        </TabsList>
        {STANDARD_OBJECTS.map((o) => (
          <TabsContent key={o.value} value={o.value} className="mt-4">
            <ObjectFieldsTab objectName={o.value} />
          </TabsContent>
        ))}
      </Tabs>
    </div>
  )
}
