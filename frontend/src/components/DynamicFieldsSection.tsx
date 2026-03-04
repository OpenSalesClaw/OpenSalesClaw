/**
 * DynamicFieldsSection fetches CustomFieldDefinitions for a given object and
 * renders all of them using DynamicFieldRenderer.
 *
 * Usage:
 *   <DynamicFieldsSection
 *     objectName="accounts"
 *     values={form.custom_fields}
 *     onChange={(updated) => setForm(f => ({ ...f, custom_fields: updated }))}
 *   />
 */
import { useEffect, useState } from 'react'
import { listCustomFieldDefinitions } from '@/api/customFieldDefinitions'
import type { CustomFieldDefinition } from '@/api/types'
import DynamicFieldRenderer from './DynamicFieldRenderer'
import { Separator } from './ui/separator'

interface DynamicFieldsSectionProps {
  /** The object name to load definitions for, e.g. "accounts", "custom_object_12" */
  objectName: string
  /** Current custom field values */
  values: Record<string, unknown>
  onChange: (updated: Record<string, unknown>) => void
  disabled?: boolean
  /** Whether to show the "Custom Fields" section heading */
  showHeading?: boolean
}

export default function DynamicFieldsSection({
  objectName,
  values,
  onChange,
  disabled = false,
  showHeading = true,
}: DynamicFieldsSectionProps) {
  const [definitions, setDefinitions] = useState<CustomFieldDefinition[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    setLoading(true)
    listCustomFieldDefinitions({ object_name: objectName, limit: 200 })
      .then((r) => {
        const sorted = [...r.items].sort((a, b) => {
          const oa = a.field_order ?? 9999
          const ob = b.field_order ?? 9999
          return oa !== ob ? oa - ob : a.id - b.id
        })
        setDefinitions(sorted)
      })
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [objectName])

  if (loading || definitions.length === 0) return null

  const handleFieldChange = (fieldName: string, value: unknown) => {
    onChange({ ...values, [fieldName]: value })
  }

  return (
    <div className="space-y-4">
      {showHeading && (
        <>
          <Separator />
          <h3 className="text-sm font-semibold text-muted-foreground uppercase tracking-wide">Custom Fields</h3>
        </>
      )}
      {definitions.map((def) => (
        <DynamicFieldRenderer
          key={def.id}
          definition={def}
          value={values[def.field_name] ?? def.default_value ?? null}
          onChange={handleFieldChange}
          disabled={disabled}
        />
      ))}
    </div>
  )
}
