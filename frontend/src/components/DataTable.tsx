import type { ReactNode } from 'react'
import { Button } from '@/components/ui/button'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'

export interface Column<T> {
  key: string
  label: string
  render?: (row: T) => ReactNode
}

interface DataTableProps<T extends { id: number }> {
  columns: Column<T>[]
  data: T[]
  loading?: boolean
  total: number
  page: number
  pageSize: number
  onPageChange: (page: number) => void
  onRowClick?: (row: T) => void
  emptyMessage?: string
}

export default function DataTable<T extends { id: number }>({
  columns,
  data,
  loading = false,
  total,
  page,
  pageSize,
  onPageChange,
  onRowClick,
  emptyMessage = 'No records found.',
}: DataTableProps<T>) {
  const totalPages = Math.max(1, Math.ceil(total / pageSize))

  return (
    <div className="space-y-4">
      <div className="rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              {columns.map((col) => (
                <TableHead key={col.key}>{col.label}</TableHead>
              ))}
            </TableRow>
          </TableHeader>
          <TableBody>
            {loading ? (
              <TableRow>
                <TableCell colSpan={columns.length} className="py-8 text-center text-muted-foreground">
                  Loading…
                </TableCell>
              </TableRow>
            ) : data.length === 0 ? (
              <TableRow>
                <TableCell colSpan={columns.length} className="py-8 text-center text-muted-foreground">
                  {emptyMessage}
                </TableCell>
              </TableRow>
            ) : (
              data.map((row) => (
                <TableRow
                  key={row.id}
                  className={onRowClick ? 'cursor-pointer hover:bg-muted/50' : undefined}
                  onClick={() => onRowClick?.(row)}
                >
                  {columns.map((col) => (
                    <TableCell key={col.key}>
                      {col.render
                        ? col.render(row)
                        : ((row as Record<string, unknown>)[col.key] as ReactNode) ?? '—'}
                    </TableCell>
                  ))}
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>

      {/* Pagination */}
      {total > pageSize && (
        <div className="flex items-center justify-between text-sm text-muted-foreground">
          <span>
            {Math.min((page - 1) * pageSize + 1, total)}–{Math.min(page * pageSize, total)} of {total}
          </span>
          <div className="flex gap-2">
            <Button variant="outline" size="sm" disabled={page <= 1} onClick={() => onPageChange(page - 1)}>
              Previous
            </Button>
            <span className="flex items-center px-2">
              {page} / {totalPages}
            </span>
            <Button
              variant="outline"
              size="sm"
              disabled={page >= totalPages}
              onClick={() => onPageChange(page + 1)}
            >
              Next
            </Button>
          </div>
        </div>
      )}
    </div>
  )
}
