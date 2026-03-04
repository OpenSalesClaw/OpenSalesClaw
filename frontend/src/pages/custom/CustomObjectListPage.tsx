import { useCallback, useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { customObjectsApi } from '@/api/customObjects'
import type { CustomObject, CustomObjectRecord } from '@/api/types'
import DataTable, { type Column } from '@/components/DataTable'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'

const PAGE_SIZE = 20

export default function CustomObjectListPage() {
  const { apiName } = useParams<{ apiName: string }>()
  const navigate = useNavigate()

  const [object, setObject] = useState<CustomObject | null>(null)
  const [records, setRecords] = useState<CustomObjectRecord[]>([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [loading, setLoading] = useState(false)
  const [nameFilter, setNameFilter] = useState('')
  const [nameInput, setNameInput] = useState('')

  useEffect(() => {
    customObjectsApi.get(apiName!).then(setObject).catch(() => navigate('/'))
  }, [apiName, navigate])

  const load = useCallback(
    async (p: number, name: string) => {
      setLoading(true)
      try {
        const data = await customObjectsApi.listRecords(apiName!, {
          offset: (p - 1) * PAGE_SIZE,
          limit: PAGE_SIZE,
          name: name || undefined,
        })
        setRecords(data.items)
        setTotal(data.total)
      } finally {
        setLoading(false)
      }
    },
    [apiName],
  )

  useEffect(() => {
    void load(page, nameFilter)
  }, [load, page, nameFilter])

  const columns: Column<CustomObjectRecord>[] = [
    {
      key: 'name',
      label: 'Name',
      render: (r) => r.name ?? <span className="text-muted-foreground italic">Untitled</span>,
    },
    {
      key: 'created_at',
      label: 'Created',
      render: (r) => new Date(r.created_at).toLocaleDateString(),
    },
    {
      key: 'updated_at',
      label: 'Updated',
      render: (r) => new Date(r.updated_at).toLocaleDateString(),
    },
  ]

  if (!object) return <div className="text-sm text-muted-foreground">Loading…</div>

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">{object.plural_label}</h1>
          <p className="text-sm text-muted-foreground mt-0.5">{total} record{total !== 1 ? 's' : ''}</p>
        </div>
        <Button onClick={() => navigate(`/objects/${apiName}/new`)}>+ New {object.label}</Button>
      </div>

      <div className="flex gap-2">
        <Input
          placeholder={`Search by name…`}
          value={nameInput}
          onChange={(e) => setNameInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter') {
              setNameFilter(nameInput)
              setPage(1)
            }
          }}
          className="max-w-xs"
        />
        <Button
          variant="outline"
          onClick={() => {
            setNameFilter(nameInput)
            setPage(1)
          }}
        >
          Search
        </Button>
        {nameFilter && (
          <Button
            variant="ghost"
            onClick={() => {
              setNameFilter('')
              setNameInput('')
              setPage(1)
            }}
          >
            Clear
          </Button>
        )}
      </div>

      <DataTable
        columns={columns}
        data={records}
        loading={loading}
        total={total}
        page={page}
        pageSize={PAGE_SIZE}
        onPageChange={setPage}
        onRowClick={(r) => navigate(`/objects/${apiName}/${r.id}`)}
        emptyMessage={`No ${object.plural_label.toLowerCase()} found.`}
      />
    </div>
  )
}
