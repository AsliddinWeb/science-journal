import type { UserPublic } from './user'

export type ArticleStatus =
  | 'draft'
  | 'submitted'
  | 'under_review'
  | 'revision_required'
  | 'accepted'
  | 'rejected'
  | 'published'

export type ArticleLanguage = 'uz' | 'ru' | 'en'

export interface MultilingualField {
  uz?: string
  ru?: string
  en?: string
}

export interface ArticleAuthor {
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

export interface Article {
  id: string
  title: MultilingualField
  abstract: MultilingualField
  keywords: string[]
  doi?: string
  submission_date?: string
  published_date?: string
  status: ArticleStatus
  language: ArticleLanguage
  volume_id?: string
  issue_id?: string
  category_id?: string
  author_id: string
  pdf_file_path?: string
  pdf_file_size?: number
  cover_image_url?: string
  article_type?: string
  cover_letter?: string
  references?: string[]
  funding?: string
  conflict_of_interest?: string
  acknowledgments?: string
  download_count: number
  view_count: number
  created_at: string
  updated_at: string
  author?: UserPublic
  co_authors: ArticleAuthor[]
}

export interface ArticleListItem extends Omit<Article, 'reviews'> {}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  limit: number
  pages: number
}
