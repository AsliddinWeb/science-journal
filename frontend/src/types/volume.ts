export interface Issue {
  id: string
  volume_id: string
  number: number
  published_date?: string
  cover_image_url?: string
  description?: string
  created_at: string
  article_count: number
}

export interface Volume {
  id: string
  number: number
  year: number
  is_current: boolean
  description?: string
  cover_image_url?: string
  created_at: string
  issues: Issue[]
}
