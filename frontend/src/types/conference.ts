import type { UserPublic } from './user'
import type { MultilingualField, ArticleLanguage } from './article'

export type ConferencePaperStatus = 'draft' | 'submitted' | 'accepted' | 'rejected' | 'published'

export interface Conference {
  id: string
  title: MultilingualField
  description?: MultilingualField
  location?: string
  start_date?: string
  end_date?: string
  year: number
  cover_image_url?: string
  is_active: boolean
  organizer?: string
  website_url?: string
  created_at: string
  updated_at: string
  sessions: ConferenceSession[]
  paper_count: number
}

export interface ConferenceSession {
  id: string
  conference_id: string
  title: MultilingualField
  description?: MultilingualField
  order: number
  date?: string
  created_at: string
  paper_count: number
}

export interface ConferencePaperAuthor {
  id: string
  user_id?: string
  guest_name?: string
  guest_email?: string
  guest_affiliation?: string
  guest_orcid?: string
  order: number
  is_corresponding: boolean
  user?: UserPublic
}

export interface ConferencePaper {
  id: string
  title: MultilingualField
  abstract: MultilingualField
  keywords: string[]
  language: ArticleLanguage
  conference_id: string
  session_id?: string
  author_id: string
  doi?: string
  pdf_file_path?: string
  pdf_file_size?: number
  cover_image_url?: string
  status: ConferencePaperStatus
  published_date?: string
  download_count: number
  view_count: number
  references?: string[]
  funding?: string
  created_at: string
  updated_at: string
  author?: UserPublic
  co_authors: ConferencePaperAuthor[]
}
