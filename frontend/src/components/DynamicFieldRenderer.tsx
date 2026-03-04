/**
 * DynamicFieldRenderer renders a single form input based on the field type
 * defined in a CustomFieldDefinition. Used by DynamicFieldsSection to compose
 * the full set of custom fields for an entity or custom object record.
 */
import type { CustomFieldDefinition } from '@/api/types'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Switch } from '@/components/ui/switch'
import { Textarea } from '@/components/ui/textarea'

interface DynamicFieldRendererProps {
  definition: CustomFieldDefinition
  value: unknown
  onChange: (fieldName: string, value: unknown) => void
  disabled?: boolean
}

export default function DynamicFieldRenderer({
  definition,
  value,
  onChange,
  disabled = false,
}: DynamicFieldRendererProps) {
  const { field_name, field_label, field_type, is_required, picklist_values } = definition
  const label = field_label ?? field_name
  const inputId = `custom_field_${field_name}`

  const handleChange = (v: unknown) => onChange(field_name, v)

  const renderInput = () => {
    switch (field_type) {
      case 'text':
      case 'email':
      case 'phone':
        return (
          <Input
            id={inputId}
            type={field_type === 'email' ? 'email' : 'text'}
            value={typeof value === 'string' ? value : ''}
            onChange={(e) => handleChange(e.target.value)}
            disabled={disabled}
            required={is_required}
          />
        )

      case 'url':
        return (
          <Input
            id={inputId}
            type="url"
            value={typeof value === 'string' ? value : ''}
            onChange={(e) => handleChange(e.target.value)}
            disabled={disabled}
            required={is_required}
            placeholder="https://"
          />
        )

      case 'number':
      case 'currency':
      case 'percent':
        return (
          <Input
            id={inputId}
            type="number"
            value={typeof value === 'number' ? value : ''}
            onChange={(e) => handleChange(e.target.value === '' ? null : Number(e.target.value))}
            disabled={disabled}
            required={is_required}
          />
        )

      case 'textarea':
        return (
          <Textarea
            id={inputId}
            value={typeof value === 'string' ? value : ''}
            onChange={(e) => handleChange(e.target.value)}
            disabled={disabled}
            required={is_required}
            rows={3}
          />
        )

      case 'date':
        return (
          <Input
            id={inputId}
            type="date"
            value={typeof value === 'string' ? value : ''}
            onChange={(e) => handleChange(e.target.value)}
            disabled={disabled}
            required={is_required}
          />
        )

      case 'datetime':
        return (
          <Input
            id={inputId}
            type="datetime-local"
            value={typeof value === 'string' ? value.slice(0, 16) : ''}
            onChange={(e) => handleChange(e.target.value)}
            disabled={disabled}
            required={is_required}
          />
        )

      case 'boolean':
        return (
          <div className="flex items-center gap-3 pt-1">
            <Switch
              id={inputId}
              checked={value === true}
              onCheckedChange={(checked) => handleChange(checked)}
              disabled={disabled}
            />
            <label htmlFor={inputId} className="text-sm text-muted-foreground cursor-pointer">
              {label}
            </label>
          </div>
        )

      case 'picklist':
        return (
          <Select
            value={typeof value === 'string' ? value : ''}
            onValueChange={(v) => handleChange(v)}
            disabled={disabled}
          >
            <SelectTrigger id={inputId}>
              <SelectValue placeholder="Select…" />
            </SelectTrigger>
            <SelectContent>
              {!is_required && <SelectItem value="">—</SelectItem>}
              {(picklist_values ?? []).map((opt) => (
                <SelectItem key={opt} value={opt}>
                  {opt}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        )

      default:
        return (
          <Input
            id={inputId}
            value={typeof value === 'string' ? value : ''}
            onChange={(e) => handleChange(e.target.value)}
            disabled={disabled}
          />
        )
    }
  }

  // For booleans, the label is rendered inline with the checkbox
  if (field_type === 'boolean') {
    return <div className="space-y-1">{renderInput()}</div>
  }

  return (
    <div className="space-y-1.5">
      <Label htmlFor={inputId}>
        {label}
        {is_required && <span className="text-destructive ml-0.5">*</span>}
      </Label>
      {renderInput()}
    </div>
  )
}
