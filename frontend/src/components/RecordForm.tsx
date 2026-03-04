import type { FormEvent, ReactNode } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Textarea } from '@/components/ui/textarea'

export type FieldType = 'text' | 'email' | 'tel' | 'url' | 'number' | 'date' | 'select' | 'textarea'

export interface FormFieldDef {
  key: string
  label: string
  type?: FieldType
  required?: boolean
  placeholder?: string
  options?: { value: string; label: string }[]
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
    <form onSubmit={(e) => void onSubmit(e)} className="space-y-4">
      {fields.map((field) => (
        <div key={field.key} className="space-y-1.5">
          <Label htmlFor={field.key}>
            {field.label}
            {field.required && <span className="ml-1 text-destructive">*</span>}
          </Label>
          {field.type === 'select' ? (
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
