import type { ReactNode } from 'react'

export interface FieldDefinition {
  key: string
  label: string
  format?: (value: unknown) => ReactNode
}

interface DetailViewProps<T extends Record<string, unknown>> {
  record: T
  fields: FieldDefinition[]
  children?: ReactNode
}

function formatValue(value: unknown): ReactNode {
  if (value === null || value === undefined || value === '') return <span className="text-muted-foreground">—</span>
  if (typeof value === 'boolean') return value ? 'Yes' : 'No'
  if (typeof value === 'string' && (value.endsWith('Z') || value.includes('T'))) {
    // Attempt to parse ISO datetime
    const d = new Date(value)
    if (!isNaN(d.getTime())) {
      return d.toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' })
    }
  }
  return String(value)
}

export default function DetailView<T extends Record<string, unknown>>({
  record,
  fields,
  children,
}: DetailViewProps<T>) {
  return (
    <div className="space-y-4">
      <dl className="grid grid-cols-1 gap-x-6 gap-y-3 sm:grid-cols-2">
        {fields.map((field) => {
          const value = record[field.key]
          return (
            <div key={field.key} className="flex flex-col gap-0.5">
              <dt className="text-xs font-medium uppercase tracking-wide text-muted-foreground">{field.label}</dt>
              <dd className="text-sm">{field.format ? field.format(value) : formatValue(value)}</dd>
            </div>
          )
        })}
      </dl>
      {children}
    </div>
  )
}
