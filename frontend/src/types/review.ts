export type ReviewStatus = 'pending' | 'accepted' | 'completed' | 'declined'
export type ReviewRecommendation = 'accept' | 'minor_revision' | 'major_revision' | 'reject'

export interface Review {
  id: string
  article_id: string
  reviewer_id: string
  status: ReviewStatus
  recommendation?: ReviewRecommendation
  comments_to_author?: string
  submitted_at?: string
  deadline?: string
  created_at: string
  updated_at: string
}
