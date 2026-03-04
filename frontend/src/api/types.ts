/**
 * TypeScript interfaces matching the backend Pydantic Read schemas.
 */

// ---------------------------------------------------------------------------
// Shared
// ---------------------------------------------------------------------------

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  offset: number
  limit: number
}

export interface StandardFields {
  id: number
  owner_id: number | null
  created_by_id: number | null
  updated_by_id: number | null
  created_at: string
  updated_at: string
  sfid: string | null
  custom_fields: Record<string, unknown>
}

// ---------------------------------------------------------------------------
// Account
// ---------------------------------------------------------------------------

export interface Account extends StandardFields {
  name: string
  type: string | null
  industry: string | null
  phone: string | null
  website: string | null
  description: string | null
  billing_street: string | null
  billing_city: string | null
  billing_state: string | null
  billing_postal_code: string | null
  billing_country: string | null
  annual_revenue: number | null
  number_of_employees: number | null
}

export interface AccountCreate {
  name: string
  type?: string | null
  industry?: string | null
  phone?: string | null
  website?: string | null
  description?: string | null
  billing_street?: string | null
  billing_city?: string | null
  billing_state?: string | null
  billing_postal_code?: string | null
  billing_country?: string | null
  annual_revenue?: number | null
  number_of_employees?: number | null
  custom_fields?: Record<string, unknown>
}

export type AccountUpdate = Partial<AccountCreate>

// ---------------------------------------------------------------------------
// Contact
// ---------------------------------------------------------------------------

export interface Contact extends StandardFields {
  first_name: string | null
  last_name: string
  email: string | null
  phone: string | null
  mobile_phone: string | null
  title: string | null
  department: string | null
  account_id: number | null
  lead_source: string | null
  description: string | null
  mailing_city: string | null
  mailing_country: string | null
}

export interface ContactCreate {
  last_name: string
  first_name?: string | null
  email?: string | null
  phone?: string | null
  mobile_phone?: string | null
  title?: string | null
  department?: string | null
  account_id?: number | null
  lead_source?: string | null
  description?: string | null
  mailing_city?: string | null
  mailing_country?: string | null
  custom_fields?: Record<string, unknown>
}

export type ContactUpdate = Partial<ContactCreate>

// ---------------------------------------------------------------------------
// Lead
// ---------------------------------------------------------------------------

export interface Lead extends StandardFields {
  first_name: string | null
  last_name: string
  company: string | null
  email: string | null
  phone: string | null
  status: string
  lead_source: string | null
  title: string | null
  industry: string | null
  converted_at: string | null
  converted_account_id: number | null
  converted_contact_id: number | null
}

export interface LeadCreate {
  last_name: string
  company: string
  first_name?: string | null
  email?: string | null
  phone?: string | null
  status?: string
  lead_source?: string | null
  title?: string | null
  industry?: string | null
  custom_fields?: Record<string, unknown>
}

export type LeadUpdate = Partial<LeadCreate>

// ---------------------------------------------------------------------------
// Opportunity
// ---------------------------------------------------------------------------

export interface Opportunity extends StandardFields {
  name: string
  account_id: number | null
  contact_id: number | null
  stage: string
  probability: number | null
  amount: number | null
  close_date: string
  type: string | null
  lead_source: string | null
  next_step: string | null
  description: string | null
  is_won: boolean
  is_closed: boolean
  closed_at: string | null
}

export interface OpportunityCreate {
  name: string
  close_date: string
  stage?: string
  account_id?: number | null
  contact_id?: number | null
  probability?: number | null
  amount?: number | null
  type?: string | null
  lead_source?: string | null
  next_step?: string | null
  description?: string | null
  custom_fields?: Record<string, unknown>
}

export type OpportunityUpdate = Partial<OpportunityCreate>

export interface PipelineStage {
  stage: string
  count: number
  total_amount: number | null
}

// ---------------------------------------------------------------------------
// Case
// ---------------------------------------------------------------------------

export interface Case extends StandardFields {
  case_number: string | null
  account_id: number | null
  contact_id: number | null
  subject: string
  description: string | null
  status: string
  priority: string
  origin: string | null
  type: string | null
  reason: string | null
  closed_at: string | null
}

export interface CaseCreate {
  subject: string
  account_id?: number | null
  contact_id?: number | null
  description?: string | null
  status?: string
  priority?: string
  origin?: string | null
  type?: string | null
  reason?: string | null
  custom_fields?: Record<string, unknown>
}

export type CaseUpdate = Partial<CaseCreate>
