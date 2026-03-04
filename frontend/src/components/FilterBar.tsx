import type { ReactNode } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'

export interface FilterConfig {
  key: string
  placeholder: string
  type: 'text' | 'select'
  options?: { value: string; label: string }[]
}

interface FilterBarProps {
  filters: FilterConfig[]
  values: Record<string, string>
  onChange: (key: string, value: string) => void
  onClear: () => void
  children?: ReactNode
}

export default function FilterBar({ filters, values, onChange, onClear, children }: FilterBarProps) {
  const hasActiveFilters = Object.values(values).some((v) => v !== '' && v !== undefined)

  return (
    <div className="flex flex-wrap items-center gap-2">
      {filters.map((filter) =>
        filter.type === 'select' ? (
          <Select
            key={filter.key}
            value={values[filter.key] ?? ''}
            onValueChange={(val) => onChange(filter.key, val === '_all' ? '' : val)}
          >
            <SelectTrigger className="h-9 w-40">
              <SelectValue placeholder={filter.placeholder} />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="_all">All</SelectItem>
              {filter.options?.map((opt) => (
                <SelectItem key={opt.value} value={opt.value}>
                  {opt.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        ) : (
          <Input
            key={filter.key}
            placeholder={filter.placeholder}
            value={values[filter.key] ?? ''}
            onChange={(e) => onChange(filter.key, e.target.value)}
            className="h-9 w-48"
          />
        ),
      )}
      {hasActiveFilters && (
        <Button variant="ghost" size="sm" onClick={onClear}>
          Clear filters
        </Button>
      )}
      {children}
    </div>
  )
}
