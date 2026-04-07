export type UserRole = 'superadmin' | 'editor' | 'reviewer' | 'author' | 'reader'

export interface User {
  id: string
  email: string
  full_name: string
  role: UserRole
  orcid_id?: string
  affiliation?: string
  country?: string
  avatar_url?: string
  is_active: boolean
  is_verified: boolean
  created_at: string
  updated_at: string
}

export interface UserPublic {
  id: string
  full_name: string
  affiliation?: string
  country?: string
  orcid_id?: string
  avatar_url?: string
  role: UserRole
}

export interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
}

export interface LoginCredentials {
  email: string
  password: string
}

export interface RegisterData {
  email: string
  password: string
  full_name: string
  affiliation?: string
  country?: string
  orcid_id?: string
}
