import type { FormEvent, ReactNode } from 'react'
import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Textarea } from '@/components/ui/textarea'

export type FieldType = 'text' | 'email' | 'tel' | 'url' | 'number' | 'date' | 'select' | 'textarea' | 'combobox'

export interface FormFieldDef {
  key: string
  label: string
  type?: FieldType
  required?: boolean
  placeholder?: string
  options?: { value: string; label: string }[]
}

interface ComboboxFieldProps {
  field: FormFieldDef
  value: string
  onChange: (key: string, value: string) => void
}

function ComboboxField({ field, value, onChange }: ComboboxFieldProps) {
  const [open, setOpen] = useState(false)
  const [search, setSearch] = useState('')

  const selectedLabel = field.options?.find((o) => o.value === value)?.label ?? ''

  const filtered = (field.options ?? []).filter(
    (o) =>
      o.label.toLowerCase().includes(search.toLowerCase()) ||
      o.value.toLowerCase().includes(search.toLowerCase()),
  )

  return (
    <div className="relative">
      <Input
        value={open ? search : selectedLabel}
        placeholder={field.placeholder ?? `Search ${field.label.toLowerCase()}…`}
        onChange={(e) => {
          setSearch(e.target.value)
          setOpen(true)
        }}
        onFocus={() => {
          setSearch('')
          setOpen(true)
        }}
        onBlur={() => setTimeout(() => setOpen(false), 150)}
      />
      {open && (
        <div className="absolute z-50 mt-1 w-full rounded-md border bg-popover text-popover-foreground shadow-md max-h-48 overflow-auto">
          {filtered.length === 0 ? (
            <div className="px-3 py-2 text-sm text-muted-foreground">No results</div>
          ) : (
            filtered.map((opt) => (
              <div
                key={opt.value}
                className="px-3 py-2 text-sm cursor-pointer hover:bg-accent"
                onMouseDown={() => {
                  onChange(field.key, opt.value)
                  setOpen(false)
                  setSearch('')
                }}
              >
                {opt.label}
              </div>
            ))
          )}
        </div>
      )}
    </div>
  )
}

interface RecordFormProps {
  fields: FormFieldDef[]
  values: Record<string, string>
  onChange: (key: string, value: string) => void
  onSubmit: (e: FormEvent) => void | Promise<void>
  onCancel: () => void
  submitLabel?: string
  loading?: boolean
  error?: string | null
  children?: ReactNode
}

export default function RecordForm({
  fields,
  values,
  onChange,
  onSubmit,
  onCancel,
  submitLabel = 'Save',
  loading = false,
  error,
  children,
}: RecordFormProps) {
  return (
    <form onSubmit={(e) => { e.preventDefault(); void onSubmit(e) }} className="space-y-4">
      {fields.map((field) => (
        <div key={field.key} className="space-y-1.5">
          <Label htmlFor={field.key}>
            {field.label}
            {field.required && <span className="ml-1 text-destructive">*</span>}
          </Label>
          {field.type === 'combobox' ? (
            <ComboboxField field={field} value={values[field.key] ?? ''} onChange={onChange} />
          ) : field.type === 'select' ? (
            <Select
              value={values[field.key] ?? ''}
              onValueChange={(val) => onChange(field.key, val)}
            >
              <SelectTrigger id={field.key}>
                <SelectValue placeholder={field.placeholder ?? `Select ${field.label.toLowerCase()}`} />
              </SelectTrigger>
              <SelectContent>
                {field.options?.map((opt) => (
                  <SelectItem key={opt.value} value={opt.value}>
                    {opt.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          ) : field.type === 'textarea' ? (
            <Textarea
              id={field.key}
              required={field.required}
              placeholder={field.placeholder}
              value={values[field.key] ?? ''}
              onChange={(e) => onChange(field.key, e.target.value)}
              rows={3}
            />
          ) : (
            <Input
              id={field.key}
              type={field.type ?? 'text'}
              required={field.required}
              placeholder={field.placeholder}
              value={values[field.key] ?? ''}
              onChange={(e) => onChange(field.key, e.target.value)}
            />
          )}
        </div>
      ))}
      {children}
      {error && <p className="text-sm text-destructive">{error}</p>}
      <div className="flex justify-end gap-2 pt-2">
        <Button type="button" variant="outline" onClick={onCancel} disabled={loading}>
          Cancel
        </Button>
        <Button type="submit" disabled={loading}>
          {loading ? 'Saving…' : submitLabel}
        </Button>
      </div>
    </form>
  )
}
